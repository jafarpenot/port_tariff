"""End-to-end pipeline test — no real Anthropic API calls, no PDF file:
page_texts is injected directly (extraction/graph.py's node_split skips
split_pdf when page_texts is already present in the initial state).
Exercises the full sequence including the Validate -> repair -> Extract
loop (§6.5) and the human-approval interrupt/resume (§6.1 node 9).
"""

from langgraph.types import Command

from extraction.graph import REPAIR_BUDGET, build_graph
from extraction.schemas import (
    CanonicalCharge,
    ChargeExtraction,
    PipelineStatus,
    ProposedRule,
    ProvisionalIdentity,
    SectionType,
    SemanticOutcome,
    WindowMapResult,
    WindowSection,
)

from .conftest import StubChatModel

PAGE_TEXTS = {
    1: "Acme Port Authority Tariff Book. Currency: ZAR.",
    2: "2.1 VTS dues. Rate 0.5 per GT, minimum 100.",
    3: "3.1 Pilotage. Not present in this book.",
}


def _respond_factory(vts_first_attempt_is_invalid: bool):
    vts_attempts = {"n": 0}

    def respond(schema, messages):
        schema_name = schema.__name__
        user_text = messages[-1].content

        if schema_name == "ProvisionalIdentity":
            return ProvisionalIdentity(authority="Acme Port Authority", currency="ZAR")

        if schema_name == "WindowMapResult":
            if "Pages 1-3" in user_text or "page 2" in user_text:
                return WindowMapResult(
                    window_start_page=1,
                    window_end_page=3,
                    sections=[
                        WindowSection(section_number="2.1", heading="VTS dues", section_type=SectionType.CHARGE, page=2, affects_charges=[CanonicalCharge.VTS]),
                    ],
                )
            return WindowMapResult(window_start_page=1, window_end_page=3, sections=[])

        if schema_name == "ChargeExtraction":
            if "Canonical charge type to extract: vts" in user_text:
                vts_attempts["n"] += 1
                if vts_first_attempt_is_invalid and vts_attempts["n"] == 1:
                    # Deliberately invalid: unknown basis -> Validate must
                    # reject it and route back here for a repair round.
                    return ChargeExtraction(
                        charge=CanonicalCharge.VTS,
                        outcome=SemanticOutcome.MAPPED,
                        proposed_rule=ProposedRule(
                            basis="displacement",  # not a real Basis member
                            rounding_mode="exact",
                            pricing_type="per_unit",
                            pricing_params={"rate": 0.5},
                            multiplicity="per_call",
                        ),
                        provenance_pages=[2],
                    )
                return ChargeExtraction(
                    charge=CanonicalCharge.VTS,
                    outcome=SemanticOutcome.MAPPED,
                    proposed_rule=ProposedRule(
                        basis="gross_tonnage",
                        rounding_mode="exact",
                        pricing_type="per_unit",
                        pricing_params={"rate": 0.5},
                        multiplicity="per_call",
                        minimum=100.0,
                    ),
                    provenance_pages=[2],
                )
            return ChargeExtraction(charge=CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.NOT_PRESENT)

        raise AssertionError(f"unexpected schema {schema_name}")

    return respond, vts_attempts


def _run(llm, thread_id):
    graph = build_graph()
    config = {"configurable": {"thread_id": thread_id, "llm": llm, "repair_budget": REPAIR_BUDGET}}
    initial = {"pdf_path": "unused", "page_texts": PAGE_TEXTS}
    result = graph.invoke(initial, config=config)
    return graph, result, config


def test_pipeline_runs_to_the_human_approval_interrupt_and_produces_a_report():
    respond, _ = _respond_factory(vts_first_attempt_is_invalid=False)
    llm = StubChatModel(respond)
    graph, result, config = _run(llm, "thread-clean")

    assert "__interrupt__" in result
    report = result["report"]
    vts_entry = next(e for e in report.charges if e.charge is CanonicalCharge.VTS)
    assert vts_entry.outcome is SemanticOutcome.MAPPED
    assert vts_entry.status is None  # valid — no pipeline status set

    resumed = graph.invoke(Command(resume={"approved": True}), config=config)
    assert resumed["approved"] is True


def test_invalid_extraction_triggers_a_repair_round_that_succeeds():
    respond, attempts = _respond_factory(vts_first_attempt_is_invalid=True)
    llm = StubChatModel(respond)
    _, result, _ = _run(llm, "thread-repair")

    assert attempts["n"] == 2  # one bad attempt, one repaired attempt
    report = result["report"]
    vts_entry = next(e for e in report.charges if e.charge is CanonicalCharge.VTS)
    assert vts_entry.outcome is SemanticOutcome.MAPPED
    assert vts_entry.repair_attempts == 1
    assert vts_entry.status is None  # repaired successfully -> not Extraction failed


def test_rejection_at_human_approval_is_recorded():
    respond, _ = _respond_factory(vts_first_attempt_is_invalid=False)
    llm = StubChatModel(respond)
    graph, result, config = _run(llm, "thread-reject")

    resumed = graph.invoke(Command(resume={"approved": False}), config=config)
    assert resumed["approved"] is False
    assert resumed["report"] is not None  # kept, per §6.1 node 9: "reject -> stop, keep the report"


def test_permanently_invalid_extraction_exhausts_the_budget_and_is_marked_extraction_failed():
    def respond(schema, messages):
        schema_name = schema.__name__
        if schema_name == "ProvisionalIdentity":
            return ProvisionalIdentity(authority="Acme Port Authority")
        if schema_name == "WindowMapResult":
            return WindowMapResult(window_start_page=1, window_end_page=3, sections=[])
        if schema_name == "ChargeExtraction":
            # Always invalid, no matter how many repair rounds.
            return ChargeExtraction(
                charge=CanonicalCharge.VTS,
                outcome=SemanticOutcome.MAPPED,
                proposed_rule=ProposedRule(basis="displacement", rounding_mode="exact", pricing_type="per_unit", pricing_params={}, multiplicity="per_call"),
            )
        raise AssertionError

    llm = StubChatModel(respond)
    graph, result, _ = _run(llm, "thread-exhausted")

    report = result["report"]
    vts_entry = next(e for e in report.charges if e.charge is CanonicalCharge.VTS)
    assert vts_entry.status is PipelineStatus.EXTRACTION_FAILED
    assert vts_entry.repair_attempts == REPAIR_BUDGET
