"""A deliberately simple, linear alternative to graph.py's LangGraph
orchestration — same node functions, called in plain sequential Python
instead of through a graph. Built after three consecutive live failures
against GPT-6 Luna (a schema rejection, a rate limit, a timeout, then a
single charge's exhausted-retries exception killing the whole batch)
traced back to one root cause: extract_all()/verify_all() run all 6
charges through a ThreadPoolExecutor, so a burst of parallel calls can
trip a rate limit, and pool.map() propagates the first exception and
abandons the other 5 charges' results.

This module processes one charge fully (extract -> validate-repair
loop -> verify-repair loop) before starting the next, in a plain `for`
loop — slower wall-clock, but no burst of parallel calls, and one
charge's catastrophic failure can no longer take down the others: it's
caught per-charge and recorded as PipelineStatus.SYSTEM_ERROR (declared
in schemas.py, never actually set anywhere until now) rather than
propagating.

graph.py is untouched — this is a second, independent entry point, not
a replacement. REPAIR_BUDGET/VERIFY_BUDGET are imported from it rather
than redefined, so the two don't silently drift apart on the one thing
they should agree on.
"""

from __future__ import annotations

import sys
import time
from typing import Any, Optional

from .assemble import assemble
from .extract import extract_charge
from .graph import REPAIR_BUDGET, VERIFY_BUDGET
from .identity import provisional_identity
from .map_node import map_document
from .pdf import split_pdf
from .report import build_report
from .run_log import append_trace, finish_run, run_log_path, start_run
from .structure_scan import scan_structure
from .schemas import (
    CanonicalCharge,
    ChargeExtraction,
    Disagreement,
    PipelineStatus,
    ReviewReport,
    SemanticOutcome,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    VerifierFinding,
    VerifierResult,
    VerifierSeverity,
    has_material_finding,
)
from .validate import validate_charge
from .verify import verify_charge


class ChargeOutcome:
    """Everything one charge produced, for the caller to fold into a
    ReviewReport — a plain data holder, not a schema (nothing here is
    sent to or received from a model)."""

    def __init__(self) -> None:
        self.extraction: Optional[ChargeExtraction] = None
        self.validation: Optional[ValidationResult] = None
        self.validation_history: list[ValidationResult] = []
        self.verify_result: Optional[VerifierResult] = None
        self.verify_rounds: int = 0
        self.repair_attempts: int = 0
        self.status: Optional[PipelineStatus] = None
        self.disagreement: Optional[Disagreement] = None


def _outcome_regression_issue(new_outcome: SemanticOutcome) -> ValidationIssue:
    """Confirmed live (KNOWN_ISSUES.md): a validate- or verify-repair call
    can reclassify a charge's outcome away from `mapped` instead of
    fixing its structure/content, since nothing previously constrained
    it to keep the outcome it already committed to — cost two correctly
    mapped charges their proposals in one run, over narrow concerns
    (missing surcharges) neither warranted abandoning `mapped` for. Fed
    back as a HARD validation issue so it flows through the same
    repair-budget/exhaustion machinery as any other structural
    failure — if the model can't restore `mapped` within budget, an
    honest EXTRACTION_FAILED beats silently accepting the downgrade."""
    return ValidationIssue(
        severity=ValidationSeverity.HARD,
        message=(
            f"This charge was already committed as mapped, but this repair round's outcome is {new_outcome.value!r} "
            "instead. A repair may only fix the structure/content of a proposal already mapped, never change "
            "outcome away from it. Restore outcome to 'mapped' and address the original concern within the "
            "proposal itself."
        ),
    )


def _build_disagreement(charge: CanonicalCharge, extraction: ChargeExtraction, verify_result: VerifierResult) -> Disagreement:
    material = [f for f in verify_result.findings if f.severity is VerifierSeverity.MATERIAL]
    return Disagreement(
        charge=charge,
        extractor_interpretation=(extraction.rebuttal if extraction.rebuttal else "(no rebuttal given — proposal unchanged after review)"),
        extractor_pages=extraction.provenance_pages,
        verifier_concern="; ".join(f.problem for f in material),
        verifier_pages=sorted({p for f in material for p in f.pages}),
    )


def process_charge(
    charge: CanonicalCharge,
    context: Any,
    page_texts: dict[int, str],
    llm: Any,
    *,
    pdf_path: str,
    verifier_llm: Any = None,
    repair_budget: int = REPAIR_BUDGET,
    verify_budget: int = VERIFY_BUDGET,
    log: Any = print,
    structure_notes: str = "",
) -> ChargeOutcome:
    """One charge, start to finish: extract, then alternate
    validate-repair and verify-repair (each re-extraction always goes
    back through Validate first — same invariant graph.py's node_extract
    enforces: §6.2, every Extract output passes through Validate before
    Verify or the report can see it) until either it's clean, its
    repair budget is exhausted (-> EXTRACTION_FAILED), or its verify
    budget is exhausted with a material finding still open (-> an
    unresolved Disagreement, never forced to agree). Once a charge has
    been mapped, a repair round is not allowed to reclassify it away
    from mapped (see `_outcome_regression_issue`) — a real bug found
    live, where a narrow verify concern led to abandoning a correct
    proposal instead of fixing it.

    A raw exception (a model response that fails structured-output
    parsing on every retry — found live, killed a 28-minute run outright
    when it happened inside a 6-charge batch) is caught here, not
    propagated: this charge alone becomes SYSTEM_ERROR, the other five
    charges this loop processes are never touched by it.
    """
    outcome = ChargeOutcome()
    verifier_llm = verifier_llm or llm

    try:
        extraction = extract_charge(charge, context, page_texts, llm, pdf_path=pdf_path, structure_notes=structure_notes)
        ever_mapped = extraction.outcome is SemanticOutcome.MAPPED
        repair_attempts = 0
        verify_rounds = 0
        verify_result = None
        verifier_findings: Optional[list[VerifierFinding]] = None
        repair_issues: Optional[list[ValidationIssue]] = None

        while True:
            if repair_issues is not None or verifier_findings is not None:
                extraction = extract_charge(
                    charge,
                    context,
                    page_texts,
                    llm,
                    pdf_path=pdf_path,
                    repair_issues=repair_issues,
                    verifier_findings=verifier_findings,
                    structure_notes=structure_notes,
                )
                repair_issues = None
                verifier_findings = None

            validation = validate_charge(extraction, page_texts)
            if ever_mapped and extraction.outcome is not SemanticOutcome.MAPPED:
                # Sticky, not a one-shot check: once a charge has been mapped even
                # once this run, every later round must stay mapped or be treated
                # as a HARD failure -- not just the round where it first flips.
                log(f"{charge.value}: repair round left outcome as {extraction.outcome.value!r} instead of mapped -- rejected")
                validation.issues.append(_outcome_regression_issue(extraction.outcome))
                validation.valid = False
            elif extraction.outcome is SemanticOutcome.MAPPED:
                ever_mapped = True
            outcome.validation_history.append(validation)
            log(f"{charge.value}: validate -> {'valid' if validation.valid else 'invalid'}")

            if not validation.valid:
                if repair_attempts >= repair_budget:
                    outcome.status = PipelineStatus.EXTRACTION_FAILED
                    break
                repair_attempts += 1
                repair_issues = [i for i in validation.issues if i.severity is ValidationSeverity.HARD]
                continue

            verify_result = verify_charge(charge, extraction, page_texts, verifier_llm)
            log(f"{charge.value}: verify -> {'material finding' if has_material_finding(verify_result) else 'clean'}")
            if not has_material_finding(verify_result):
                break
            if verify_rounds >= verify_budget:
                outcome.disagreement = _build_disagreement(charge, extraction, verify_result)
                break
            verify_rounds += 1
            verifier_findings = [f for f in verify_result.findings if f.severity is VerifierSeverity.MATERIAL]

        outcome.extraction = extraction
        outcome.validation = validation
        outcome.verify_result = verify_result
        outcome.verify_rounds = verify_rounds
        outcome.repair_attempts = repair_attempts
        return outcome

    except Exception as exc:  # noqa: BLE001 — deliberately broad: this charge's
        # failure must never take the other five down with it (§ this module's
        # own docstring — the exact bug this design replaces).
        log(f"{charge.value}: SYSTEM_ERROR — {type(exc).__name__}: {exc}")
        outcome.status = PipelineStatus.SYSTEM_ERROR
        return outcome


def run_pipeline(
    pdf_path: str,
    llm: Any,
    *,
    verifier_llm: Any = None,
    page_texts: Optional[dict[int, str]] = None,
    repair_budget: int = REPAIR_BUDGET,
    verify_budget: int = VERIFY_BUDGET,
    map_concurrency_limit: int = 1,
    thread_id: Optional[str] = None,
) -> ReviewReport:
    """Structure scan -> Split -> Identity -> Map -> Assemble, then one
    charge at a time,
    fully sequential — no ThreadPoolExecutor anywhere in this call path.
    `map_concurrency_limit` defaults to 1 (not map_document's own
    default) to keep Map's own internal batching out of this pipeline's
    otherwise-linear behaviour too; raise it if Map specifically is
    known not to be the problem for a given run.
    """
    started_at = time.time()
    log_path = run_log_path(thread_id=thread_id, run_started_at=started_at, llm=llm)
    start_run(log_path, pdf_path=pdf_path, llm=llm, thread_id=thread_id)

    def log(msg: str) -> None:
        print(f"[pipeline] {msg}", file=sys.stderr, flush=True)
        append_trace(log_path, msg)

    structure_notes = scan_structure(pdf_path, llm)
    log(f"structure_scan: {len(structure_notes)} chars")

    page_texts = page_texts or split_pdf(pdf_path)
    identity = provisional_identity(page_texts, llm, structure_notes=structure_notes)
    log(f"identity: authority={identity.authority!r} currency={identity.currency!r}")

    map_results = map_document(
        page_texts, llm, pdf_path=pdf_path, concurrency_limit=map_concurrency_limit, structure_notes=structure_notes
    )
    total_sections = sum(len(w.sections) for w in map_results)
    log(f"map: {len(map_results)} windows, {total_sections} sections found")

    assemble_result = assemble(map_results, identity, page_texts)
    log(f"assemble: {len(assemble_result.out_of_scope_sections)} out-of-scope sections, general_terms_found={assemble_result.general_terms_found}")

    extractions: dict[CanonicalCharge, ChargeExtraction] = {}
    validations: dict[CanonicalCharge, ValidationResult] = {}
    validation_history: dict[CanonicalCharge, list[ValidationResult]] = {}
    pipeline_statuses: dict[CanonicalCharge, PipelineStatus] = {}
    repair_counts: dict[CanonicalCharge, int] = {}
    verify_results: dict[CanonicalCharge, VerifierResult] = {}
    verify_rounds: dict[CanonicalCharge, int] = {}
    disagreements: list[Disagreement] = []

    for charge in CanonicalCharge:
        context = assemble_result.charge_contexts[charge]
        log(f"{charge.value}: starting, context pages={context.pages} sections={context.section_numbers}")
        result = process_charge(
            charge,
            context,
            page_texts,
            llm,
            pdf_path=pdf_path,
            verifier_llm=verifier_llm,
            repair_budget=repair_budget,
            verify_budget=verify_budget,
            log=log,
            structure_notes=structure_notes,
        )
        if result.extraction is not None:
            extractions[charge] = result.extraction
        if result.validation is not None:
            validations[charge] = result.validation
        validation_history[charge] = result.validation_history
        repair_counts[charge] = result.repair_attempts
        verify_rounds[charge] = result.verify_rounds
        if result.verify_result is not None:
            verify_results[charge] = result.verify_result
        if result.status is not None:
            pipeline_statuses[charge] = result.status
        if result.disagreement is not None:
            disagreements.append(result.disagreement)
        log(f"{charge.value}: done")

    total_pages = max(page_texts) if page_texts else 0
    report = build_report(
        identity,
        assemble_result,
        extractions,
        validations,
        pipeline_statuses,
        repair_counts,
        total_pages,
        verify_results=verify_results,
        verify_rounds=verify_rounds,
        disagreements=disagreements,
    )
    try:
        finish_run(log_path, report, started_at=started_at, validation_history=validation_history)
    except OSError:
        pass  # a log write failing must never fail the pipeline itself
    return report
