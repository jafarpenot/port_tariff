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
from typing import Any, Callable

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from .llm import structured_call
from .pdf import extract_pdf_pages
from .prompts import EXTRACT_SYSTEM_PROMPT, MODIFIER_SYSTEM_PROMPT, extract_user_prompt
from .schemas import (
    CanonicalCharge,
    ChargeContext,
    ChargeExtraction,
    ModifierExtraction,
    SectionConsidered,
    SectionConsideredStatus,
    SemanticOutcome,
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


def _charge_content(
    charge: CanonicalCharge, context: ChargeContext, pdf_path: str, notes: str = "", structure_notes: str = ""
) -> str | list:
    """The pages behind this charge's context (`context.pages`), sliced
    from the real PDF and attached natively — or plain text alone if
    Map never found any relevant pages for this charge at all (a valid,
    expected case: a charge genuinely absent from the book), since
    there'd be nothing to attach."""
    text = extract_user_prompt(
        charge.value,
        context.pages,
        notes,
        pages_attached=bool(context.pages),
        structure_notes=structure_notes,
        map_notes=context.notes,
    )
    if not context.pages:
        return text
    pdf_bytes = extract_pdf_pages(pdf_path, context.pages)
    b64 = base64.b64encode(pdf_bytes).decode()
    return [
        {"type": "text", "text": text},
        {"type": "file", "source_type": "base64", "mime_type": "application/pdf", "data": b64, "filename": f"{charge.value}-context.pdf"},
    ]


def _modifier_content(
    charge: CanonicalCharge, context: ChargeContext, pdf_path: str, structure_notes: str = ""
) -> str | list:
    """Same shape as `_charge_content`, but sourced from
    `context.modifier_pages` — a separate, usually smaller page set —
    instead of the base-rate `context.pages`. Stage 3's two calls per
    charge are deliberately given different attachments, not just a
    different prompt over the same pages."""
    text = extract_user_prompt(
        charge.value,
        context.modifier_pages,
        "",
        pages_attached=bool(context.modifier_pages),
        structure_notes=structure_notes,
        map_notes=context.notes,
    )
    if not context.modifier_pages:
        return text
    pdf_bytes = extract_pdf_pages(pdf_path, context.modifier_pages)
    b64 = base64.b64encode(pdf_bytes).decode()
    return [
        {"type": "text", "text": text},
        {"type": "file", "source_type": "base64", "mime_type": "application/pdf", "data": b64, "filename": f"{charge.value}-modifiers.pdf"},
    ]


def _extract_modifiers(charge: CanonicalCharge, context: ChargeContext, pdf_path: str, llm: Any, structure_notes: str = "") -> ModifierExtraction:
    """Stage 3's second, independent, best-effort call per charge — never
    allowed to fail the charge as a whole (unlike the base-rate call):
    a modifier that can't be found or a transient error here just means
    an empty, unremarkable ModifierExtraction, not a lost charge."""
    try:
        return structured_call(
            llm,
            ModifierExtraction,
            MODIFIER_SYSTEM_PROMPT,
            _modifier_content(charge, context, pdf_path, structure_notes),
        )
    except Exception as exc:
        return ModifierExtraction(unmapped_modifier_notes=[f"Modifier extraction failed ({type(exc).__name__}: {exc}) — not computed."])


def _apply_modifiers(extraction: ChargeExtraction, modifier_result: ModifierExtraction) -> None:
    """Merges the modifier call's findings into the base-rate
    extraction's own ProposedRule(s), in place. Only meaningful for a
    mapped outcome — a bundled/not_present/unmapped charge has no
    ProposedRule to attach a modifier to. When the book varies this
    charge by port, the same modifier list is applied to every port's
    rule — a documented simplification: a modifier's condition (e.g.
    "outside ordinary working hours") is typically charge-wide, not
    port-specific, and this codebase has no evidence yet of a
    port-specific modifier to the contrary."""
    extraction.unmapped_modifier_notes = modifier_result.unmapped_modifier_notes
    if extraction.outcome is not SemanticOutcome.MAPPED or not modifier_result.modifiers:
        return
    if extraction.varies_by_port:
        for rule in extraction.per_port_rules.values():
            rule.modifiers = modifier_result.modifiers
    elif extraction.proposed_rule is not None:
        extraction.proposed_rule.modifiers = modifier_result.modifiers


def _run_tool_rounds(
    charge: CanonicalCharge, context: ChargeContext, pdf_path: str, page_texts: dict[int, str], llm: Any, structure_notes: str = ""
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
        HumanMessage(content=_charge_content(charge, context, pdf_path, structure_notes=structure_notes)),
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
    structure_notes: str = "",
) -> ChargeExtraction:
    leads, tool_results, extra_pages = _run_tool_rounds(charge, context, pdf_path, page_texts, llm, structure_notes)
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
        llm,
        ChargeExtraction,
        EXTRACT_SYSTEM_PROMPT,
        _charge_content(charge, final_context, pdf_path, notes, structure_notes),
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

    # Stage 3's second, independent, best-effort call — never allowed to
    # turn a successful base-rate extraction into a failed charge. Only
    # worth running once there's a mapped rule to attach a modifier to.
    if extraction.outcome is SemanticOutcome.MAPPED:
        modifier_result = _extract_modifiers(charge, context, pdf_path, llm, structure_notes)
        _apply_modifiers(extraction, modifier_result)

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
    structure_notes: str = "",
    log: Callable[[str], None] = lambda msg: None,
) -> tuple[dict[CanonicalCharge, ChargeExtraction], dict[CanonicalCharge, str]]:
    """Charges in `repair_issues_by_charge` get that charge's specific
    validation errors folded into the prompt (§6.5's repair round);
    charges in `verifier_findings_by_charge` get an adversarial challenge
    folded in instead (§6.6's repair round — the two are never expected
    together, since Validate and Verify run at different graph stages).
    Every other charge in `charge_contexts` runs a first-pass extraction.
    Pass a `charge_contexts` containing only the charges to (re-)run to
    repair without redoing already-settled charges.

    One charge's exception (a `structured_call` exhausting its retries,
    most often) no longer kills every other charge in the same batch —
    found live: pipeline.py's own per-charge try/except was built for
    exactly this, but graph.py called this function directly with none,
    so one bad modifier crashed the whole `graph.invoke()` run instead
    of failing just that charge. Caught per charge here instead, so both
    entry points share the same isolation. Returns `(extractions, errors)`
    — `errors` holds only the charges that raised, keyed by charge, value
    is `str(exc)`; a charge that failed has no entry in `extractions`."""
    charges = list(charge_contexts)
    repairs = repair_issues_by_charge or {}
    challenges = verifier_findings_by_charge or {}

    def _call(charge: CanonicalCharge) -> tuple[CanonicalCharge, ChargeExtraction | None, str | None]:
        log(f"{charge.value}: extract starting")
        try:
            extraction = extract_charge(
                charge,
                charge_contexts[charge],
                page_texts,
                llm,
                pdf_path=pdf_path,
                repair_issues=repairs.get(charge),
                verifier_findings=challenges.get(charge),
                structure_notes=structure_notes,
            )
            log(f"{charge.value}: extract done")
            return charge, extraction, None
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            log(f"{charge.value}: extract FAILED — {error}")
            return charge, None, error

    with ThreadPoolExecutor(max_workers=max(1, concurrency_limit)) as pool:
        results = list(pool.map(_call, charges))

    extractions = {charge: extraction for charge, extraction, _ in results if extraction is not None}
    errors = {charge: error for charge, _, error in results if error is not None}
    return extractions, errors
