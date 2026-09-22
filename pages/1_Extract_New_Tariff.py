"""Streamlit page: upload a port tariff PDF, run the extraction pipeline
(specs/EXTRACTION_SPEC.md), and review the proposed rate schedule.

Review only. Approving here records the decision on this run but does
not yet feed a working calculation — tariffs/calculators.py's six
functions are hand-written for TNPA's specific schedule shape (named
surcharges, exemption lists, TNPA-only fields), not generic over the
extraction pipeline's basis/pricing_type/pricing_params vocabulary. A
generic, pricing-type-driven calculation engine is future work.

Needs the `extraction` optional dependency group: pip install -e .[extraction]
Needs ANTHROPIC_API_KEY set in the environment, same as app.py — README
tells whoever deploys this to set their own key.
"""

import os
import tempfile
import uuid

import streamlit as st

st.set_page_config(page_title="Extract a New Tariff", page_icon="\U0001F4C4")
st.title("Extract a New Tariff (beta)")
st.caption(
    "Upload any port authority's tariff PDF and an LLM pipeline proposes a structured rate "
    "schedule for human review — naming, currency, per-charge rules, and anything it disagrees "
    "with itself about. Review only for now: approving here does not feed the calculator page "
    "yet, see the module docstring for why."
)

try:
    from langgraph.types import Command

    from extraction.graph import build_graph
    from extraction.llm import default_llm
    from extraction.schemas import VerifierSeverity
except ImportError:
    st.error(
        "The extraction pipeline isn't installed in this environment. "
        'Install it with `pip install -e ".[extraction]"` and restart the app.'
    )
    st.stop()

if not os.environ.get("ANTHROPIC_API_KEY"):
    st.error("ANTHROPIC_API_KEY is not set in this environment. Set it and restart the app.")
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
]:
    st.session_state.setdefault(key, default)

uploaded = st.file_uploader("Port tariff PDF", type=["pdf"])
st.caption("A run makes many real LLM calls and can take several minutes, depending on the book's length.")

if st.button("Run extraction", type="primary", disabled=not uploaded):
    st.session_state["extract_result"] = None
    st.session_state["extract_decision"] = None

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(uploaded.getvalue())
        tmp_path = tmp.name

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id, "llm": default_llm()}, "recursion_limit": 80}

    with st.spinner("Running extraction — split, map, extract, validate, verify. This takes a while."):
        try:
            result = _get_graph().invoke({"pdf_path": tmp_path}, config=config)
        except Exception as exc:  # broken program, not a bad request — see app.py's same pattern
            st.exception(exc)
            st.stop()
        finally:
            os.unlink(tmp_path)

    st.session_state["extract_thread_id"] = thread_id
    st.session_state["extract_config"] = config
    st.session_state["extract_result"] = result

result = st.session_state["extract_result"]
if result is not None:
    _render_report(result["report"])

    if "__interrupt__" in result and st.session_state["extract_decision"] is None:
        st.subheader("Your decision")
        c1, c2 = st.columns(2)
        if c1.button("Approve", type="primary"):
            _get_graph().invoke(Command(resume={"approved": True}), config=st.session_state["extract_config"])
            st.session_state["extract_decision"] = "approved"
            st.rerun()
        if c2.button("Reject"):
            _get_graph().invoke(Command(resume={"approved": False}), config=st.session_state["extract_config"])
            st.session_state["extract_decision"] = "rejected"
            st.rerun()
    elif st.session_state["extract_decision"] is not None:
        st.success(f"Recorded: {st.session_state['extract_decision']}. Upload another PDF above to run again.")
