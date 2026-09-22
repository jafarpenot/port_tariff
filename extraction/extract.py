"""Node 5 — Extract (§6.1). LLM, parallel, one call per charge.

Focused context from Assemble, not the whole document. Has read and
search tools (§6.3), used only to follow a lead — a reference pointing
outside the given context. A bounded pre-step: up to MAX_LEAD_ROUNDS of
tool calls, then one structured-output call for the final answer, same
mechanism (`with_structured_output`) as every other LLM node in this
package. Anything found via a tool is flagged in the output — it means
Map/Assemble missed a link, which doubles as a quality signal on Map.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from .llm import structured_call
from .prompts import EXTRACT_SYSTEM_PROMPT, extract_user_prompt
from .schemas import CanonicalCharge, ChargeContext, ChargeExtraction, SectionConsidered, SectionConsideredStatus, ValidationIssue
from .tools import make_tools

MAX_LEAD_ROUNDS = 2
DEFAULT_CONCURRENCY_LIMIT = 5


def _repair_note(issues: list[ValidationIssue]) -> str:
    lines = ["Your previous proposal for this charge failed validation. Fix these specific problems:"]
    for issue in issues:
        line = f"- {issue.message}"
        if issue.allowed_options:
            line += f" (allowed: {issue.allowed_options})"
        lines.append(line)
    return "\n".join(lines)


def _run_tool_rounds(charge: CanonicalCharge, context: ChargeContext, page_texts: dict[int, str], llm: Any) -> list[str]:
    """Returns the leads followed, as human-readable strings — the tool
    *results* are folded into the final call's context text by the
    caller, not returned here."""
    tools = make_tools(page_texts)
    tools_by_name = {t.name: t for t in tools}
    tool_llm = llm.bind_tools(tools)

    messages = [
        SystemMessage(content=EXTRACT_SYSTEM_PROMPT),
        HumanMessage(content=extract_user_prompt(charge.value, context.combined_text)),
    ]
    leads: list[str] = []
    tool_results: list[str] = []
    for _ in range(MAX_LEAD_ROUNDS):
        response = tool_llm.invoke(messages)
        tool_calls = getattr(response, "tool_calls", None)
        if not tool_calls:
            break
        messages.append(response)
        for call in tool_calls:
            tool_obj = tools_by_name.get(call["name"])
            result = tool_obj.invoke(call["args"]) if tool_obj is not None else f"Unknown tool: {call['name']}"
            leads.append(f"{call['name']}({call['args']}) -> used to extend context")
            tool_results.append(str(result))
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    return leads, tool_results


def extract_charge(
    charge: CanonicalCharge,
    context: ChargeContext,
    page_texts: dict[int, str],
    llm: Any,
    *,
    repair_issues: list[ValidationIssue] | None = None,
) -> ChargeExtraction:
    leads, tool_results = _run_tool_rounds(charge, context, page_texts, llm)
    combined_text = context.combined_text
    if tool_results:
        combined_text += "\n\n---\nFollowed a lead outside your original context:\n" + "\n\n".join(tool_results)
    if repair_issues:
        combined_text += "\n\n---\n" + _repair_note(repair_issues)

    extraction = structured_call(
        llm, ChargeExtraction, EXTRACT_SYSTEM_PROMPT, extract_user_prompt(charge.value, combined_text)
    )
    extraction.charge = charge  # the request, not the model's own echo, is authoritative
    if leads:
        extraction.sections_considered.append(
            SectionConsidered(
                heading="Found via the search/read tool, outside the assembled context",
                status=SectionConsideredStatus.USED,
                reason="; ".join(leads),
                found_via_lead=True,
            )
        )
    return extraction


def extract_all(
    charge_contexts: dict[CanonicalCharge, ChargeContext],
    page_texts: dict[int, str],
    llm: Any,
    *,
    concurrency_limit: int = DEFAULT_CONCURRENCY_LIMIT,
    repair_issues_by_charge: dict[CanonicalCharge, list[ValidationIssue]] | None = None,
) -> dict[CanonicalCharge, ChargeExtraction]:
    """Charges in `repair_issues_by_charge` get that charge's specific
    validation errors folded into the prompt (§6.5's repair round);
    every other charge in `charge_contexts` runs a first-pass extraction.
    Pass a `charge_contexts` containing only the charges to (re-)run —
    e.g. just the ones that failed Validate — to repair without redoing
    already-valid charges."""
    charges = list(charge_contexts)
    repairs = repair_issues_by_charge or {}

    def _call(charge: CanonicalCharge) -> ChargeExtraction:
        return extract_charge(charge, charge_contexts[charge], page_texts, llm, repair_issues=repairs.get(charge))

    with ThreadPoolExecutor(max_workers=max(1, concurrency_limit)) as pool:
        results = list(pool.map(_call, charges))
    return dict(zip(charges, results))
