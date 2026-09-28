"""Node 6 — Validate (§6.1, §6.4, §6.5). Python, deterministic.

Reuses tariffs' own vocabulary (tariffs.rules) and shapes (tariffs.shapes)
directly for the smoke calculation, rather than re-implementing a second
copy of what "valid" means — the whole point of Stage 1's closed rule
vocabulary is that the calculator and this validator speak the same
schema. Only MAPPED extractions are validated; bundled/not_present/
unmapped charges carry no rule to check.

The smoke calculation's pricing-type dispatch itself lives in
`tariffs.generic_calculator.compute_base_amount` — shared with that
module's *real* (non-synthetic) computation, so there is one dispatch
to keep correct, not two independently drifting copies.
"""

from __future__ import annotations

from tariffs.generic_calculator import compute_base_amount
from tariffs.rules import PricingType, RoundingMode

from .schemas import ChargeExtraction, ProposedRule, SemanticOutcome, ValidationIssue, ValidationResult, ValidationSeverity

# Synthetic vessels for the smoke calculation (§6.4) — small, medium, large.
_SMOKE_TEST_UNITS = [10.0, 5_000.0, 120_000.0]


def _hard(message: str, allowed_options: list[str] | None = None) -> ValidationIssue:
    return ValidationIssue(severity=ValidationSeverity.HARD, message=message, allowed_options=allowed_options)


def _warn(message: str) -> ValidationIssue:
    return ValidationIssue(severity=ValidationSeverity.WARNING, message=message)


def outcome_regression_issue(new_outcome: SemanticOutcome) -> ValidationIssue:
    """Confirmed live (KNOWN_ISSUES.md): a validate- or verify-repair call
    can reclassify a charge's outcome away from `mapped` instead of
    fixing its structure/content, since nothing previously constrained
    it to keep the outcome it already committed to — cost two correctly
    mapped charges their proposals in one run, over narrow concerns
    (missing surcharges) neither warranted abandoning `mapped` for. Fed
    back as a HARD validation issue so it flows through the same
    repair-budget/exhaustion machinery as any other structural
    failure — if the model can't restore `mapped` within budget, an
    honest EXTRACTION_FAILED beats silently accepting the downgrade.

    Shared by pipeline.py and graph.py — the two entry points apply the
    same sticky "once mapped, stay mapped" rule, just wired through
    different control flow (a plain loop vs. graph state checkpointed
    across node invocations)."""
    return ValidationIssue(
        severity=ValidationSeverity.HARD,
        message=(
            f"This charge was already committed as mapped, but this repair round's outcome is {new_outcome.value!r} "
            "instead. A repair may only fix the structure/content of a proposal already mapped, never change "
            "outcome away from it. Restore outcome to 'mapped' and address the original concern within the "
            "proposal itself."
        ),
    )


def _validate_enums(rule: ProposedRule) -> list[ValidationIssue]:
    """`basis`/`rounding_mode`/`multiplicity`/`time_rounding` are real
    enums on ProposedRule (extraction/schemas.py) — an invalid value is
    now structurally impossible to construct, same as `pricing_type`
    below. Only the one cross-field rule pydantic can't express
    declaratively (CEIL_TO_UNIT needs a unit) is still checked here."""
    if rule.rounding_mode is RoundingMode.CEIL_TO_UNIT and not rule.rounding_unit:
        return [_hard("rounding_mode 'ceil_to_unit' requires a positive rounding_unit.")]
    return []


def _validate_band_structure(bands: list[dict]) -> list[ValidationIssue]:
    """Ordered, contiguous under the exclusive/inclusive interval
    convention (SPEC.md §5.4); final band open-ended or explicit null.
    Every band is guaranteed to have all five keys present by
    `PricingBand` (extraction/schemas.py) — only ordering/contiguity,
    which Pydantic can't express declaratively, is checked here."""
    issues: list[ValidationIssue] = []
    if bands[0]["min_exclusive"] != 0:
        issues.append(_hard(f"band[0].min_exclusive must be 0, got {bands[0]['min_exclusive']!r}."))
    for i in range(1, len(bands)):
        if bands[i]["min_exclusive"] != bands[i - 1]["max_inclusive"]:
            issues.append(
                _hard(f"band[{i}].min_exclusive ({bands[i]['min_exclusive']!r}) must equal band[{i - 1}].max_inclusive ({bands[i - 1]['max_inclusive']!r}).")
            )
    if bands[-1]["max_inclusive"] is not None:
        issues.append(_hard("the final band's max_inclusive must be null (open-ended)."))
    return issues


def _validate_pricing(rule: ProposedRule) -> list[ValidationIssue]:
    """Required-keys-per-shape is enforced structurally now, by
    `PricingShapes`'s own model validator (extraction/schemas.py) — a
    `ChargeExtraction` with a malformed pricing shape can't be
    constructed at all, so it never reaches here. Only band
    ordering/contiguity is left to check."""
    if rule.pricing.banded.selected:
        return _validate_band_structure(rule.pricing_params["bands"])
    return []


def _validate_citations(extraction: ChargeExtraction, page_texts: dict[int, str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    max_page = max(page_texts) if page_texts else 0
    for page in extraction.provenance_pages:
        if page < 1 or page > max_page:
            issues.append(_hard(f"cited page {page} does not exist in this document (1..{max_page})."))
    return issues


def _smoke_calculate(rule: ProposedRule) -> list[ValidationIssue]:
    """The engine computes this rule for a few synthetic vessels without
    error, non-negative (§6.4) — via `compute_base_amount`'s dispatch,
    the same one the real (non-smoke) computation uses."""
    issues: list[ValidationIssue] = []
    known_pricing_types = {pt.value for pt in PricingType}
    if rule.pricing_type not in known_pricing_types:
        return issues  # unknown pricing_type already flagged elsewhere

    try:
        for units in _SMOKE_TEST_UNITS:
            days = 1.0 if rule.pricing_type == PricingType.BASE_PLUS_INCREMENT_TIMES_DURATION.value else None
            amount = compute_base_amount(rule, units, days=days)
            if rule.maximum is not None:
                amount = min(amount, rule.maximum)
            if amount < 0:
                issues.append(_hard(f"smoke calculation produced a negative amount ({amount}) at basis value {units}."))
    except Exception as exc:  # the smoke test's whole job is to catch exactly this
        issues.append(_hard(f"smoke calculation raised {type(exc).__name__}: {exc}"))
    return issues


def _validate_numeric_citations(rule: ProposedRule, extraction: ChargeExtraction, page_texts: dict[int, str]) -> list[ValidationIssue]:
    """Warning only (§6.4) — PDF text extraction formatting (spacing,
    thousands separators) varies too much for a missing verbatim match
    to be a hard gate."""
    cited_text = "\n".join(page_texts.get(p, "") for p in extraction.provenance_pages)
    if not cited_text:
        return []
    issues: list[ValidationIssue] = []
    numeric_values = [v for v in rule.pricing_params.values() if isinstance(v, (int, float))]
    numeric_values += [v for m in rule.modifiers for v in (m.adjustment_percentage, m.adjustment_flat_amount) if v is not None]
    for value in numeric_values:
        if str(value) not in cited_text and f"{value:,.2f}" not in cited_text:
            issues.append(_warn(f"value {value!r} not found verbatim on its cited page(s) — PDF formatting may differ from the raw number."))
    return issues


def _validate_one_rule(rule: ProposedRule, extraction: ChargeExtraction, page_texts: dict[int, str]) -> list[ValidationIssue]:
    issues = list(_validate_enums(rule))
    issues.extend(_validate_pricing(rule))
    if not any(i.severity is ValidationSeverity.HARD for i in issues):
        issues.extend(_smoke_calculate(rule))
        issues.extend(_validate_numeric_citations(rule, extraction, page_texts))
    return issues


def validate_charge(extraction: ChargeExtraction, page_texts: dict[int, str]) -> ValidationResult:
    issues = list(_validate_citations(extraction, page_texts))

    if extraction.outcome is SemanticOutcome.MAPPED:
        if extraction.varies_by_port:
            if not extraction.per_port_rules:
                issues.append(_hard("outcome is 'mapped' with varies_by_port=true but per_port_rules is empty."))
            for port, rule in extraction.per_port_rules.items():
                for issue in _validate_one_rule(rule, extraction, page_texts):
                    issue.message = f"[{port}] {issue.message}"
                    issues.append(issue)
        else:
            if extraction.proposed_rule is None:
                issues.append(_hard("outcome is 'mapped' with varies_by_port=false but no proposed_rule was given."))
            else:
                issues.extend(_validate_one_rule(extraction.proposed_rule, extraction, page_texts))
    elif extraction.outcome is SemanticOutcome.BUNDLED and extraction.included_in is None:
        issues.append(_hard("outcome is 'bundled' but included_in was not set."))
    elif extraction.outcome is SemanticOutcome.UNMAPPED and not extraction.unmapped_source_text:
        issues.append(_hard("outcome is 'unmapped' but no source text was quoted."))

    valid = not any(i.severity is ValidationSeverity.HARD for i in issues)
    return ValidationResult(charge=extraction.charge, valid=valid, issues=issues)


def validate_all(
    extractions: dict, page_texts: dict[int, str]
) -> dict:
    return {charge: validate_charge(extraction, page_texts) for charge, extraction in extractions.items()}
