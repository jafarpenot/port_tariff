"""Streamlit page: upload a port tariff PDF, run the extraction pipeline
(specs/EXTRACTION_SPEC.md), and review the proposed rate schedule.

Approving now saves the report to `extracted_reports/` (one JSON file
per approval) — the main calculator page (app.py) can load it from
there and compute against it via `tariffs.generic_calculator`'s
data-driven engine, base rate only (v1 — see that module's docstring
for why modifiers aren't applied yet). Rejecting still just records
the decision; nothing is saved.

Needs the `extraction` optional dependency group: pip install -e .[extraction]
Needs OPENAI_API_KEY set in the environment — extraction/llm.py's
default_llm() runs on OpenAI's GPT-6 Luna, not Anthropic, a deliberate
extraction-only cost choice. The calculator page above is unaffected
and still needs its own ANTHROPIC_API_KEY.
"""

import os
import re
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

EXTRACTED_REPORTS_DIR = Path(__file__).resolve().parent.parent / "extracted_reports"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "unknown"


def _save_report(report) -> Path:
    """One JSON file per approval -- never overwritten, so a review
    history accumulates rather than one authority's saves clobbering
    each other. app.py lists this directory to build its "Tariff book"
    picker."""
    EXTRACTED_REPORTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    authority = _slug(report.identity.authority or "unknown-authority")
    path = EXTRACTED_REPORTS_DIR / f"{authority}_{stamp}.json"
    path.write_text(report.model_dump_json(indent=2))
    return path

st.set_page_config(page_title="Extract a New Tariff", page_icon="\U0001F4C4")
st.title("Extract a New Tariff (beta)")
st.caption(
    "Upload any port authority's tariff PDF and an LLM pipeline proposes a structured rate "
    "schedule for human review — naming, currency, per-charge rules, and anything it disagrees "
    "with itself about. Approving saves the report so the calculator page can compute against "
    "it (base rate only — see the module docstring)."
)

try:
    from langgraph.types import Command

    from extraction.extract import DEFAULT_CONCURRENCY_LIMIT
    from extraction.graph import build_graph
    from extraction.llm import default_llm
    from extraction.run_log import run_log_path
    from extraction.schemas import VerifierSeverity
except ImportError:
    st.error(
        "The extraction pipeline isn't installed in this environment. "
        'Install it with `pip install -e ".[extraction]"` and restart the app.'
    )
    st.stop()

if not os.environ.get("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY is not set in this environment. Set it and restart the app.")
    st.stop()


@st.cache_resource
def _get_graph():
    # Shared across every visitor's session on this server process —
    # that's fine, LangGraph's MemorySaver checkpoints per thread_id, and
    # each run below gets its own fresh one. Checkpoints are never
    # evicted, so a long-lived public deployment will grow this
    # process's memory over time — acceptable for now, a real fix is a
    # checkpoint TTL/eviction policy, not attempted here.
    return build_graph()


def _render_report(report) -> None:
    st.subheader("Identity")
    identity = report.identity
    cols = st.columns(3)
    cols[0].metric("Authority", identity.authority or "?")
    cols[1].metric("Currency", identity.currency or "?")
    cols[2].metric("New edition of the loaded schedule?", "Yes" if report.is_new_edition else "No")
    with st.expander("Full identity fields"):
        st.json(identity.model_dump())

    st.subheader("Coverage")
    st.write(
        f"Pages read: {report.coverage_pages_read}/{report.coverage_total_pages} · "
        f"General terms found: {'yes' if report.general_terms_found else 'no'} · "
        f"Out-of-scope sections: {len(report.out_of_scope_sections)}"
    )
    if report.out_of_scope_sections:
        with st.expander("Out-of-scope sections"):
            for s in report.out_of_scope_sections:
                st.write(f"- {s}")

    st.subheader("Charges")
    for entry in report.charges:
        outcome = entry.outcome.value if entry.outcome else "?"
        status = entry.status.value if entry.status else "ok"
        needs_attention = entry.status is not None or bool(entry.verifier_findings)
        with st.expander(f"{entry.charge.value} — outcome: {outcome} · status: {status}", expanded=needs_attention):
            if entry.status is not None:
                st.error(f"Pipeline status: {entry.status.value.replace('_', ' ')} — not safe to use as-is.")
            if entry.included_in:
                st.write(f"Bundled into: **{entry.included_in.value}**")
            if entry.unmapped_source_text:
                st.write("Unmapped source text (quoted, not structured):")
                st.code(entry.unmapped_source_text)
            if entry.varies_by_port and entry.per_port_rules:
                st.write("Varies by port:")
                st.json({port: rule.model_dump() for port, rule in entry.per_port_rules.items()})
            elif entry.proposed_rule:
                st.json(entry.proposed_rule.model_dump())
            for w in entry.warnings:
                st.warning(w)
            if entry.verifier_findings:
                st.write("Verifier findings:")
                for f in entry.verifier_findings:
                    icon = "\U0001F534" if f.severity is VerifierSeverity.MATERIAL else "\U0001F7E1"
                    st.write(f"{icon} ({f.severity.value}) {f.problem}")
            st.caption(f"repair attempts: {entry.repair_attempts} · verify rounds: {entry.verify_rounds}")

    if report.disagreements:
        st.subheader("Unresolved disagreements")
        st.caption(
            "The extractor and the adversarial verifier still disagree after the repair budget "
            "ran out — a human call is needed here, the pipeline deliberately does not force "
            "them to agree."
        )
        for d in report.disagreements:
            with st.expander(d.charge.value):
                st.write("**Extractor's position:**")
                st.write(d.extractor_interpretation)
                st.write("**Verifier's concern:**")
                st.write(d.verifier_concern)


for key, default in [
    ("extract_thread_id", None),
    ("extract_config", None),
    ("extract_result", None),
    ("extract_decision", None),
    ("extract_saved_path", None),
]:
    st.session_state.setdefault(key, default)

uploaded = st.file_uploader("Port tariff PDF", type=["pdf"])
st.caption("A run makes many real LLM calls and can take several minutes, depending on the book's length.")

concurrency_limit = st.number_input(
    "Charges extracted in parallel",
    min_value=1,
    max_value=6,
    value=DEFAULT_CONCURRENCY_LIMIT,
    help=(
        "How many of the six charges extract at once. A book like TNPA, with modest "
        "per-charge context, is fine at 3-4. A larger or more token-heavy book -- one "
        "where Map ends up attaching many more pages per charge (RAK Ports is one "
        "example, found live: single extraction calls there used ~150k of a 200k "
        "tokens-per-minute budget) -- can hit the LLM provider's rate limit when "
        "several such calls run at once; lower this toward 1 (fully sequential, "
        "slower but safest) if you see 'system error' statuses after a run."
    ),
)

if st.button("Run extraction", type="primary", disabled=not uploaded):
    st.session_state["extract_result"] = None
    st.session_state["extract_decision"] = None
    st.session_state["extract_saved_path"] = None

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(uploaded.getvalue())
        tmp_path = tmp.name

    thread_id = str(uuid.uuid4())
    llm = default_llm()
    config = {
        "configurable": {"thread_id": thread_id, "llm": llm, "concurrency_limit": concurrency_limit},
        "recursion_limit": 80,
    }
    # Set here, not left for node_split to generate, so this page can compute the
    # exact same live-log path independently and tail it below (run_log_path() is
    # a pure function of thread_id/run_started_at/llm -- same inputs, same path).
    run_started_at = time.time()
    log_path = run_log_path(thread_id=thread_id, run_started_at=run_started_at, llm=llm)

    graph = _get_graph()  # resolved on this (Streamlit-managed) thread, not the worker below
    outcome: dict = {}

    def _run_graph() -> None:
        try:
            outcome["result"] = graph.invoke({"pdf_path": tmp_path, "run_started_at": run_started_at}, config=config)
        except Exception as exc:  # surfaced on the main thread below, not raised here
            outcome["error"] = exc

    worker = threading.Thread(target=_run_graph, daemon=True)
    worker.start()

    st.subheader("Live progress")
    st.caption("Tailing the same live trace file `docker compose logs -f app | grep '\\[graph\\]'` would show.")
    log_placeholder = st.empty()
    with st.spinner("Running extraction — split, map, extract, validate, verify. This takes a while."):
        while worker.is_alive():
            if log_path and log_path.exists():
                log_placeholder.code(log_path.read_text(), language=None)
            time.sleep(1.5)
        worker.join()
        if log_path and log_path.exists():
            log_placeholder.code(log_path.read_text(), language=None)

    os.unlink(tmp_path)

    if "error" in outcome:
        st.exception(outcome["error"])
        st.stop()

    st.session_state["extract_thread_id"] = thread_id
    st.session_state["extract_config"] = config
    st.session_state["extract_result"] = outcome["result"]

result = st.session_state["extract_result"]
if result is not None:
    _render_report(result["report"])

    if "__interrupt__" in result and st.session_state["extract_decision"] is None:
        st.subheader("Your decision")
        c1, c2 = st.columns(2)
        if c1.button("Approve", type="primary"):
            _get_graph().invoke(Command(resume={"approved": True}), config=st.session_state["extract_config"])
            saved_path = _save_report(result["report"])
            st.session_state["extract_decision"] = "approved"
            st.session_state["extract_saved_path"] = str(saved_path)
            st.rerun()
        if c2.button("Reject"):
            _get_graph().invoke(Command(resume={"approved": False}), config=st.session_state["extract_config"])
            st.session_state["extract_decision"] = "rejected"
            st.rerun()
    elif st.session_state["extract_decision"] is not None:
        st.success(f"Recorded: {st.session_state['extract_decision']}. Upload another PDF above to run again.")
        if st.session_state["extract_saved_path"]:
            st.caption(f"Saved to `{st.session_state['extract_saved_path']}` — pick it on the calculator page's \"Tariff book\" selector.")
