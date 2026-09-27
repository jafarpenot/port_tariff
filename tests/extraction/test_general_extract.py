from extraction.general_extract import extract_charge_general
from extraction.general_shapes import GeneralChargeExtraction, GeneralProposedRule, KeyedBand, ValueFormula
from extraction.schemas import CanonicalCharge, SemanticOutcome

from .conftest import StubChatModel, make_blank_pdf, text_of


def test_extract_charge_general_attaches_native_pdf_and_sets_charge():
    seen = {}

    def respond(schema, messages):
        seen["content"] = messages[-1].content
        return GeneralChargeExtraction(
            charge=CanonicalCharge.TOWAGE,
            outcome=SemanticOutcome.MAPPED,
            proposed_rule=GeneralProposedRule(
                key_dimension="tug type",
                bands=[KeyedBand(key="Ghalilah", value=ValueFormula(kind="flat", flat_amount=1569.0))],
                multiplicity="per_service",
            ),
        )

    llm = StubChatModel(respond)
    result = extract_charge_general(CanonicalCharge.TOWAGE, make_blank_pdf(), [5, 6], llm)

    assert result.charge is CanonicalCharge.TOWAGE  # the request, not the model's own echo
    content = seen["content"]
    assert isinstance(content, list)
    file_block = next(b for b in content if b["type"] == "file")
    assert file_block["filename"] == "towage-context.pdf"


def test_extract_charge_general_with_no_pages_sends_text_only():
    seen = {}

    def respond(schema, messages):
        seen["content"] = messages[-1].content
        return GeneralChargeExtraction(charge=CanonicalCharge.TOWAGE, outcome=SemanticOutcome.NOT_PRESENT)

    llm = StubChatModel(respond)
    result = extract_charge_general(CanonicalCharge.TOWAGE, "unused", [], llm)

    assert result.outcome is SemanticOutcome.NOT_PRESENT
    assert isinstance(seen["content"], str)
    assert "No relevant sections" in text_of(seen["content"])
