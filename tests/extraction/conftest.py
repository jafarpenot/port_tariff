"""Shared LLM stub for extraction pipeline tests — no real Anthropic API
calls, no ANTHROPIC_API_KEY needed (specs/EXTRACTION_SPEC.md §9).

Unlike tariffs/nlp.py's tests (one call per test), Map/Extract issue
several structured-output calls per run, sometimes concurrently
(ThreadPoolExecutor) — order is not guaranteed, so the stub must route
each call by its *content*, not by call sequence.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Callable

import pypdf


def make_blank_pdf(n_pages: int = 30) -> str:
    """A real, on-disk PDF with enough pages for any test's Map/Extract
    page-slicing to succeed. Content is irrelevant — the LLM is
    stubbed — only page *count* matters, since extraction/pdf.py's
    extract_pdf_pages() needs real bytes to slice from regardless of
    which page numbers a test's synthetic page_texts/WindowSection data
    references. Written once per test session to a fixed temp path
    (idempotent — skips rewriting if already there), not regenerated
    per test."""
    path = Path(tempfile.gettempdir()) / "port_tariff_test_fixture.pdf"
    if not path.exists():
        writer = pypdf.PdfWriter()
        for _ in range(n_pages):
            writer.add_blank_page(width=600, height=800)
        with open(path, "wb") as f:
            writer.write(f)
    return str(path)


def text_of(content) -> str:
    """The text portion of a message's content, whether it's a plain
    string (Identity/Verify's calls, unchanged) or the multimodal list
    [{"type": "text", ...}, {"type": "file", ...}] Map/Extract now send
    (extraction/map_node.py, extraction/extract.py) — so a test can keep
    checking substrings without caring which shape it got."""
    if isinstance(content, str):
        return content
    return "\n".join(block["text"] for block in content if isinstance(block, dict) and block.get("type") == "text")


class _StubStructuredLLM:
    def __init__(self, respond: Callable, schema):
        self._respond = respond
        self._schema = schema

    def invoke(self, messages):
        return self._respond(self._schema, messages)


class _StubToolLLM:
    def __init__(self, tool_respond: Callable, tools):
        self._tool_respond = tool_respond
        self._tools = tools

    def invoke(self, messages):
        return self._tool_respond(self._tools, messages)


class StubChatModel:
    """`.with_structured_output(schema).invoke(messages)` — the same
    minimal surface tariffs/nlp.py's tests stub — but `respond` gets the
    schema and the full message list, so a test can return a different
    canned object per call based on what's actually being asked.

    `tool_respond(tools, messages) -> AIMessage` additionally stubs
    `.bind_tools(tools).invoke(messages)` for Extract's tool-calling
    rounds (extraction/extract.py). Defaults to "never call a tool" —
    most tests don't exercise the lead-following path at all.
    """

    def __init__(self, respond: Callable, tool_respond: Callable | None = None):
        self._respond = respond
        self._tool_respond = tool_respond or (lambda tools, messages: _NoToolCalls())

    def with_structured_output(self, schema, **kwargs):
        # **kwargs (e.g. `method=`) accepted and ignored, matching real
        # providers' signatures — extraction/llm.py's structured_call()
        # passes method="function_calling" explicitly.
        return _StubStructuredLLM(self._respond, schema)

    def bind_tools(self, tools):
        return _StubToolLLM(self._tool_respond, tools)


class _NoToolCalls:
    tool_calls: list = []
