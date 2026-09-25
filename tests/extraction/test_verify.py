from langchain_core.messages import AIMessage

from extraction.schemas import (
    CanonicalCharge,
    ChargeExtraction,
    PerUnitShape,
    PricingShapes,
    ProposedRule,
    SemanticOutcome,
    VerifierFinding,
    VerifierResult,
    VerifierSeverity,
    has_material_finding,
)
from extraction.verify import MAX_VERIFY_TOOL_ROUNDS, verify_all, verify_charge

from .conftest import StubChatModel


def _mapped_extraction(charge):
    return ChargeExtraction(
        charge=charge,
        outcome=SemanticOutcome.MAPPED,
        proposed_rule=ProposedRule(basis="gross_tonnage", rounding_mode="exact", pricing=PricingShapes(per_unit=PerUnitShape(selected=True, rate=1.0)), multiplicity="per_call"),
        provenance_pages=[3],
    )


def test_verify_charge_with_no_findings():
    def respond(schema, messages):
        return VerifierResult(charge=CanonicalCharge.VTS, findings=[])

    llm = StubChatModel(respond)
    result = verify_charge(CanonicalCharge.VTS, _mapped_extraction(CanonicalCharge.VTS), {1: "text"}, llm)
    assert result.findings == []
    assert has_material_finding(result) is False


def test_verify_charge_the_request_charge_is_authoritative():
    def respond(schema, messages):
        # Echoes the wrong charge — must not be trusted over the request.
        return VerifierResult(charge=CanonicalCharge.LIGHT_DUES, findings=[])

    llm = StubChatModel(respond)
    result = verify_charge(CanonicalCharge.TOWAGE, _mapped_extraction(CanonicalCharge.TOWAGE), {1: "text"}, llm)
    assert result.charge == CanonicalCharge.TOWAGE


def test_verify_charge_does_not_see_sections_considered_reasoning():
    """Independent reasoning path (§6.6): Verify's prompt must not carry
    Extract's own justification for its answer."""
    from extraction.schemas import SectionConsidered, SectionConsideredStatus

    extraction = _mapped_extraction(CanonicalCharge.VTS)
    extraction.sections_considered = [
        SectionConsidered(heading="Secret extractor reasoning", status=SectionConsideredStatus.USED, reason="trust me")
    ]
    seen = {}

    def respond(schema, messages):
        seen["text"] = messages[-1].content
        return VerifierResult(charge=CanonicalCharge.VTS, findings=[])

    llm = StubChatModel(respond)
    verify_charge(CanonicalCharge.VTS, extraction, {1: "text"}, llm)
    assert "Secret extractor reasoning" not in seen["text"]
    assert "trust me" not in seen["text"]


def test_verify_charge_folds_tool_results_into_final_call():
    call_count = {"n": 0}

    def tool_respond(tools, messages):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return AIMessage(content="", tool_calls=[{"name": "search_document", "args": {"query": "contradicts"}, "id": "c1"}])
        return AIMessage(content="", tool_calls=[])

    seen = {}

    def respond(schema, messages):
        seen["text"] = messages[-1].content
        return VerifierResult(
            charge=CanonicalCharge.VTS,
            findings=[VerifierFinding(severity=VerifierSeverity.MATERIAL, problem="rate contradicts source", pages=[5])],
        )

    page_texts = {1: "text", 5: "this section directly contradicts the proposed rate"}
    llm = StubChatModel(respond, tool_respond)
    result = verify_charge(CanonicalCharge.VTS, _mapped_extraction(CanonicalCharge.VTS), page_texts, llm)

    assert has_material_finding(result) is True
    assert "contradicts the proposed rate" in seen["text"]


def test_verify_charge_tool_loop_is_bounded():
    call_count = {"n": 0}

    def tool_respond(tools, messages):
        call_count["n"] += 1
        return AIMessage(content="", tool_calls=[{"name": "search_document", "args": {"query": "x"}, "id": f"c{call_count['n']}"}])

    def respond(schema, messages):
        return VerifierResult(charge=CanonicalCharge.VTS, findings=[])

    llm = StubChatModel(respond, tool_respond)
    verify_charge(CanonicalCharge.VTS, _mapped_extraction(CanonicalCharge.VTS), {1: "text"}, llm)
    assert call_count["n"] == MAX_VERIFY_TOOL_ROUNDS


def test_verify_all_runs_every_charge():
    def respond(schema, messages):
        return VerifierResult(charge=CanonicalCharge.VTS, findings=[])

    llm = StubChatModel(respond)
    extractions = {c: _mapped_extraction(c) for c in CanonicalCharge}
    results = verify_all(extractions, {1: "text"}, llm)
    assert set(results.keys()) == set(CanonicalCharge)
    for charge, result in results.items():
        assert result.charge == charge


def test_has_material_finding_distinguishes_severity():
    minor_only = VerifierResult(charge=CanonicalCharge.VTS, findings=[VerifierFinding(severity=VerifierSeverity.MINOR, problem="x")])
    material = VerifierResult(charge=CanonicalCharge.VTS, findings=[VerifierFinding(severity=VerifierSeverity.MATERIAL, problem="y")])
    assert has_material_finding(minor_only) is False
    assert has_material_finding(material) is True
    assert has_material_finding(None) is False
