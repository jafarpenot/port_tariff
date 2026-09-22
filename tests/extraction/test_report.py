from extraction.assemble import AssembleResult
from extraction.report import build_report
from extraction.schemas import (
    CanonicalCharge,
    ChargeExtraction,
    PipelineStatus,
    ProvisionalIdentity,
    SemanticOutcome,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)


def _empty_assemble_result(general_terms_found=True):
    return AssembleResult(sections=[], charge_contexts={}, identity=ProvisionalIdentity(), out_of_scope_sections=[], general_terms_found=general_terms_found)


def test_report_matches_existing_authority_as_new_edition():
    identity = ProvisionalIdentity(authority="Transnet National Ports Authority")
    report = build_report(identity, _empty_assemble_result(), {}, {}, {}, {}, total_pages=27)
    assert report.is_new_edition is True
    assert report.matched_existing_authority == "Transnet National Ports Authority"


def test_report_unrecognised_authority_is_a_new_schedule():
    identity = ProvisionalIdentity(authority="Acme Port Authority")
    report = build_report(identity, _empty_assemble_result(), {}, {}, {}, {}, total_pages=10)
    assert report.is_new_edition is False
    assert report.matched_existing_authority is None


def test_report_includes_every_canonical_charge_even_if_never_extracted():
    report = build_report(ProvisionalIdentity(), _empty_assemble_result(), {}, {}, {}, {}, total_pages=1)
    charges_in_report = {entry.charge for entry in report.charges}
    assert charges_in_report == set(CanonicalCharge)


def test_report_carries_warnings_and_repair_attempts():
    extractions = {CanonicalCharge.VTS: ChargeExtraction(charge=CanonicalCharge.VTS, outcome=SemanticOutcome.NOT_PRESENT)}
    validations = {
        CanonicalCharge.VTS: ValidationResult(
            charge=CanonicalCharge.VTS, valid=True, issues=[ValidationIssue(severity=ValidationSeverity.WARNING, message="a warning")]
        )
    }
    report = build_report(ProvisionalIdentity(), _empty_assemble_result(), extractions, validations, {}, {CanonicalCharge.VTS: 2}, total_pages=5)
    vts_entry = next(e for e in report.charges if e.charge is CanonicalCharge.VTS)
    assert vts_entry.warnings == ["a warning"]
    assert vts_entry.repair_attempts == 2


def test_report_missing_general_terms_is_recorded_as_an_assumption():
    report = build_report(ProvisionalIdentity(), _empty_assemble_result(general_terms_found=False), {}, {}, {}, {}, total_pages=1)
    assert report.general_terms_found is False
    assert any("general terms" in a.lower() for a in report.assumptions)


def test_extraction_failed_status_is_carried_without_a_proposed_rule():
    statuses = {CanonicalCharge.TOWAGE: PipelineStatus.EXTRACTION_FAILED}
    report = build_report(ProvisionalIdentity(), _empty_assemble_result(), {}, {}, statuses, {CanonicalCharge.TOWAGE: 3}, total_pages=1)
    towage_entry = next(e for e in report.charges if e.charge is CanonicalCharge.TOWAGE)
    assert towage_entry.status is PipelineStatus.EXTRACTION_FAILED
    assert towage_entry.repair_attempts == 3
