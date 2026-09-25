"""Live smoke tests — skipped unless OPENAI_API_KEY is set, same
pattern as tests/test_nlp_parser.py's live tests. Cheap and small on
purpose: this checks the real API actually works with these schemas
(structured output on nested Pydantic models, bind_tools) before
spending more on a full pipeline run against the whole PDF.
"""

import os

import pytest

from extraction.identity import provisional_identity
from extraction.llm import default_llm
from extraction.map_node import map_document
from extraction.pdf import split_pdf
from extraction.schemas import CanonicalCharge, ChargeExtraction, PerUnitShape, PricingShapes, ProposedRule, SemanticOutcome, has_material_finding
from extraction.verify import verify_charge

pytestmark = pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="requires a real OPENAI_API_KEY")

PDF_PATH = "Port Tariff.pdf"


@pytest.fixture(scope="module")
def page_texts():
    return split_pdf(PDF_PATH)


def test_live_provisional_identity(page_texts):
    llm = default_llm()
    identity = provisional_identity(page_texts, llm)
    print("\n[live] provisional_identity:", identity.model_dump())
    assert identity.currency  # the opening pages do state a currency


def test_live_map_single_window(page_texts):
    llm = default_llm()
    window_pages = {p: page_texts[p] for p in range(1, 4) if p in page_texts}
    result = map_document(window_pages, llm, window_size=3, overlap=1, concurrency_limit=1)
    print("\n[live] map window result:", [r.model_dump() for r in result])
    assert len(result) == 1
    assert isinstance(result[0].sections, list)


def test_live_verify_catches_an_obviously_wrong_rate(page_texts):
    """A minimal correctness check, not just a wiring smoke test: VTS's
    real rate is well under 1.0 per GT everywhere in the book — a
    proposed 999.0 is off by roughly three orders of magnitude. If
    Verify can't flag this as material, it isn't doing its job."""
    llm = default_llm()
    wrong_extraction = ChargeExtraction(
        charge=CanonicalCharge.VTS,
        outcome=SemanticOutcome.MAPPED,
        proposed_rule=ProposedRule(basis="gross_tonnage", rounding_mode="exact", pricing=PricingShapes(per_unit=PerUnitShape(selected=True, rate=999.0)), multiplicity="per_call"),
        provenance_pages=[11],
    )
    result = verify_charge(CanonicalCharge.VTS, wrong_extraction, page_texts, llm)
    print("\n[live] verify (deliberately wrong rate):", result.model_dump())
    assert has_material_finding(result) is True
