"""Node 8's companion: writes one detailed markdown file per pipeline
run to eval_runs/auto/ — regardless of what invoked the graph (pytest,
the Streamlit page, an ad-hoc script). Complements tests/conftest.py's
pytest-only bare-facts trace, which never sees a non-pytest run at all.

Covers every run that reaches node_report — the same rich content this
session's hand-written eval_runs/*.md entries were built from, no
longer requiring someone to notice a run was worth writing up. Does
NOT cover a run that crashes before reaching the report (a raw
exception in Extract/Verify propagates straight up through
graph.invoke() and node_report never runs) — a known gap, not
attempted here.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .schemas import ReviewReport

_LOG_DIR = Path(__file__).resolve().parent.parent / "eval_runs" / "auto"


def _model_id(llm: Any) -> str:
    # Checked in this order since it's the only thing that differs
    # between the two providers this project uses (ChatOpenAI exposes
    # `model_name`, ChatAnthropic exposes `model`) — a stub test LLM
    # has neither, hence the final fallback.
    return getattr(llm, "model_name", None) or getattr(llm, "model", None) or "unknown"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "run"


def write_run_log(
    report: ReviewReport,
    *,
    pdf_path: str,
    llm: Any,
    thread_id: Optional[str] = None,
    started_at: Optional[float] = None,
) -> Optional[Path]:
    model = _model_id(llm)
    if model == "unknown":
        return None  # a mocked/stub LLM (tests/extraction/conftest.py's StubChatModel)
        # has neither attribute a real ChatOpenAI/ChatAnthropic exposes — treated as the
        # signal this is a test run, not a real one, so the dozens of mocked pytest runs
        # every `pytest` invocation makes don't spam this tracked, committed folder.

    now = datetime.now(timezone.utc)
    duration = f"{now.timestamp() - started_at:.1f}s" if started_at else "unknown"

    lines: list[str] = []
    lines.append(f"# Extraction run — {now.isoformat(timespec='seconds')}")
    lines.append("")
    lines.append(f"**PDF:** {pdf_path}")
    lines.append(f"**Model:** {_model_id(llm)}")
    lines.append(f"**Thread ID:** {thread_id or '(none given)'}")
    lines.append(f"**Duration:** {duration}")
    lines.append("")

    lines.append("## Identity")
    lines.append(f"```\n{report.identity.model_dump()}\n```")
    lines.append(f"is_new_edition={report.is_new_edition} matched_existing_authority={report.matched_existing_authority}")
    lines.append("")

    lines.append("## Coverage")
    lines.append(f"- pages_read: {report.coverage_pages_read}/{report.coverage_total_pages}")
    lines.append(f"- general_terms_found: {report.general_terms_found}")
    lines.append(f"- out_of_scope_sections: {len(report.out_of_scope_sections)}")
    lines.append("")

    lines.append("## Charges")
    for entry in report.charges:
        outcome = entry.outcome.value if entry.outcome else "?"
        status = entry.status.value if entry.status else "-"
        lines.append(f"### {entry.charge.value} — outcome={outcome} status={status}")
        lines.append(f"repair_attempts={entry.repair_attempts} verify_rounds={entry.verify_rounds}")
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

    lines.append("## Disagreements")
    if report.disagreements:
        for d in report.disagreements:
            lines.append(f"- **{d.charge.value}**: {d.verifier_concern}")
    else:
        lines.append("(none)")
    lines.append("")

    identity_bit = report.identity.authority or "unknown-authority"
    filename = f"{now.strftime('%Y%m%dT%H%M%SZ')}_{_slug(identity_bit)}.md"
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = _LOG_DIR / filename
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
