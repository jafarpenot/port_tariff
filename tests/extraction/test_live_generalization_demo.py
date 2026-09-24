"""specs/EXTRACTION_SPEC.md §8 eval 4 — the generalisation demo. Runs the
full pipeline (Extract + Validate + Verify) against a real, different
authority's tariff book and prints the review report: naming
reconciliation, currency, new-schedule vs. diff, and the four semantic
outcomes. Skipped unless OPENAI_API_KEY is set.
"""

import os

import pytest

from extraction.graph import build_graph
from extraction.llm import default_llm

pytestmark = pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="requires a real OPENAI_API_KEY")

PDF_PATH = "new_tariff_pdf/RAK-Ports-Tariff-2026.pdf"


def test_live_generalization_demo_on_a_second_authority():
    llm = default_llm()
    graph = build_graph()
    config = {"configurable": {"thread_id": "generalization-demo-rak-ports", "llm": llm}, "recursion_limit": 80}
    result = graph.invoke({"pdf_path": PDF_PATH}, config=config)

    report = result["report"]
    print("\n=== Identity ===")
    print(report.identity.model_dump())
    print(f"is_new_edition={report.is_new_edition} matched_existing_authority={report.matched_existing_authority}")

    print("\n=== Coverage ===")
    print(f"pages_read={report.coverage_pages_read}/{report.coverage_total_pages}")
    print(f"general_terms_found={report.general_terms_found}")
    print(f"out_of_scope_sections={len(report.out_of_scope_sections)}")

    print("\n=== Charges ===")
    for entry in report.charges:
        outcome = entry.outcome.value if entry.outcome else "?"
        status = entry.status.value if entry.status else "-"
        print(f"{entry.charge.value:20s} outcome={outcome:15s} status={status:17s} repair_attempts={entry.repair_attempts} verify_rounds={entry.verify_rounds}")
        if entry.included_in:
            print(f"    included_in={entry.included_in.value}")
        if entry.unmapped_source_text:
            print(f"    unmapped_source_text={entry.unmapped_source_text[:200]!r}")
        if entry.varies_by_port:
            print(f"    per_port_rules keys: {list(entry.per_port_rules.keys())}")
        elif entry.proposed_rule:
            print(f"    pricing_type={entry.proposed_rule.pricing_type!r} params={entry.proposed_rule.pricing_params}")
        for f in entry.verifier_findings:
            print(f"    ({f.severity.value}) {f.problem[:200]}")

    print("\n=== Disagreements ===")
    for d in report.disagreements:
        print(f"{d.charge.value}: {d.verifier_concern[:200]}")

    assert len(report.charges) == 6
