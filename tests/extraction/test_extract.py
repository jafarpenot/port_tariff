from langchain_core.messages import AIMessage

from extraction.extract import extract_all, extract_charge
from extraction.schemas import (
    CanonicalCharge,
    ChargeContext,
    ChargeExtraction,
    SemanticOutcome,
    ValidationIssue,
    ValidationSeverity,
    VerifierFinding,
    VerifierSeverity,
)

from .conftest import StubChatModel


def _context(charge, text="Some section text.", section_numbers=None):
    return ChargeContext(charge=charge, section_numbers=section_numbers or ["1.1"], combined_text=text)


def test_extract_charge_with_no_tool_calls_returns_the_structured_answer():
    def respond(schema, messages):
        return ChargeExtraction(charge=CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.NOT_PRESENT)

    llm = StubChatModel(respond)  # default tool_respond: never calls a tool
    result = extract_charge(CanonicalCharge.LIGHT_DUES, _context(CanonicalCharge.LIGHT_DUES), {1: "text"}, llm)

    assert result.outcome == SemanticOutcome.NOT_PRESENT
    assert result.sections_considered == []  # no lead followed -> nothing appended


def test_extract_charge_follows_a_lead_and_flags_it():
    call_count = {"n": 0}

    def tool_respond(tools, messages):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return AIMessage(
                content="",
                tool_calls=[{"name": "search_document", "args": {"query": "referenced clause"}, "id": "call_1"}],
            )
        return AIMessage(content="", tool_calls=[])  # stop after one round

    seen_final_context = {}

    def respond(schema, messages):
        seen_final_context["text"] = messages[-1].content
        return ChargeExtraction(charge=CanonicalCharge.PORT_DUES, outcome=SemanticOutcome.MAPPED)

    page_texts = {1: "Section 1.1 text.", 2: "Section referenced clause lives here with details."}
    llm = StubChatModel(respond, tool_respond)
    result = extract_charge(CanonicalCharge.PORT_DUES, _context(CanonicalCharge.PORT_DUES), page_texts, llm)

    assert result.outcome == SemanticOutcome.MAPPED
    assert len(result.sections_considered) == 1
    assert result.sections_considered[0].found_via_lead is True
    assert "referenced clause lives here" in seen_final_context["text"]  # tool result folded into final call


def test_extract_charge_stops_after_max_lead_rounds():
    call_count = {"n": 0}

    def tool_respond(tools, messages):
        call_count["n"] += 1
        # Always wants to call a tool — must not loop forever.
        return AIMessage(content="", tool_calls=[{"name": "search_document", "args": {"query": "x"}, "id": f"call_{call_count['n']}"}])

    def respond(schema, messages):
        return ChargeExtraction(charge=CanonicalCharge.TOWAGE, outcome=SemanticOutcome.UNMAPPED, unmapped_source_text="n/a")

    llm = StubChatModel(respond, tool_respond)
    extract_charge(CanonicalCharge.TOWAGE, _context(CanonicalCharge.TOWAGE), {1: "text"}, llm)

    from extraction.extract import MAX_LEAD_ROUNDS

    assert call_count["n"] == MAX_LEAD_ROUNDS  # bounded, not unbounded


def test_repair_issues_are_folded_into_the_prompt():
    seen = {}

    def respond(schema, messages):
        seen["text"] = messages[-1].content
        return ChargeExtraction(charge=CanonicalCharge.VTS, outcome=SemanticOutcome.MAPPED)

    llm = StubChatModel(respond)
    issues = [ValidationIssue(severity=ValidationSeverity.HARD, message="Unknown basis 'foo'", allowed_options=["gross_tonnage"])]
    extract_charge(CanonicalCharge.VTS, _context(CanonicalCharge.VTS), {1: "text"}, llm, repair_issues=issues)

    assert "Unknown basis 'foo'" in seen["text"]
    assert "gross_tonnage" in seen["text"]


def test_extract_all_only_repairs_charges_with_issues():
    requested_charges = []

    def respond(schema, messages):
        requested_charges.append(messages[-1].content)
        return ChargeExtraction(charge=CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.NOT_PRESENT)

    llm = StubChatModel(respond)
    contexts = {CanonicalCharge.LIGHT_DUES: _context(CanonicalCharge.LIGHT_DUES)}  # only the failing charge
    issues = {CanonicalCharge.LIGHT_DUES: [ValidationIssue(severity=ValidationSeverity.HARD, message="bad thing")]}
    results = extract_all(contexts, {1: "text"}, llm, repair_issues_by_charge=issues)

    assert list(results.keys()) == [CanonicalCharge.LIGHT_DUES]
    assert "bad thing" in requested_charges[0]


def test_verifier_findings_are_folded_into_the_prompt():
    seen = {}

    def respond(schema, messages):
        seen["text"] = messages[-1].content
        return ChargeExtraction(charge=CanonicalCharge.VTS, outcome=SemanticOutcome.MAPPED)

    llm = StubChatModel(respond)
    findings = [VerifierFinding(severity=VerifierSeverity.MATERIAL, problem="rate does not match the source", pages=[5])]
    extract_charge(CanonicalCharge.VTS, _context(CanonicalCharge.VTS), {1: "text"}, llm, verifier_findings=findings)

    assert "rate does not match the source" in seen["text"]
    assert "adversarial reviewer" in seen["text"]


def test_extract_charge_can_rebut_a_verifier_challenge_and_leave_proposal_unchanged():
    def respond(schema, messages):
        return ChargeExtraction(
            charge=CanonicalCharge.VTS,
            outcome=SemanticOutcome.MAPPED,
            rebuttal="The source at page 5 confirms this rate; the reviewer's concern is mistaken.",
        )

    llm = StubChatModel(respond)
    findings = [VerifierFinding(severity=VerifierSeverity.MATERIAL, problem="rate does not match the source", pages=[5])]
    result = extract_charge(CanonicalCharge.VTS, _context(CanonicalCharge.VTS), {1: "text"}, llm, verifier_findings=findings)

    assert result.rebuttal is not None
    assert "reviewer's concern is mistaken" in result.rebuttal


def test_extract_all_runs_every_charge_and_the_request_charge_is_authoritative():
    def respond(schema, messages):
        # Deliberately echo the WRONG charge — extract_charge must not
        # trust the model's own self-report over what was actually asked.
        return ChargeExtraction(charge=CanonicalCharge.VTS, outcome=SemanticOutcome.NOT_PRESENT)

    llm = StubChatModel(respond)
    contexts = {c: _context(c) for c in CanonicalCharge}
    results = extract_all(contexts, {1: "text"}, llm)

    assert set(results.keys()) == set(CanonicalCharge)
    for charge, extraction in results.items():
        assert extraction.charge == charge
