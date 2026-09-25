"""Node 7 — Verify (§6.1, §6.6). The one genuinely agentic node.

Independent reasoning path: this deliberately does NOT receive Extract's
sections_considered reasoning — only the proposal itself (what it
claims), plus its own whole-document search/read tools to check that
claim directly. A more generous tool budget than Extract's (§6.6: the
one place a ReAct agent is justified), but still bounded — even the
"genuinely agentic" node gets a hard cap, per the "freedom inside nodes,
control on the edges" principle.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from .llm import structured_call
from .prompts import VERIFY_SYSTEM_PROMPT, verify_user_prompt
from .schemas import CanonicalCharge, ChargeExtraction, SemanticOutcome, VerifierResult
from .tools import make_tools

MAX_VERIFY_TOOL_ROUNDS = 4
DEFAULT_CONCURRENCY_LIMIT = 3  # see extraction/extract.py's DEFAULT_CONCURRENCY_LIMIT — same
# reasoning, only relevant when this module is called directly, not through the graph.


def _summarize_proposal(extraction: ChargeExtraction) -> str:
    """What the proposal claims — never how it was derived (no
    sections_considered, no reasoning trail). That's the "independent
    reasoning path" requirement: Verify checks the claim against the
    source, not against Extract's own justification for it."""
    lines = [f"Outcome: {extraction.outcome.value}"]
    if extraction.outcome is SemanticOutcome.MAPPED:
        if extraction.varies_by_port:
            lines.append("Per-port rules:")
            for port, rule in extraction.per_port_rules.items():
                lines.append(
                    f"  {port}: pricing_type={rule.pricing_type}, basis={rule.basis}, "
                    f"multiplicity={rule.multiplicity}, params={rule.pricing_params}, "
                    f"minimum={rule.minimum}, maximum={rule.maximum}"
                )
        elif extraction.proposed_rule:
            r = extraction.proposed_rule
            lines.append(
                f"Rule: pricing_type={r.pricing_type}, basis={r.basis}, multiplicity={r.multiplicity}, "
                f"params={r.pricing_params}, minimum={r.minimum}, maximum={r.maximum}"
            )
    elif extraction.outcome is SemanticOutcome.BUNDLED:
        lines.append(f"Claims this charge is included in: {extraction.included_in.value if extraction.included_in else '(unspecified)'}")
    elif extraction.outcome is SemanticOutcome.UNMAPPED:
        lines.append(f"Claims unmapped; quoted source text: {extraction.unmapped_source_text!r}")
    lines.append(f"Cited sections: {extraction.provenance_sections or '(none)'}, cited pages: {extraction.provenance_pages or '(none)'}")
    if extraction.rebuttal:
        lines.append(f"Note: the proposer has already rebutted an earlier challenge on this charge: {extraction.rebuttal!r}")
    return "\n".join(lines)


def verify_charge(charge: CanonicalCharge, extraction: ChargeExtraction, page_texts: dict[int, str], llm: Any) -> VerifierResult:
    tools = make_tools(page_texts)
    tools_by_name = {t.name: t for t in tools}
    tool_llm = llm.bind_tools(tools)

    proposal_summary = _summarize_proposal(extraction)
    messages = [
        SystemMessage(content=VERIFY_SYSTEM_PROMPT),
        HumanMessage(content=verify_user_prompt(charge.value, proposal_summary)),
    ]
    tool_results: list[str] = []
    for _ in range(MAX_VERIFY_TOOL_ROUNDS):
        response = tool_llm.invoke(messages)
        tool_calls = getattr(response, "tool_calls", None)
        if not tool_calls:
            break
        messages.append(response)
        for call in tool_calls:
            tool_obj = tools_by_name.get(call["name"])
            result = tool_obj.invoke(call["args"]) if tool_obj is not None else f"Unknown tool: {call['name']}"
            tool_results.append(str(result))
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    extra_context = "\n\n".join(tool_results)
    result = structured_call(
        llm, VerifierResult, VERIFY_SYSTEM_PROMPT, verify_user_prompt(charge.value, proposal_summary, extra_context)
    )
    result.charge = charge  # the request, not the model's own echo, is authoritative
    return result


def verify_all(
    extractions: dict[CanonicalCharge, ChargeExtraction],
    page_texts: dict[int, str],
    llm: Any,
    *,
    concurrency_limit: int = DEFAULT_CONCURRENCY_LIMIT,
) -> dict[CanonicalCharge, VerifierResult]:
    charges = list(extractions)

    def _call(charge: CanonicalCharge) -> VerifierResult:
        return verify_charge(charge, extractions[charge], page_texts, llm)

    with ThreadPoolExecutor(max_workers=max(1, concurrency_limit)) as pool:
        results = list(pool.map(_call, charges))
    return dict(zip(charges, results))
