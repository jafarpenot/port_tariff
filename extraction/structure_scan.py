"""Node 1 — Structure scan. LLM, bounded tool-calling loop, before
anything else runs.

Three phases, the same tool-calling pattern already proven in
`extraction/extract.py`'s `_run_tool_rounds()` (a `llm.bind_tools([...])`
loop, a bounded round count, `ToolMessage` round-trip):

1. One native-PDF pass — the original single-shot read, unchanged
   mechanism: the whole document attached natively, asked for a first
   impression (organisation, table of contents, layout oddities).
2. A bounded exploration round: the model samples a handful of specific
   pages via `read_pages` (cheap, text-only — the same tools Extract's
   own lead-following loop uses, over `split_pdf()`'s own page texts,
   computed here rather than threaded in from Split, since this node
   still runs before Split in the graph) to validate or correct its own
   page-offset hypothesis, then confirms each claimed section by reading
   its first page(s) and tagging what's actually there.
3. A final structured call folding the exploration transcript into a
   `StructureScanResult` — the verified section map Stage 2's Map node
   can act on, gated by each section's own `confidence`.

Computing `page_texts` locally here (rather than depending on Split's
own output) duplicates a cheap, local, non-LLM parse — `split_pdf()` has
no network call and no meaningful cost — in exchange for not reordering
the graph's human-approval/resume-sensitive node sequence.

Stays strictly advisory exactly as before: Identity/Map/Extract/Verify
treat `structure_notes` (this result's free-text `notes` field) as
background context, never ground truth. The one real change from the
original single-shot version: a high-confidence `ScannedSection` is now
trustworthy enough — because it was actually confirmed by reading a
page, not merely guessed from a table of contents — to let Map (Stage 2)
change its own behaviour, not just its prose.
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from .llm import structured_call
from .pdf import split_pdf
from .prompts import (
    STRUCTURE_SCAN_EXPLORATION_SYSTEM_PROMPT,
    STRUCTURE_SCAN_FINAL_SYSTEM_PROMPT,
    STRUCTURE_SCAN_SYSTEM_PROMPT,
)
from .schemas import StructureScanResult
from .tools import make_tools

MAX_EXPLORATION_ROUNDS = 6  # bounded: page-offset validation + section confirmation together,
# same "bounded, cheap, stop as soon as confident" shape as extract.py's MAX_LEAD_ROUNDS.


def _initial_impression(pdf_path: str, llm: Any) -> str:
    """The original single-shot native-PDF pass — a cheap first
    hypothesis, better to seed the exploration round with than nothing:
    deciding which pages are worth sampling requires some starting
    guess about where things are."""
    pdf_bytes = Path(pdf_path).read_bytes()
    b64 = base64.b64encode(pdf_bytes).decode()
    content = [
        {"type": "text", "text": "The full port tariff book is attached as a PDF."},
        {"type": "file", "source_type": "base64", "mime_type": "application/pdf", "data": b64, "filename": "document.pdf"},
    ]
    return structured_call(llm, StructureScanResult, STRUCTURE_SCAN_SYSTEM_PROMPT, content).notes


def _run_exploration_rounds(impression: str, page_texts: dict[int, str], llm: Any) -> list[str]:
    """Returns the tool results as plain text, folded into the final
    structured_call's context — this loop's own output is never the
    final answer, the same separation extract.py's tool round already
    uses (a tool round and the final structured-output call are two
    separate, disconnected model calls)."""
    tools = make_tools(page_texts)
    tools_by_name = {t.name: t for t in tools}
    tool_llm = llm.bind_tools(tools)

    messages = [
        SystemMessage(content=STRUCTURE_SCAN_EXPLORATION_SYSTEM_PROMPT),
        HumanMessage(content=f"Your first-glance impression of this document:\n\n{impression}"),
    ]
    tool_results: list[str] = []
    for _ in range(MAX_EXPLORATION_ROUNDS):
        response = tool_llm.invoke(messages)
        tool_calls = getattr(response, "tool_calls", None)
        if not tool_calls:
            break
        messages.append(response)
        for call in tool_calls:
            tool_obj = tools_by_name.get(call["name"])
            result = tool_obj.invoke(call["args"]) if tool_obj is not None else f"Unknown tool: {call['name']}"
            tool_results.append(f"{call['name']}({call['args']}) -> {result}")
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    return tool_results


def scan_structure(pdf_path: str, llm: Any) -> StructureScanResult:
    page_texts = split_pdf(pdf_path)
    impression = _initial_impression(pdf_path, llm)
    tool_results = _run_exploration_rounds(impression, page_texts, llm)

    transcript = f"First-glance impression:\n{impression}"
    if tool_results:
        transcript += "\n\nWhat was actually confirmed by reading specific pages:\n" + "\n\n".join(tool_results)
    else:
        transcript += "\n\nNo pages were read to check this impression — nothing below should be marked high confidence."

    return structured_call(llm, StructureScanResult, STRUCTURE_SCAN_FINAL_SYSTEM_PROMPT, transcript)


def notes_with_glossary(result: StructureScanResult) -> str:
    """Stage 4: folds `result.glossary` into the single advisory string
    every other node already threads as `structure_notes` — deliberately
    not a second parallel parameter through Identity/Map/Extract's ~10
    call sites, since a glossary is exactly the same kind of thing
    (advisory, never ground truth) `structure_notes` already is."""
    if not result.glossary:
        return result.notes
    return result.notes + "\n\n---\nGlossary of terms defined in this book:\n" + result.glossary
