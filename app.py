"""v3: Streamlit UI. Wrapping only — no calculation or business logic
lives here. Every request goes through tariffs.nlp.parse_vessel_request()
and renders whatever ParseResult comes back. tariffs.engine.calculate()
is never called from this file.

Run: streamlit run app.py
Needs ANTHROPIC_API_KEY set in the environment (see README).
"""

import os

import streamlit as st

from tariffs.nlp import Rejected, parse_vessel_request

st.set_page_config(page_title="Port Tariff Calculator", page_icon="\U0001F6A2")
st.title("Port Tariff Calculator")
st.caption(
    "Transnet National Ports Authority (TNPA) port tariffs, 2024/2025 edition — "
    "from a free-text vessel request."
)

if not os.environ.get("ANTHROPIC_API_KEY"):
    st.error("ANTHROPIC_API_KEY is not set in this environment. Set it and restart the app.")
    st.stop()

request_text = st.text_area(
    "Describe the vessel call",
    height=150,
    placeholder=(
        "The bulk carrier SUDESTADA, GT 51,300, called at the Port of Durban. "
        "Arrived 15 Nov 2024, departed 22 Nov 2024. Number of Operations: 2."
    ),
)

if st.button("Calculate", type="primary") and request_text.strip():
    with st.spinner("Parsing request..."):
        try:
            result = parse_vessel_request(request_text)
        except Exception as exc:  # broken program — not a bad request (see tariffs/nlp.py)
            st.exception(exc)
            st.stop()

    if isinstance(result, Rejected):
        st.warning(result.reason)
        if result.parsed_so_far:
            with st.expander("What was understood before rejecting"):
                st.table([e.model_dump() for e in result.parsed_so_far])
        st.stop()

    # Parsed vessel call + evidence shown BEFORE the results.
    st.subheader("Parsed vessel call")
    st.json(result.call.model_dump(mode="json"))

    st.subheader("Evidence")
    if result.evidence:
        st.table([e.model_dump() for e in result.evidence])
    else:
        st.write("(nothing was extracted)")

    st.subheader("Tariffs")
    tariff_rows = []
    for name, outcome in result.tariffs.items():
        if outcome.computed and outcome.result is not None:
            tariff_rows.append({"tariff": name, "amount (ZAR)": f"{outcome.result.amount:,.2f}"})
        else:
            tariff_rows.append({"tariff": name, "amount (ZAR)": f"not computable — {outcome.reason}"})
    st.table(tariff_rows)

    st.subheader("Trace")
    trace_rows = []
    for outcome in result.tariffs.values():
        if outcome.computed and outcome.result:
            for step in outcome.result.trace:
                trace_rows.append(
                    {
                        "tariff": step.tariff,
                        "section": step.section,
                        "page": step.page,
                        "description": step.description,
                        "modifier_resolution": step.modifier_resolution,
                        "subtotal": step.subtotal,
                    }
                )
    if trace_rows:
        st.table(trace_rows)
    else:
        st.write("(no trace)")

    st.subheader("Warnings")
    warnings = [
        w for outcome in result.tariffs.values() if outcome.computed and outcome.result for w in outcome.result.warnings
    ]
    if warnings:
        for w in warnings:
            st.warning(w)
    else:
        st.write("(none)")
