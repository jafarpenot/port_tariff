"""Shared LLM stub for extraction pipeline tests — no real Anthropic API
calls, no ANTHROPIC_API_KEY needed (specs/EXTRACTION_SPEC.md §9).

Unlike tariffs/nlp.py's tests (one call per test), Map/Extract issue
several structured-output calls per run, sometimes concurrently
(ThreadPoolExecutor) — order is not guaranteed, so the stub must route
each call by its *content*, not by call sequence.
"""

from __future__ import annotations

from typing import Callable


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

    def with_structured_output(self, schema):
        return _StubStructuredLLM(self._respond, schema)

    def bind_tools(self, tools):
        return _StubToolLLM(self._tool_respond, tools)


class _NoToolCalls:
    tool_calls: list = []
