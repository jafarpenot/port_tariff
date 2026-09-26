"""Node 5 — Extract (§6.1). LLM, parallel, one call per charge.

Focused context from Assemble, not the whole document — sent as the
real PDF pages behind that context (`ChargeContext.pages`), not their
flattened text, same reasoning as Map (see extraction/map_node.py's
docstring). Has read and search tools (§6.3), used only to follow a
lead — a reference pointing outside the given context; those still
operate over `page_texts` (cheap, text-only) purely to *locate* which
extra pages matter. The tool round and the final structured-output
call are two separate, disconnected model calls in this code — nothing
the model sees mid-tool-loop carries forward except the tool results'
own text — so reading a lead's pages natively during the tool loop
itself would be wasted. Instead, any page range read via the
`read_pages` tool is unioned into the charge's page set and attached as
one native PDF alongside the original context in the final call, the
one that actually produces the citable answer. A bounded pre-step: up
to MAX_LEAD_ROUNDS of tool calls, then one structured-output call for
the final answer, same mechanism (`with_structured_output`) as every
other LLM node in this package. Anything found via a tool is flagged in
the output — it means Map/Assemble missed a link, which doubles as a
quality signal on Map.
"""

from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from .llm import structured_call
from .pdf import extract_pdf_pages
from .prompts import EXTRACT_SYSTEM_PROMPT, extract_user_prompt
from .schemas import (
    CanonicalCharge,
    ChargeContext,
    ChargeExtraction,
    SectionConsidered,
    SectionConsideredStatus,
    ValidationIssue,
    VerifierFinding,
)
from .tools import make_tools

MAX_LEAD_ROUNDS = 2
DEFAULT_CONCURRENCY_LIMIT = 3  # graph.py reuses this one constant as the shared default for
# map/extract/verify alike (§6's single, config-overridable knob). Lowered from 5 after a
# live 429 on GPT-6 Luna: 6 charges extracting in parallel burst past a 200k TPM account
# limit. Still configurable per run via config["configurable"]["concurrency_limit"].


def _repair_note(issues: list[ValidationIssue]) -> str:
    lines = ["Your previous proposal for this charge failed validation. Fix these specific problems:"]
    for issue in issues:
        line = f"- {issue.message}"
        if issue.allowed_options:
            line += f" (allowed: {issue.allowed_options})"
        lines.append(line)
    lines.append(
        "If your previous proposal's outcome was 'mapped', it must stay 'mapped' here — fix the "
        "structure or content of that proposal, never reclassify it to bundled/not_present/unmapped "
        "as a way of avoiding the problem above."
    )
    return "\n".join(lines)


def _verifier_challenge_note(findings: list[VerifierFinding]) -> str:
    lines = [
        "An independent adversarial reviewer, working from the source document directly "
        "(not from your reasoning), challenges your proposal for this charge:"
    ]
    for finding in findings:
        lines.append(f"- ({finding.severity.value}) {finding.problem} [pages: {finding.pages}]")
    lines.append(
        "If your proposal's outcome was 'mapped', it must stay 'mapped' — correct the proposal's content "
        "to address the concern, never reclassify it to bundled/not_present/unmapped instead of fixing it."
    )
    lines.append(
        "If you agree, correct your proposal to address this — leave `rebuttal` unset. If you "
        "believe your original proposal is correct despite this challenge, set `rebuttal` to a "
        "specific, evidence-based explanation citing the source text and pages, and leave your "
        "proposal itself unchanged."
    )
    return "\n".join(lines)


def _charge_content(charge: CanonicalCharge, context: ChargeContext, pdf_path: str, notes: str = "") -> str | list:
    """The pages behind this charge's context (`context.pages`), sliced
    from the real PDF and attached natively — or plain text alone if
    Map never found any relevant pages for this charge at all (a valid,
    expected case: a charge genuinely absent from the book), since
    there'd be nothing to attach."""
    text = extract_user_prompt(charge.value, context.pages, notes, pages_attached=bool(context.pages))
    if not context.pages:
        return text
    pdf_bytes = extract_pdf_pages(pdf_path, context.pages)
    b64 = base64.b64encode(pdf_bytes).decode()
    return [
        {"type": "text", "text": text},
        {"type": "file", "source_type": "base64", "mime_type": "application/pdf", "data": b64, "filename": f"{charge.value}-context.pdf"},
    ]


def _run_tool_rounds(
    charge: CanonicalCharge, context: ChargeContext, pdf_path: str, page_texts: dict[int, str], llm: Any
) -> tuple[list[str], list[str], set[int]]:
    """Returns the leads followed (human-readable strings), the tool
    *results* (folded into the final call's notes text by the caller),
    and every page number touched by a `read_pages` call — the caller
    unions these into the charge's page set so the final call attaches
    them as real PDF, not the text this loop saw. `search_document`
    results aren't page-parsed here: it's a locator, not something the
    final answer should cite numbers from directly."""
    tools = make_tools(page_texts)
    tools_by_name = {t.name: t for t in tools}
    tool_llm = llm.bind_tools(tools)

    messages = [
        SystemMessage(content=EXTRACT_SYSTEM_PROMPT),
        HumanMessage(content=_charge_content(charge, context, pdf_path)),
    ]
    leads: list[str] = []
    tool_results: list[str] = []
    extra_pages: set[int] = set()
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
            if call["name"] == "read_pages":
                start, end = call["args"].get("start_page"), call["args"].get("end_page")
                if isinstance(start, int) and isinstance(end, int):
                    extra_pages.update(range(start, end + 1))
    return leads, tool_results, extra_pages


def extract_charge(
    charge: CanonicalCharge,
    context: ChargeContext,
    page_texts: dict[int, str],
    llm: Any,
    *,
    pdf_path: str,
    repair_issues: list[ValidationIssue] | None = None,
    verifier_findings: list[VerifierFinding] | None = None,
) -> ChargeExtraction:
    leads, tool_results, extra_pages = _run_tool_rounds(charge, context, pdf_path, page_texts, llm)
    notes = ""
    if tool_results:
        notes += "Followed a lead outside your original context:\n" + "\n\n".join(tool_results)
    if repair_issues:
        notes += ("\n\n---\n" if notes else "") + _repair_note(repair_issues)
    if verifier_findings:
        notes += ("\n\n---\n" if notes else "") + _verifier_challenge_note(verifier_findings)

    final_context = context
    if extra_pages - set(context.pages):
        final_context = context.model_copy(update={"pages": sorted(set(context.pages) | extra_pages)})

    extraction = structured_call(
        llm, ChargeExtraction, EXTRACT_SYSTEM_PROMPT, _charge_content(charge, final_context, pdf_path, notes)
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
    pdf_path: str,
    concurrency_limit: int = DEFAULT_CONCURRENCY_LIMIT,
    repair_issues_by_charge: dict[CanonicalCharge, list[ValidationIssue]] | None = None,
    verifier_findings_by_charge: dict[CanonicalCharge, list[VerifierFinding]] | None = None,
) -> dict[CanonicalCharge, ChargeExtraction]:
    """Charges in `repair_issues_by_charge` get that charge's specific
    validation errors folded into the prompt (§6.5's repair round);
    charges in `verifier_findings_by_charge` get an adversarial challenge
    folded in instead (§6.6's repair round — the two are never expected
    together, since Validate and Verify run at different graph stages).
    Every other charge in `charge_contexts` runs a first-pass extraction.
    Pass a `charge_contexts` containing only the charges to (re-)run to
    repair without redoing already-settled charges."""
    charges = list(charge_contexts)
    repairs = repair_issues_by_charge or {}
    challenges = verifier_findings_by_charge or {}

    def _call(charge: CanonicalCharge) -> ChargeExtraction:
        return extract_charge(
            charge,
            charge_contexts[charge],
            page_texts,
            llm,
            pdf_path=pdf_path,
            repair_issues=repairs.get(charge),
            verifier_findings=challenges.get(charge),
        )

    with ThreadPoolExecutor(max_workers=max(1, concurrency_limit)) as pool:
        results = list(pool.map(_call, charges))
    return dict(zip(charges, results))
