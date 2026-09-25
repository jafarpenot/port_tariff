"""Writes one markdown file per pipeline run to eval_runs/auto/, live —
appended to as the run progresses, not held in memory and only flushed
by node_report. That matters: a run that crashes mid-pipeline (a real
timeout killed a 28-minute TNPA run outright) used to leave nothing
behind but a bare pass/fail line; now everything up to the crash is
already on disk. Covers every run regardless of what invoked the graph
(pytest, the Streamlit page, an ad-hoc script) — complements
tests/conftest.py's pytest-only bare-facts trace.

The path is deterministic from (thread_id, run_started_at) — every
node can compute it independently without threading a Path through
state, which would need PipelineState/checkpointer changes for
something that's really just a side effect.
"""

from __future__ import annotations

import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .schemas import CanonicalCharge, ReviewReport, ValidationResult

_LOG_DIR = Path(__file__).resolve().parent.parent / "eval_runs" / "auto"
_write_lock = threading.Lock()


def _model_id(llm: Any) -> str:
    # Checked in this order since it's the only thing that differs
    # between the two providers this project uses (ChatOpenAI exposes
    # `model_name`, ChatAnthropic exposes `model`) — a stub test LLM
    # has neither, hence the final fallback.
    return getattr(llm, "model_name", None) or getattr(llm, "model", None) or "unknown"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "run"


def run_log_path(*, thread_id: Optional[str], run_started_at: Optional[float], llm: Any) -> Optional[Path]:
    """None whenever there's nothing sensible to log to: a mocked/stub
    LLM (tests/extraction/conftest.py's StubChatModel exposes neither
    `model_name` nor `model` — the signal this is a test run, not a
    real one, so the ~250 mocked pytest runs every `pytest` invocation
    makes never touch this tracked, committed folder), or missing
    thread_id/run_started_at (nothing to key a stable path on)."""
    if _model_id(llm) == "unknown" or not thread_id or not run_started_at:
        return None
    stamp = datetime.fromtimestamp(run_started_at, tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return _LOG_DIR / f"{stamp}_{_slug(thread_id)}.md"


def start_run(path: Optional[Path], *, pdf_path: str, llm: Any, thread_id: Optional[str]) -> None:
    """Idempotent — safe to call on every node, only the first call (per
    path) actually creates the file."""
    if path is None or path.exists():
        return
    with _write_lock:
        if path.exists():
            return
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        header = (
            f"# Extraction run — {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n\n"
            f"**PDF:** {pdf_path}\n"
            f"**Model:** {_model_id(llm)}\n"
            f"**Thread ID:** {thread_id or '(none given)'}\n\n"
            "Written live as the run progresses, not just at the end — if this file "
            "stops mid-trace with no \"Final report\" section below, the run crashed or "
            "is still in progress; everything above the cutoff genuinely happened.\n\n"
            "## Live trace\n```\n"
        )
        path.write_text(header, encoding="utf-8")


def append_trace(path: Optional[Path], msg: str) -> None:
    if path is None:
        return
    with _write_lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")


def finish_run(
    path: Optional[Path],
    report: ReviewReport,
    *,
    started_at: Optional[float] = None,
    validation_history: Optional[dict[CanonicalCharge, list[ValidationResult]]] = None,
) -> None:
    """Appends the polished final summary to the same live file — only
    reached on a successful run (node_report). A crashed run simply
    ends at whatever the live trace had captured up to that point."""
    if path is None:
        return

    now = datetime.now(timezone.utc)
    duration = f"{now.timestamp() - started_at:.1f}s" if started_at else "unknown"

    lines: list[str] = ["```\n"]  # closes the "## Live trace" fence opened by start_run
    lines.append(f"\n## Final report — duration {duration}\n")

    lines.append("### Identity")
    lines.append(f"```\n{report.identity.model_dump()}\n```")
    lines.append(f"is_new_edition={report.is_new_edition} matched_existing_authority={report.matched_existing_authority}")
    lines.append("")

    lines.append("### Coverage")
    lines.append(f"- pages_read: {report.coverage_pages_read}/{report.coverage_total_pages}")
    lines.append(f"- general_terms_found: {report.general_terms_found}")
    lines.append(f"- out_of_scope_sections: {len(report.out_of_scope_sections)}")
    lines.append("")

    lines.append("### Charges")
    for entry in report.charges:
        outcome = entry.outcome.value if entry.outcome else "?"
        status = entry.status.value if entry.status else "-"
        lines.append(f"#### {entry.charge.value} — outcome={outcome} status={status}")
        lines.append(f"repair_attempts={entry.repair_attempts} verify_rounds={entry.verify_rounds}")
        history = (validation_history or {}).get(entry.charge, [])
        if len(history) > 1:  # only worth showing when something actually changed across attempts
            lines.append("- validation history:")
            for i, result in enumerate(history, start=1):
                verdict = "valid" if result.valid else "invalid"
                lines.append(f"  - attempt {i}: {verdict}")
                for issue in result.issues:
                    lines.append(f"    - ({issue.severity.value}) {issue.message}")
        if entry.included_in:
            lines.append(f"- included_in: {entry.included_in.value}")
        if entry.unmapped_source_text:
            lines.append(f"- unmapped_source_text: {entry.unmapped_source_text!r}")
        if entry.varies_by_port and entry.per_port_rules:
            lines.append(f"- per_port_rules: {[(port, rule.pricing_type, rule.pricing_params) for port, rule in entry.per_port_rules.items()]}")
        elif entry.proposed_rule:
            lines.append(f"- pricing_type: {entry.proposed_rule.pricing_type!r} params: {entry.proposed_rule.pricing_params}")
        for w in entry.warnings:
            lines.append(f"- warning: {w}")
        for f in entry.verifier_findings:
            lines.append(f"- ({f.severity.value}) {f.problem}")
        lines.append("")

    lines.append("### Disagreements")
    if report.disagreements:
        for d in report.disagreements:
            lines.append(f"- **{d.charge.value}**: {d.verifier_concern}")
    else:
        lines.append("(none)")
    lines.append("")

    with _write_lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines))
