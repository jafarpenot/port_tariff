"""End-to-end pipeline test — no real Anthropic API calls, no PDF file:
page_texts is injected directly (extraction/graph.py's node_split skips
split_pdf when page_texts is already present in the initial state).
Exercises the full sequence: Validate's structural repair loop (§6.5),
Verify's adversarial repair loop and disagreement recording (§6.6), and
the human-approval interrupt/resume (§6.1 node 9).
"""

from langgraph.types import Command

from extraction.graph import REPAIR_BUDGET, VERIFY_BUDGET, build_graph
from extraction.schemas import (
    CanonicalCharge,
    ChargeExtraction,
    PipelineStatus,
    ProposedRule,
    ProvisionalIdentity,
    SectionType,
    SemanticOutcome,
    VerifierFinding,
    VerifierResult,
    VerifierSeverity,
    WindowMapResult,
    WindowSection,
)

from .conftest import StubChatModel

PAGE_TEXTS = {
    1: "Acme Port Authority Tariff Book. Currency: ZAR.",
    2: "2.1 VTS dues. Rate 0.5 per GT, minimum 100.",
    3: "3.1 Pilotage. Not present in this book.",
}


def _good_vts_rule(minimum=100.0):
    return ChargeExtraction(
        charge=CanonicalCharge.VTS,
        outcome=SemanticOutcome.MAPPED,
        proposed_rule=ProposedRule(
            basis="gross_tonnage", rounding_mode="exact", pricing_type="per_unit", pricing_params={"rate": 0.5}, multiplicity="per_call", minimum=minimum
        ),
        provenance_pages=[2],
    )


def _map_respond(user_text):
    if "Pages 1-3" in user_text or "page 2" in user_text:
        return WindowMapResult(
            window_start_page=1,
            window_end_page=3,
            sections=[WindowSection(section_number="2.1", heading="VTS dues", section_type=SectionType.CHARGE, page=2, affects_charges=[CanonicalCharge.VTS])],
        )
    return WindowMapResult(window_start_page=1, window_end_page=3, sections=[])


def _run(llm, thread_id, verify_budget=VERIFY_BUDGET):
    graph = build_graph()
    config = {"configurable": {"thread_id": thread_id, "llm": llm, "repair_budget": REPAIR_BUDGET, "verify_budget": verify_budget}}
    initial = {"pdf_path": "unused", "page_texts": PAGE_TEXTS}
    result = graph.invoke(initial, config=config)
    return graph, result, config


def test_pipeline_runs_to_the_human_approval_interrupt_and_produces_a_clean_report():
    def respond(schema, messages):
        schema_name = schema.__name__
        user_text = messages[-1].content
        if schema_name == "ProvisionalIdentity":
            return ProvisionalIdentity(authority="Acme Port Authority", currency="ZAR")
        if schema_name == "WindowMapResult":
            return _map_respond(user_text)
        if schema_name == "ChargeExtraction":
            if "Canonical charge type to extract: vts" in user_text:
                return _good_vts_rule()
            return ChargeExtraction(charge=CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.NOT_PRESENT)
        if schema_name == "VerifierResult":
            return VerifierResult(charge=CanonicalCharge.VTS, findings=[])
        raise AssertionError(f"unexpected schema {schema_name}")

    llm = StubChatModel(respond)
    graph, result, config = _run(llm, "thread-clean")

    assert "__interrupt__" in result
    report = result["report"]
    vts_entry = next(e for e in report.charges if e.charge is CanonicalCharge.VTS)
    assert vts_entry.outcome is SemanticOutcome.MAPPED
    assert vts_entry.status is None
    assert vts_entry.verify_rounds == 0  # clean on the first pass — no repair round consumed
    assert report.disagreements == []

    resumed = graph.invoke(Command(resume={"approved": True}), config=config)
    assert resumed["approved"] is True


def test_invalid_extraction_triggers_a_validate_repair_round_that_succeeds():
    vts_attempts = {"n": 0}

    def respond(schema, messages):
        schema_name = schema.__name__
        user_text = messages[-1].content
        if schema_name == "ProvisionalIdentity":
            return ProvisionalIdentity(authority="Acme Port Authority", currency="ZAR")
        if schema_name == "WindowMapResult":
            return _map_respond(user_text)
        if schema_name == "ChargeExtraction":
            if "Canonical charge type to extract: vts" in user_text:
                vts_attempts["n"] += 1
                if vts_attempts["n"] == 1:
                    return ChargeExtraction(
                        charge=CanonicalCharge.VTS,
                        outcome=SemanticOutcome.MAPPED,
                        proposed_rule=ProposedRule(basis="displacement", rounding_mode="exact", pricing_type="per_unit", pricing_params={"rate": 0.5}, multiplicity="per_call"),
                        provenance_pages=[2],
                    )
                return _good_vts_rule()
            return ChargeExtraction(charge=CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.NOT_PRESENT)
        if schema_name == "VerifierResult":
            return VerifierResult(charge=CanonicalCharge.VTS, findings=[])
        raise AssertionError(f"unexpected schema {schema_name}")

    llm = StubChatModel(respond)
    _, result, _ = _run(llm, "thread-validate-repair")

    assert vts_attempts["n"] == 2
    report = result["report"]
    vts_entry = next(e for e in report.charges if e.charge is CanonicalCharge.VTS)
    assert vts_entry.repair_attempts == 1
    assert vts_entry.status is None


def test_verifier_material_finding_triggers_a_repair_that_resolves_it():
    """Verify flags a wrong minimum; Extract corrects it; the next verify
    pass finds nothing -> resolved, no disagreement.

    node_verify runs all six charges concurrently each round (five of
    them NOT_PRESENT, one VTS) — attempt counts must be tracked per
    charge, not with one shared counter, or a race between charges
    racing through the same round makes this test flaky/wrong."""
    vts_extract_attempts = {"n": 0}
    vts_verify_attempts = {"n": 0}

    def respond(schema, messages):
        schema_name = schema.__name__
        user_text = messages[-1].content
        if schema_name == "ProvisionalIdentity":
            return ProvisionalIdentity(authority="Acme Port Authority", currency="ZAR")
        if schema_name == "WindowMapResult":
            return _map_respond(user_text)
        if schema_name == "ChargeExtraction":
            if "Canonical charge type to extract: vts" in user_text:
                vts_extract_attempts["n"] += 1
                if vts_extract_attempts["n"] == 1:
                    return _good_vts_rule(minimum=50.0)  # wrong — source says 100
                return _good_vts_rule(minimum=100.0)  # corrected in response to the challenge
            return ChargeExtraction(charge=CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.NOT_PRESENT)
        if schema_name == "VerifierResult":
            if "Canonical charge type under review: vts" in user_text:
                vts_verify_attempts["n"] += 1
                if vts_verify_attempts["n"] == 1:
                    return VerifierResult(
                        charge=CanonicalCharge.VTS,
                        findings=[VerifierFinding(severity=VerifierSeverity.MATERIAL, problem="minimum should be 100, not 50, per the source text", pages=[2])],
                    )
                return VerifierResult(charge=CanonicalCharge.VTS, findings=[])
            return VerifierResult(charge=CanonicalCharge.LIGHT_DUES, findings=[])
        raise AssertionError(f"unexpected schema {schema_name}")

    llm = StubChatModel(respond)
    _, result, _ = _run(llm, "thread-verify-repair")

    assert vts_extract_attempts["n"] == 2
    assert vts_verify_attempts["n"] == 2
    report = result["report"]
    vts_entry = next(e for e in report.charges if e.charge is CanonicalCharge.VTS)
    assert vts_entry.proposed_rule.minimum == 100.0
    assert vts_entry.verify_rounds == 1  # one repair round consumed; the always-happening first pass is free
    assert report.disagreements == []


def test_verifier_disagreement_recorded_after_budget_exhausted_when_extractor_rebuts():
    """Extract is confident its answer is right and rebuts every time —
    Verify keeps disagreeing. After the budget, this must land as an
    unresolved disagreement, never an infinite loop."""

    def respond(schema, messages):
        schema_name = schema.__name__
        user_text = messages[-1].content
        if schema_name == "ProvisionalIdentity":
            return ProvisionalIdentity(authority="Acme Port Authority", currency="ZAR")
        if schema_name == "WindowMapResult":
            return _map_respond(user_text)
        if schema_name == "ChargeExtraction":
            if "Canonical charge type to extract: vts" in user_text:
                extraction = _good_vts_rule(minimum=50.0)
                if "adversarial reviewer" in user_text:  # this is a verify-repair round
                    extraction.rebuttal = "The source's '100' refers to a different fee; 50 is correct for VTS."
                return extraction
            return ChargeExtraction(charge=CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.NOT_PRESENT)
        if schema_name == "VerifierResult":
            if "Canonical charge type under review: vts" in user_text:
                return VerifierResult(
                    charge=CanonicalCharge.VTS,
                    findings=[VerifierFinding(severity=VerifierSeverity.MATERIAL, problem="minimum should be 100, not 50, per the source text", pages=[2])],
                )
            return VerifierResult(charge=CanonicalCharge.LIGHT_DUES, findings=[])
        raise AssertionError(f"unexpected schema {schema_name}")

    llm = StubChatModel(respond)
    _, result, _ = _run(llm, "thread-disagreement", verify_budget=1)

    report = result["report"]
    vts_entry = next(e for e in report.charges if e.charge is CanonicalCharge.VTS)
    assert vts_entry.verify_rounds == VERIFY_BUDGET
    assert len(report.disagreements) == 1
    disagreement = report.disagreements[0]
    assert disagreement.charge is CanonicalCharge.VTS
    assert disagreement.status == "unresolved"
    assert "50 is correct" in disagreement.extractor_interpretation
    assert "minimum should be 100" in disagreement.verifier_concern


def test_verifier_minor_finding_does_not_trigger_a_repair():
    vts_extract_attempts = {"n": 0}

    def respond(schema, messages):
        schema_name = schema.__name__
        user_text = messages[-1].content
        if schema_name == "ProvisionalIdentity":
            return ProvisionalIdentity(authority="Acme Port Authority", currency="ZAR")
        if schema_name == "WindowMapResult":
            return _map_respond(user_text)
        if schema_name == "ChargeExtraction":
            if "Canonical charge type to extract: vts" in user_text:
                vts_extract_attempts["n"] += 1
                return _good_vts_rule()
            return ChargeExtraction(charge=CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.NOT_PRESENT)
        if schema_name == "VerifierResult":
            return VerifierResult(
                charge=CanonicalCharge.VTS, findings=[VerifierFinding(severity=VerifierSeverity.MINOR, problem="citation formatting could be clearer", pages=[2])]
            )
        raise AssertionError(f"unexpected schema {schema_name}")

    llm = StubChatModel(respond)
    _, result, _ = _run(llm, "thread-minor-finding")

    assert vts_extract_attempts["n"] == 1  # no repair round triggered
    report = result["report"]
    vts_entry = next(e for e in report.charges if e.charge is CanonicalCharge.VTS)
    assert vts_entry.verifier_findings[0].severity is VerifierSeverity.MINOR
    assert report.disagreements == []


def test_rejection_at_human_approval_is_recorded():
    def respond(schema, messages):
        schema_name = schema.__name__
        user_text = messages[-1].content
        if schema_name == "ProvisionalIdentity":
            return ProvisionalIdentity(authority="Acme Port Authority", currency="ZAR")
        if schema_name == "WindowMapResult":
            return _map_respond(user_text)
        if schema_name == "ChargeExtraction":
            if "Canonical charge type to extract: vts" in user_text:
                return _good_vts_rule()
            return ChargeExtraction(charge=CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.NOT_PRESENT)
        if schema_name == "VerifierResult":
            return VerifierResult(charge=CanonicalCharge.VTS, findings=[])
        raise AssertionError(f"unexpected schema {schema_name}")

    llm = StubChatModel(respond)
    graph, result, config = _run(llm, "thread-reject")

    resumed = graph.invoke(Command(resume={"approved": False}), config=config)
    assert resumed["approved"] is False
    assert resumed["report"] is not None  # kept, per §6.1 node 9: "reject -> stop, keep the report"


def test_permanently_invalid_extraction_exhausts_the_validate_budget_before_ever_reaching_verify():
    verify_was_called = {"called": False}

    def respond(schema, messages):
        schema_name = schema.__name__
        if schema_name == "ProvisionalIdentity":
            return ProvisionalIdentity(authority="Acme Port Authority")
        if schema_name == "WindowMapResult":
            return WindowMapResult(window_start_page=1, window_end_page=3, sections=[])
        if schema_name == "ChargeExtraction":
            return ChargeExtraction(
                charge=CanonicalCharge.VTS,
                outcome=SemanticOutcome.MAPPED,
                proposed_rule=ProposedRule(basis="displacement", rounding_mode="exact", pricing_type="per_unit", pricing_params={}, multiplicity="per_call"),
            )
        if schema_name == "VerifierResult":
            verify_was_called["called"] = True
            return VerifierResult(charge=CanonicalCharge.VTS, findings=[])
        raise AssertionError

    llm = StubChatModel(respond)
    graph, result, _ = _run(llm, "thread-exhausted")

    report = result["report"]
    vts_entry = next(e for e in report.charges if e.charge is CanonicalCharge.VTS)
    assert vts_entry.status is PipelineStatus.EXTRACTION_FAILED
    assert vts_entry.repair_attempts == REPAIR_BUDGET
    assert verify_was_called["called"] is False  # never structurally valid -> never gets an adversarial pass
