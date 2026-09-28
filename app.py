"""v3: Streamlit UI. Wrapping only — no calculation or business logic
lives here. Every request goes through tariffs.nlp.parse_vessel_request()
and renders whatever ParseResult comes back. tariffs.engine.calculate()
is never called from this file.

The "Tariff book" selector below is the only new logic: TNPA (existing)
calls parse_vessel_request() exactly as before (tariff_plan=None, its
own default); a saved, approved extraction report instead loads that
report, compiles it via tariffs.generic_calculator (base rate only —
see that module's docstring), and passes the result in as tariff_plan.

Run: streamlit run app.py
Needs ANTHROPIC_API_KEY set in the environment (see README).
"""

import os
from pathlib import Path

import streamlit as st

from tariffs.nlp import BERTHING_SERVICES_NOTE, Rejected, parse_vessel_request

try:
    from extraction.schemas import ReviewReport

    from tariffs.generic_calculator import compile_report, to_tariff_plan

    _EXTRACTION_AVAILABLE = True
except ImportError:
    # The `extraction` optional dependency group isn't installed — the
    # base TNPA calculator below still works fully; only the "load a
    # newly extracted tariff book" option is unavailable.
    _EXTRACTION_AVAILABLE = False

EXTRACTED_REPORTS_DIR = Path(__file__).resolve().parent / "extracted_reports"

st.set_page_config(page_title="Port Tariff Calculator", page_icon="\U0001F6A2")
st.title("Port Tariff Calculator")
st.caption(
    "Transnet National Ports Authority (TNPA) port tariffs, 2024/2025 edition — "
    "from a free-text vessel request."
)

if not os.environ.get("ANTHROPIC_API_KEY"):
    st.error("ANTHROPIC_API_KEY is not set in this environment. Set it and restart the app.")
    st.stop()


def _saved_reports() -> dict[str, Path]:
    """label -> path, newest first. Label falls back to the filename if
    a saved report is somehow unreadable (never lets one bad file break
    the picker for every other saved report)."""
    if not EXTRACTED_REPORTS_DIR.exists():
        return {}
    labels: dict[str, Path] = {}
    for path in sorted(EXTRACTED_REPORTS_DIR.glob("*.json"), reverse=True):
        try:
            authority = ReviewReport.model_validate_json(path.read_text()).identity.authority
        except Exception:
            authority = None
        stamp = path.stem.rsplit("_", 1)[-1]
        labels[f"{authority or path.stem} — {stamp}"] = path
    return labels


TNPA_EXISTING = "TNPA (existing)"
saved = _saved_reports() if _EXTRACTION_AVAILABLE else {}
tariff_book = st.selectbox("Tariff book", [TNPA_EXISTING, *saved.keys()])
if tariff_book != TNPA_EXISTING:
    st.caption(
        "Computing against a freshly extracted (not hand-written) schedule — base rate only, "
        "modifiers are reported as skipped, never applied."
    )

request_text = st.text_area(
    "Describe the vessel call",
    height=150,
    placeholder=(
        "The bulk carrier SUDESTADA, GT 51,300, called at the Port of Durban. "
        "Arrived 15 Nov 2024, departed 22 Nov 2024. Number of Operations: 2."
    ),
)

if st.button("Calculate", type="primary") and request_text.strip():
    tariff_plan = None
    if tariff_book != TNPA_EXISTING:
        loaded_report = ReviewReport.model_validate_json(saved[tariff_book].read_text())
        charges_by_key = {entry.charge: entry for entry in loaded_report.charges}
        compiled = compile_report(charges_by_key, currency=loaded_report.identity.currency or "ZAR")
        tariff_plan = to_tariff_plan(compiled)

    with st.spinner("Parsing request..."):
        try:
            result = parse_vessel_request(request_text, tariff_plan=tariff_plan)
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
    # "berthing_services" is what actually answers the assignment's
    # "running of vessel lines dues" — carried in its own "note" column
    # below (README §3), not just documented separately.
    tariff_rows = []
    for name, outcome in result.tariffs.items():
        row = {
            "tariff": name,
            "note": BERTHING_SERVICES_NOTE if name == "berthing_services" else "",
        }
        if outcome.computed and outcome.result is not None:
            row["amount"] = f"{outcome.result.amount:,.2f}"
            # Genuinely from the selected schedule (specs/EXTRACTION_SPEC.md
            # §5.2) — a column, not baked into the "amount" header, since a
            # single table's rows aren't guaranteed to share one currency.
            row["currency"] = outcome.result.currency
        else:
            # outcome.reason already reads "not computable — ..." (built
            # once, at the source, in tariffs/nlp.py).
            row["amount"] = outcome.reason
            row["currency"] = ""
        tariff_rows.append(row)
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
