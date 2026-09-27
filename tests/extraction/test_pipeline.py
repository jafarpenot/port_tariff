"""extraction/pipeline.py — the linear, sequential alternative to
graph.py. No real API calls (StubChatModel, same as test_graph.py).

The one test that matters most here is
test_run_pipeline_one_charge_exception_does_not_affect_the_others —
that's the actual bug (a single charge's exhausted-retries exception
killing the whole batch through extract_all()'s ThreadPoolExecutor)
this module exists to fix. Confirmed by deliberately making one charge
always raise and checking the other five still come back clean.
"""

from extraction.pipeline import process_charge, run_pipeline
from extraction.schemas import (
    CanonicalCharge,
    ChargeContext,
    ChargeExtraction,
    PerUnitShape,
    PipelineStatus,
    PricingShapes,
    ProposedRule,
    ProvisionalIdentity,
    SectionType,
    SemanticOutcome,
    StructureScanResult,
    VerifierFinding,
    VerifierResult,
    VerifierSeverity,
    WindowMapResult,
    WindowSection,
)

from .conftest import StubChatModel, make_blank_pdf, text_of

PAGE_TEXTS = {1: "Acme Port Authority Tariff Book. Currency: ZAR.", 2: "2.1 VTS dues. Rate 0.5 per GT, minimum 100."}
CONTEXT = ChargeContext(charge=CanonicalCharge.VTS, section_numbers=["2.1"], combined_text=PAGE_TEXTS[2])


def _rule(rate=0.5) -> ProposedRule:
    return ProposedRule(basis="gross_tonnage", rounding_mode="exact", pricing=PricingShapes(per_unit=PerUnitShape(selected=True, rate=rate)), multiplicity="per_call")


def _mapped(rate=0.5) -> ChargeExtraction:
    return ChargeExtraction(charge=CanonicalCharge.VTS, outcome=SemanticOutcome.MAPPED, proposed_rule=_rule(rate), provenance_pages=[2])


def test_process_charge_clean_first_pass_no_repairs_needed():
    def respond(schema, messages):
        if schema.__name__ == "ChargeExtraction":
            return _mapped()
        if schema.__name__ == "VerifierResult":
            return VerifierResult(charge=CanonicalCharge.VTS, findings=[])
        raise AssertionError(schema.__name__)

    llm = StubChatModel(respond)
    outcome = process_charge(CanonicalCharge.VTS, CONTEXT, PAGE_TEXTS, llm, pdf_path="unused", log=lambda msg: None)

    assert outcome.status is None
    assert outcome.repair_attempts == 0
    assert outcome.verify_rounds == 0
    assert outcome.disagreement is None
    assert outcome.validation.valid is True


def test_process_charge_validate_repair_succeeds():
    attempts = {"n": 0}

    def respond(schema, messages):
        if schema.__name__ == "ChargeExtraction":
            attempts["n"] += 1
            if attempts["n"] == 1:
                return ChargeExtraction(charge=CanonicalCharge.VTS, outcome=SemanticOutcome.MAPPED, proposed_rule=_rule(-5.0), provenance_pages=[2])
            return _mapped()
        if schema.__name__ == "VerifierResult":
            return VerifierResult(charge=CanonicalCharge.VTS, findings=[])
        raise AssertionError(schema.__name__)

    llm = StubChatModel(respond)
    outcome = process_charge(CanonicalCharge.VTS, CONTEXT, PAGE_TEXTS, llm, pdf_path="unused", log=lambda msg: None)

    assert outcome.repair_attempts == 1
    assert outcome.status is None
    assert outcome.validation.valid is True
    assert len(outcome.validation_history) == 2
    assert outcome.validation_history[0].valid is False


def test_process_charge_repair_budget_exhausted_is_extraction_failed():
    def respond(schema, messages):
        if schema.__name__ == "ChargeExtraction":
            return ChargeExtraction(charge=CanonicalCharge.VTS, outcome=SemanticOutcome.MAPPED, proposed_rule=_rule(-5.0), provenance_pages=[2])
        raise AssertionError(schema.__name__)

    llm = StubChatModel(respond)
    outcome = process_charge(CanonicalCharge.VTS, CONTEXT, PAGE_TEXTS, llm, pdf_path="unused", repair_budget=3, log=lambda msg: None)

    assert outcome.status is PipelineStatus.EXTRACTION_FAILED
    assert outcome.repair_attempts == 3
    assert outcome.verify_result is None  # never reaches Verify


def test_process_charge_verify_repair_succeeds():
    calls = {"n": 0}

    def respond(schema, messages):
        if schema.__name__ == "ChargeExtraction":
            calls["n"] += 1
            return _mapped(rate=999.0 if calls["n"] == 1 else 0.5)
        if schema.__name__ == "VerifierResult":
            if "999.0" in messages[-1].content:
                return VerifierResult(charge=CanonicalCharge.VTS, findings=[VerifierFinding(severity=VerifierSeverity.MATERIAL, problem="wrong rate", pages=[2])])
            return VerifierResult(charge=CanonicalCharge.VTS, findings=[])
        raise AssertionError(schema.__name__)

    llm = StubChatModel(respond)
    outcome = process_charge(CanonicalCharge.VTS, CONTEXT, PAGE_TEXTS, llm, pdf_path="unused", verify_budget=1, log=lambda msg: None)

    assert outcome.verify_rounds == 1
    assert outcome.disagreement is None
    assert not any(f.severity is VerifierSeverity.MATERIAL for f in outcome.verify_result.findings)


def test_process_charge_verify_budget_exhausted_records_disagreement():
    def respond(schema, messages):
        if schema.__name__ == "ChargeExtraction":
            return _mapped()
        if schema.__name__ == "VerifierResult":
            return VerifierResult(charge=CanonicalCharge.VTS, findings=[VerifierFinding(severity=VerifierSeverity.MATERIAL, problem="still wrong", pages=[2])])
        raise AssertionError(schema.__name__)

    llm = StubChatModel(respond)
    outcome = process_charge(CanonicalCharge.VTS, CONTEXT, PAGE_TEXTS, llm, pdf_path="unused", verify_budget=1, log=lambda msg: None)

    assert outcome.verify_rounds == 1
    assert outcome.disagreement is not None
    assert outcome.disagreement.charge is CanonicalCharge.VTS
    assert "still wrong" in outcome.disagreement.verifier_concern


def test_verify_repair_that_reclassifies_away_from_mapped_is_rejected_and_retried():
    """Regression test for a real bug found live (KNOWN_ISSUES.md): a
    verify-repair call abandoned a correct `mapped` proposal instead of
    fixing the narrow concern it was challenged on. The abandonment must
    be rejected as an ordinary structural failure (HARD validation
    issue, consumes the repair budget) and given one more chance to
    restore `mapped`, rather than accepted."""
    extract_attempts = {"n": 0}
    verify_attempts = {"n": 0}

    def respond(schema, messages):
        if schema.__name__ == "ChargeExtraction":
            extract_attempts["n"] += 1
            if extract_attempts["n"] == 2:
                return ChargeExtraction(charge=CanonicalCharge.VTS, outcome=SemanticOutcome.NOT_PRESENT)  # wrongly abandons mapped
            return _mapped()
        if schema.__name__ == "VerifierResult":
            verify_attempts["n"] += 1
            if verify_attempts["n"] == 1:
                return VerifierResult(charge=CanonicalCharge.VTS, findings=[VerifierFinding(severity=VerifierSeverity.MATERIAL, problem="missing surcharge", pages=[2])])
            return VerifierResult(charge=CanonicalCharge.VTS, findings=[])
        raise AssertionError(schema.__name__)

    llm = StubChatModel(respond)
    outcome = process_charge(CanonicalCharge.VTS, CONTEXT, PAGE_TEXTS, llm, pdf_path="unused", verify_budget=1, repair_budget=3, log=lambda msg: None)

    assert extract_attempts["n"] == 3  # 1st pass, wrongful reclassification, repair-of-the-regression
    assert outcome.status is None
    assert outcome.extraction.outcome is SemanticOutcome.MAPPED
    assert outcome.repair_attempts == 1
    assert outcome.disagreement is None
    assert any("already committed as mapped" in i.message for h in outcome.validation_history for i in h.issues)


def test_verify_repair_that_reclassifies_away_from_mapped_exhausts_repair_budget_honestly():
    """If the model never restores `mapped` within budget (the sticky
    guard fires on every round, not just the first flip), land on an
    honest EXTRACTION_FAILED rather than silently accepting the
    downgrade or wandering back into Verify with a wrong outcome."""
    extract_attempts = {"n": 0}

    def respond(schema, messages):
        if schema.__name__ == "ChargeExtraction":
            extract_attempts["n"] += 1
            if extract_attempts["n"] == 1:
                return _mapped()
            return ChargeExtraction(charge=CanonicalCharge.VTS, outcome=SemanticOutcome.NOT_PRESENT)  # never recovers
        if schema.__name__ == "VerifierResult":
            return VerifierResult(charge=CanonicalCharge.VTS, findings=[VerifierFinding(severity=VerifierSeverity.MATERIAL, problem="missing surcharge", pages=[2])])
        raise AssertionError(schema.__name__)

    llm = StubChatModel(respond)
    outcome = process_charge(CanonicalCharge.VTS, CONTEXT, PAGE_TEXTS, llm, pdf_path="unused", verify_budget=1, repair_budget=2, log=lambda msg: None)

    assert outcome.status is PipelineStatus.EXTRACTION_FAILED
    assert outcome.repair_attempts == 2
    assert outcome.disagreement is None  # never reaches Verify again to record a disagreement


def test_process_charge_exception_becomes_system_error_and_does_not_raise():
    def respond(schema, messages):
        raise RuntimeError("the model fundamentally failed")

    llm = StubChatModel(respond)
    outcome = process_charge(CanonicalCharge.VTS, CONTEXT, PAGE_TEXTS, llm, pdf_path="unused", log=lambda msg: None)

    assert outcome.status is PipelineStatus.SYSTEM_ERROR
    assert outcome.extraction is None


def test_run_pipeline_one_charge_exception_does_not_affect_the_others():
    """The actual regression test for the bug this module exists to
    fix: extract_all()'s ThreadPoolExecutor + pool.map() used to let one
    charge's exhausted-retries exception propagate and abandon the
    other five charges' results entirely (confirmed live: killed a real
    TNPA run 12 minutes in). Here, TOWAGE always raises; the other five
    charges must still come back with real, correct results."""

    def respond(schema, messages):
        name = schema.__name__
        if name == "StructureScanResult":
            return StructureScanResult(notes="No anomalies found.")
        if name == "ProvisionalIdentity":
            return ProvisionalIdentity(authority="Acme Port Authority", currency="ZAR")
        if name == "WindowMapResult":
            return WindowMapResult(
                window_start_page=1,
                window_end_page=2,
                sections=[WindowSection(section_number="2.1", heading="VTS dues", section_type=SectionType.CHARGE, page=2, affects_charges=[CanonicalCharge.VTS])],
            )
        if name == "ChargeExtraction":
            user_text = text_of(messages[-1].content)
            if "Canonical charge type to extract: towage" in user_text:
                raise RuntimeError("towage extraction fundamentally failed")
            charge = CanonicalCharge.VTS if "vts" in user_text else None
            return ChargeExtraction(charge=charge or CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.NOT_PRESENT)
        if name == "VerifierResult":
            return VerifierResult(charge=CanonicalCharge.VTS, findings=[])
        raise AssertionError(name)

    llm = StubChatModel(respond)
    report = run_pipeline(make_blank_pdf(), llm, page_texts=PAGE_TEXTS, thread_id=None)

    assert len(report.charges) == 6
    by_charge = {e.charge: e for e in report.charges}
    assert by_charge[CanonicalCharge.TOWAGE].status is PipelineStatus.SYSTEM_ERROR
    # every other charge reached a real, non-crashed outcome
    for charge in CanonicalCharge:
        if charge is CanonicalCharge.TOWAGE:
            continue
        assert by_charge[charge].status is None
        assert by_charge[charge].outcome is not None
