"""specs/EXTRACTION_SPEC.md §8 eval 1 — the actual Stage 2 checkpoint.
Runs the full pipeline against the real Port Tariff.pdf and scores it
cell by cell against the existing hand-verified gold YAML. Real
Anthropic API calls: identity (1) + Map (7 windows) + Extract (6
charges, possibly with repair rounds) — skipped unless
ANTHROPIC_API_KEY is set, same pattern as every other live test here.
"""

import os

import pytest

from extraction.evaluate import print_score_report, score_report
from extraction.graph import build_graph
from extraction.llm import default_llm

pytestmark = pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="requires a real ANTHROPIC_API_KEY")


def test_live_full_pipeline_accuracy_on_tnpa():
    llm = default_llm()
    graph = build_graph()
    config = {"configurable": {"thread_id": "live-full-run-with-verify", "llm": llm}}
    result = graph.invoke({"pdf_path": "Port Tariff.pdf"}, config=config)

    report = result["report"]
    scores = score_report(report)
    print()
    print_score_report(report, scores)

    print("\n--- Verify (Stage 4) ---")
    for entry in report.charges:
        if entry.verify_rounds or entry.verifier_findings:
            print(f"{entry.charge.value}: verify_rounds={entry.verify_rounds}, findings={len(entry.verifier_findings)}")
            for f in entry.verifier_findings:
                print(f"    ({f.severity.value}) {f.problem} [pages {f.pages}]")
    if report.disagreements:
        print("Unresolved disagreements:")
        for d in report.disagreements:
            print(f"  {d.charge.value}: extractor={d.extractor_interpretation!r} vs verifier={d.verifier_concern!r}")
    else:
        print("No unresolved disagreements.")

    # Not an accuracy assertion (this is a first real run, not a
    # calibrated threshold) — just confirms the run reached the report
    # stage for every charge, i.e. nothing crashed or silently vanished.
    assert len(report.charges) == 6
