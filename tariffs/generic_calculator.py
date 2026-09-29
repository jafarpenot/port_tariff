"""A data-driven calculator: compute a fee straight from an extraction
pipeline's `ProposedRule` (basis/pricing_type/pricing_params/rounding/
multiplicity/min-max), instead of `tariffs/calculators.py`'s pattern of
one hand-written Python function per charge. v1, base rate only —
`ProposedRule.modifiers` are reported as skipped, never applied (see
`compute_charge`'s docstring).

`compute_base_amount` is the same dispatch `extraction/validate.py`'s
own smoke-test already did (pricing_type -> the matching tariffs.shapes
function) — pulled out here as a public, reusable function so Validate
and this module share one dispatch instead of two copies drifting apart.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from extraction.schemas import CanonicalCharge, ChargeReportEntry, ProposedRule, SemanticOutcome

from .calculators import _apply_maximum, _basis_value, _services_for
from .models import TariffResult, TraceStep, VesselCall
from .nlp import _TARIFF_PLAN
from .rules import Basis, PricingType, RoundingMode, RoundingSpec, TimeRounding, TimeSpec, round_time
from .shapes import Band, banded_base_plus_increment, base_plus_increment, base_plus_increment_times_duration, per_unit_rate

# CanonicalCharge's values match tariffs.schedule.TariffSchedule's field
# names (see that enum's own docstring) but not always calculators.py's
# function/TariffResult names -- towage/vts/pilotage each add a "_dues"
# suffix there. Kept here so a compiled TariffResult's `name` matches
# what the hand-written calculator would have called the same charge,
# for an easy side-by-side comparison.
_RESULT_NAME = {
    CanonicalCharge.LIGHT_DUES: "light_dues",
    CanonicalCharge.PORT_DUES: "port_dues",
    CanonicalCharge.TOWAGE: "towage_dues",
    CanonicalCharge.VTS: "vts_dues",
    CanonicalCharge.PILOTAGE: "pilotage_dues",
    CanonicalCharge.BERTHING_SERVICES: "berthing_services",
}


def compute_base_amount(
    rule: ProposedRule, basis_value: float, *, days: Optional[float] = None, key: Optional[str] = None
) -> float:
    """One service instance's raw amount for `rule`, dispatched on
    `rule.pricing_type` -- no `rule.maximum` cap and no multiplicity
    applied here, since both are the caller's responsibility. Validate's
    smoke test checks one raw instance directly; `compute_charge` below
    caps the *total* after multiplying by service count, not each
    instance before -- capping here would silently do the wrong thing
    for a multi-service charge.

    `key` selects a row for `keyed_rate` (a tug name, a vessel class) --
    required for that shape, ignored by every other shape.
    """
    rounding = RoundingSpec(mode=RoundingMode(rule.rounding_mode), unit=rule.rounding_unit)
    pt = rule.pricing_type

    if pt == PricingType.PER_UNIT.value:
        return per_unit_rate(basis_value, rule.pricing_params["rate"], rounding, rule.minimum)
    if pt == PricingType.BASE_PLUS_INCREMENT.value:
        return base_plus_increment(basis_value, rule.pricing_params["base"], rule.pricing_params["rate"], rounding)
    if pt == PricingType.BANDED.value:
        bands = [
            Band(
                min_gt_exclusive=b["min_exclusive"],
                max_gt_inclusive=b["max_inclusive"],
                base=b["base"],
                increment_above_gt=b["increment_above"],
                per_100t=b["per_unit_rate"],
            )
            for b in rule.pricing_params["bands"]
        ]
        return banded_base_plus_increment(basis_value, bands)
    if pt == PricingType.BASE_PLUS_INCREMENT_TIMES_DURATION.value:
        if days is None:
            raise ValueError("pricing_type 'base_plus_increment_times_duration' requires `days`")
        result = base_plus_increment_times_duration(
            basis_value, rule.pricing_params["basic_rate"], rule.pricing_params["daily_rate"], days, rounding
        )
        return result.total
    if pt == PricingType.KEYED_RATE.value:
        if key is None:
            raise ValueError("pricing_type 'keyed_rate' requires `key`")
        row = _match_category_key(key, rule.pricing_params["keys"])
        if row is None:
            raise ValueError(f"no keyed_rate row matches {key!r} (known: {[r['key'] for r in rule.pricing_params['keys']]})")
        if row["flat_amount"] is not None:
            return row["flat_amount"]
        return row["rate"] * basis_value
    raise ValueError(f"unknown pricing_type {pt!r}")


def compute_charge(
    rule: ProposedRule, call: VesselCall, *, name: str, currency: str = "ZAR", section: str = "(extracted)", page: int = 0
) -> TariffResult:
    """The real (non-smoke-test) computation: a real basis value off
    `call`, real multiplicity, real time-rounding, `rule.maximum` applied
    to the *total*. Every one of `rule.modifiers` is reported in
    `warnings`, never applied -- v1 is base rate only (see this module's
    docstring); a result is never silently presented as complete when a
    modifier was actually needed.
    """
    key = None
    if rule.pricing_type == PricingType.KEYED_RATE.value:
        if call.category_selection is None:
            raise ValueError(f"{name}: VesselCall.category_selection is required for this pricing_type.")
        key = call.category_selection

    basis_value = _basis_value(call, Basis(rule.basis))

    days = None
    if rule.pricing_type == PricingType.BASE_PLUS_INCREMENT_TIMES_DURATION.value:
        if call.chargeable_period_days is None:
            raise ValueError(f"{name}: VesselCall.chargeable_period_days is required for this pricing_type.")
        time_spec = TimeSpec(unit_hours=rule.time_unit_hours, rounding=rule.time_rounding) if rule.time_unit_hours and rule.time_rounding else None
        days = round_time(call.chargeable_period_days, time_spec)

    per_service_amount = compute_base_amount(rule, basis_value, days=days, key=key)
    services, service_note = _services_for(call, rule.multiplicity)
    amount = _apply_maximum(round(per_service_amount * services, 2), rule.maximum)

    warnings: list[str] = []
    if rule.modifiers:
        warnings.append(
            f"{len(rule.modifiers)} modifier(s) not applied (base rate only): "
            + "; ".join(m.condition for m in rule.modifiers)
        )
    assumptions = [service_note] if service_note else []

    trace = [
        TraceStep(
            tariff=name,
            section=section,
            page=page,
            description=f"compute_base_amount(pricing_type={rule.pricing_type!r}) x {services} service(s)",
            inputs={"basis_value": basis_value, "services": services},
            rounding=RoundingSpec(mode=RoundingMode(rule.rounding_mode), unit=rule.rounding_unit),
            subtotal=amount,
        )
    ]
    return TariffResult(name=name, amount=amount, currency=currency, trace=trace, warnings=warnings, assumptions=assumptions)


_NEGATION_WORDS = ("excluding", "except", "other than")


def _normalize_label(label: str) -> str:
    return " ".join(label.replace("/", " ").replace("_", " ").split()).lower()


def _match_label(value: str, candidates: list[str]) -> Optional[str]:
    """Shared matcher behind both `_match_port_key` (a dict of per-port
    rules) and `_match_category_key` (a list of keyed_rate rows) --
    same failure mode either way: a book sometimes combines entries
    ('Port Elizabeth / Ngqura'), renames a leftover bucket ('Other' vs.
    'Other Ports'), or names one as a negation of the entries that *do*
    have their own row ('all ports excluding Durban...' -- found live:
    contains the substring "durban", which a naive substring check
    matched instead of the real, exact 'Durban' entry next to it).

    Every candidate is checked for an *exact* match first, before a
    substring match is tried on any candidate -- an exact match must
    always win over an accidental substring hit. A negation-worded
    candidate is never substring-matched at all; it's only reachable
    via the single-catch-all fallback, same as 'Other'."""
    if value in candidates:
        return value

    normalized_target = _normalize_label(value)
    normalized = {c: _normalize_label(c) for c in candidates}

    for candidate, normalized_candidate in normalized.items():
        if normalized_target == normalized_candidate:
            return candidate

    for candidate, normalized_candidate in normalized.items():
        if any(word in normalized_candidate for word in _NEGATION_WORDS):
            continue
        if normalized_target in normalized_candidate:
            return candidate

    catch_all = [c for c, nc in normalized.items() if "other" in nc or any(word in nc for word in _NEGATION_WORDS)]
    if len(catch_all) == 1:
        return catch_all[0]
    return None


def _match_port_key(port_value: str, per_port_rules: dict[str, ProposedRule]) -> Optional[str]:
    """`VesselCall.port` values are the registry's own snake_case names
    ('richards_bay'); extracted `per_port_rules` keys are the book's own
    spelling ('Richards Bay'). See `_match_label` for the matching
    strategy shared with `_match_category_key`."""
    return _match_label(port_value, list(per_port_rules))


def _match_category_key(value: str, keys: list[dict]) -> Optional[dict]:
    """Same matching strategy as `_match_port_key`, generalised to any
    keyed_rate category (a tug name, a vessel class) instead of a port
    name specifically. Returns the matching row dict, or None."""
    matched = _match_label(value, [row["key"] for row in keys])
    if matched is None:
        return None
    return next(row for row in keys if row["key"] == matched)


def compile_charge(charge: CanonicalCharge, entry: ChargeReportEntry, *, currency: str = "ZAR") -> Callable[[VesselCall, Any], TariffResult]:
    """One closure per charge, matching `tariffs/calculators.py`'s exact
    calling convention -- `fn(call, schedule=None) -> TariffResult` --
    so `tariffs/nlp.py`'s registry can call a compiled charge exactly
    the way it calls a hand-written one. `schedule` is accepted only for
    interface compatibility and is never read: the closure already
    carries its own extracted rule, captured when it was built."""
    name = _RESULT_NAME.get(charge, charge.value)

    if entry.outcome is not SemanticOutcome.MAPPED:
        def _not_computable(call: VesselCall, schedule: Any = None) -> TariffResult:
            return TariffResult(name=name, amount=None, currency=currency, warnings=[f"not computable: outcome is {entry.outcome!r}, not mapped"])
        return _not_computable

    section = ", ".join(entry.provenance_sections) or "(extracted)"
    page = entry.provenance_pages[0] if entry.provenance_pages else 0

    if entry.varies_by_port:
        per_port_rules = entry.per_port_rules

        def _varies_by_port(call: VesselCall, schedule: Any = None) -> TariffResult:
            matched_key = _match_port_key(call.port.value, per_port_rules)
            if matched_key is None:
                return TariffResult(
                    name=name, amount=None, currency=currency,
                    warnings=[f"no extracted rule matches port {call.port.value!r} (known: {sorted(per_port_rules)})"],
                )
            return compute_charge(per_port_rules[matched_key], call, name=name, currency=currency, section=section, page=page)

        return _varies_by_port

    rule = entry.proposed_rule

    def _single_rule(call: VesselCall, schedule: Any = None) -> TariffResult:
        return compute_charge(rule, call, name=name, currency=currency, section=section, page=page)

    return _single_rule


def compile_report(charges: dict[CanonicalCharge, ChargeReportEntry], *, currency: str = "ZAR") -> dict[CanonicalCharge, Callable[[VesselCall, Any], TariffResult]]:
    """Every charge in `charges`, compiled -- including non-mapped ones,
    which compile to a closure that reports why rather than being
    omitted (so a caller iterating this dict never has to special-case
    a missing key)."""
    return {charge: compile_charge(charge, entry, currency=currency) for charge, entry in charges.items()}


def _no_modifiers(result: TariffResult, call: VesselCall, schedule: Any) -> TariffResult:
    """`tariffs/nlp.py`'s tariff-plan shape always applies a modifier
    function to a calculator's result; a compiled charge already
    reports its skipped modifiers in `TariffResult.warnings` (v1, base
    rate only -- see this module's docstring), so this slot is a
    pass-through, not `tariffs.modifiers`'s TNPA-specific surcharge
    rules, which don't apply to a different (or even the same,
    freshly re-extracted) rule set."""
    return result


def to_tariff_plan(compiled: dict[CanonicalCharge, Callable[[VesselCall, Any], TariffResult]]) -> dict[str, tuple]:
    """Adapts `compile_report()`'s output into the exact shape
    `tariffs/nlp.py`'s `_TARIFF_PLAN` uses -- `name -> (calc_fn, mod_fn,
    dependency_met, missing_field)` -- so `parse_vessel_request(...,
    tariff_plan=to_tariff_plan(compiled))` can call a compiled charge
    exactly the way it calls a hand-written `calculators.py` one.

    Reuses `_TARIFF_PLAN`'s own dependency checks (does this VesselCall
    state a service count, a chargeable period?) unchanged -- those are
    about what the vessel call itself says, not which authority's rates
    are being used, so there's nothing authority-specific to re-derive."""
    plan: dict[str, tuple] = {}
    for charge, fn in compiled.items():
        name = _RESULT_NAME.get(charge, charge.value)
        if name not in _TARIFF_PLAN:
            continue  # a charge tariffs/nlp.py doesn't (yet) plan for at all
        _, _, dependency_met, missing_field = _TARIFF_PLAN[name]
        plan[name] = (fn, _no_modifiers, dependency_met, missing_field)
    return plan
