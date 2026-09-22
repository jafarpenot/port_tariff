"""Node 8 — review report (§6.1, §7). Assembles everything the earlier
nodes produced into one object a business reviewer can read without
opening the code. No LLM call; pure assembly.
"""

from __future__ import annotations

from tariffs.schedule import load_schedule

from .assemble import AssembleResult
from .schemas import (
    CanonicalCharge,
    ChargeExtraction,
    ChargeReportEntry,
    Disagreement,
    PipelineStatus,
    ProvisionalIdentity,
    ReviewReport,
    ValidationResult,
    ValidationSeverity,
    VerifierResult,
)


def _detect_new_edition(identity: ProvisionalIdentity) -> tuple[bool, str | None]:
    """Simplified for Stage 2 (specs/EXTRACTION_SPEC.md §11 leaves report
    format to judgment): a case-insensitive authority-name match against
    the currently loaded schedule. A real structured diff against the
    matched schedule is future work — this only decides new-edition vs
    new-schedule, it does not yet render the diff itself."""
    if not identity.authority:
        return False, None
    try:
        current = load_schedule()
    except Exception:
        return False, None
    current_authority = current.schedule_identity.authority
    if identity.authority.strip().lower() == current_authority.strip().lower():
        return True, current_authority
    return False, None


def build_report(
    identity: ProvisionalIdentity,
    assemble_result: AssembleResult,
    extractions: dict[CanonicalCharge, ChargeExtraction],
    validations: dict[CanonicalCharge, ValidationResult],
    pipeline_statuses: dict[CanonicalCharge, PipelineStatus],
    repair_counts: dict[CanonicalCharge, int],
    total_pages: int,
    verify_results: dict[CanonicalCharge, VerifierResult] | None = None,
    verify_rounds: dict[CanonicalCharge, int] | None = None,
    disagreements: list[Disagreement] | None = None,
) -> ReviewReport:
    is_new_edition, matched_authority = _detect_new_edition(identity)
    verify_results = verify_results or {}
    verify_rounds = verify_rounds or {}

    charges = []
    for charge in CanonicalCharge:
        extraction = extractions.get(charge)
        validation = validations.get(charge)
        status = pipeline_statuses.get(charge)
        warnings = [i.message for i in validation.issues if i.severity is ValidationSeverity.WARNING] if validation else []
        verify_result = verify_results.get(charge)
        charges.append(
            ChargeReportEntry(
                charge=charge,
                outcome=extraction.outcome if extraction else None,
                status=status,
                varies_by_port=extraction.varies_by_port if extraction else False,
                proposed_rule=extraction.proposed_rule if extraction else None,
                per_port_rules=extraction.per_port_rules if extraction else {},
                included_in=extraction.included_in if extraction else None,
                unmapped_source_text=extraction.unmapped_source_text if extraction else None,
                provenance_sections=extraction.provenance_sections if extraction else [],
                provenance_pages=extraction.provenance_pages if extraction else [],
                sections_considered=extraction.sections_considered if extraction else [],
                warnings=warnings,
                repair_attempts=repair_counts.get(charge, 0),
                verifier_findings=verify_result.findings if verify_result else [],
                verify_rounds=verify_rounds.get(charge, 0),
            )
        )

    assumptions = []
    if not assemble_result.general_terms_found:
        assumptions.append(
            "No general terms section was found anywhere in the document — assumptions about tonnage "
            "basis and currency could not be inherited from the book's own general conditions."
        )

    return ReviewReport(
        identity=identity,
        is_new_edition=is_new_edition,
        matched_existing_authority=matched_authority,
        charges=charges,
        out_of_scope_sections=[f"{s.section_number or '(no number)'}: {s.heading}" for s in assemble_result.out_of_scope_sections],
        coverage_pages_read=total_pages,
        coverage_total_pages=total_pages,
        general_terms_found=assemble_result.general_terms_found,
        assumptions=assumptions,
        disagreements=disagreements or [],
    )
