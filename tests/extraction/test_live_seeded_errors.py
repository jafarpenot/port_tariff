"""specs/EXTRACTION_SPEC.md §8 eval 3 — the verifier's seeded-error
catch rate, against the real Verify LLM. Skipped unless
OPENAI_API_KEY is set.
"""

import os

import pytest

from extraction.llm import default_llm
from extraction.pdf import split_pdf
from extraction.seeded_errors import run_seeded_error_eval

pytestmark = pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="requires a real OPENAI_API_KEY")


def test_live_seeded_error_catch_rate():
    page_texts = split_pdf("Port Tariff.pdf")
    llm = default_llm()
    results = run_seeded_error_eval(page_texts, llm)

    caught = sum(1 for r in results.values() if r["caught"])
    total = len(results)
    print(f"\n[live] seeded-error catch rate: {caught}/{total} ({100 * caught / total:.0f}%)")
    for name, r in results.items():
        mark = "CAUGHT" if r["caught"] else "MISSED"
        print(f"  [{mark}] {name} — {r['description']}")
        for finding in r["findings"]:
            print(f"      ({finding['severity']}) {finding['problem']} [pages {finding['pages']}]")

    assert total == 5
