"""Repo-wide pytest hooks. Currently one: an automatic, append-only trace
of every live test (anything with "test_live" in its name — the existing
convention both tests/test_nlp_parser.py and tests/extraction/test_live_*.py
already follow, gated by pytest.mark.skipif on an API key being set).

This is a bare-facts trace (timestamp, pass/fail/skipped, duration, which
test), not a substitute for eval_runs/*.md's hand-written narrative
entries — a live run whose actual result matters (a real comparison, a
bug reproduced live, a number worth remembering) still gets its own
dated write-up there. This just guarantees no live run goes completely
unrecorded even when nobody writes one up.
"""

from __future__ import annotations

import datetime
from pathlib import Path

_LOG_PATH = Path(__file__).resolve().parent.parent / "eval_runs" / "auto_log.md"


def pytest_runtest_logreport(report) -> None:
    # A skipped test (pytest.mark.skipif, no API key set) only ever reports
    # during "setup", never "call" — log that one. A test that actually ran
    # reports "setup"/"call"/"teardown" separately; "call" is the real
    # pass/fail outcome, the other two are just fixture bookkeeping.
    is_the_one_real_outcome = report.when == "call" or report.outcome == "skipped"
    if not is_the_one_real_outcome or "test_live" not in report.nodeid:
        return

    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    duration = f"{report.duration:.1f}s"
    line = f"- {timestamp} | {report.outcome:7s} | {duration:>7s} | {report.nodeid}\n"

    _LOG_PATH.parent.mkdir(exist_ok=True)
    is_new = not _LOG_PATH.exists()
    with open(_LOG_PATH, "a", encoding="utf-8") as f:
        if is_new:
            f.write(
                "# Automatic live-test trace\n\n"
                "One line per live test outcome, appended automatically (tests/conftest.py's "
                "pytest_runtest_logreport hook) — every run, not hand-written. See this "
                "folder's other files for the analytical write-ups of the runs that mattered.\n\n"
            )
        f.write(line)
