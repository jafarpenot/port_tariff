"""LLM client factory and a small structured-call helper, mirroring
tariffs.nlp's pattern: dependency-injectable so tests pass a stub
instead of making a real API call (specs/EXTRACTION_SPEC.md §9 — pipeline
tests must not require network access or an API key).
"""

from __future__ import annotations

from typing import Any, Type, TypeVar

from pydantic import BaseModel

DEFAULT_MODEL = "claude-sonnet-5"
DEFAULT_REQUEST_TIMEOUT_SECONDS = 120  # ChatAnthropic's own default is None — unbounded — and a
# stalled connection (observed live: a seeded-error eval run sat on one open TCP connection for
# 58 minutes doing nothing) then hangs forever instead of failing loudly.

T = TypeVar("T", bound=BaseModel)


def default_llm(model: str = DEFAULT_MODEL, timeout: float = DEFAULT_REQUEST_TIMEOUT_SECONDS) -> Any:
    from langchain_anthropic import ChatAnthropic

    # No `temperature` argument: newer Claude models (e.g. claude-sonnet-5)
    # reject it outright — see tariffs/nlp.py's _default_llm for the same note.
    return ChatAnthropic(model=model, timeout=timeout)


MAX_STRUCTURED_CALL_ATTEMPTS = 3


def structured_call(llm: Any, schema: Type[T], system_prompt: str, user_prompt: str) -> T:
    """One structured-output call: system + user message in, a validated
    instance of `schema` out. A stub `llm` for tests only needs to
    implement `.with_structured_output(schema).invoke(messages)` —
    the same minimal surface tariffs/nlp.py's tests already stub.

    Retries on a schema-validation failure (observed live: the model
    occasionally wraps its answer in a spurious extra key, or returns a
    string where a list was asked for) — this is API-call flakiness, not
    a business-logic problem, so it's handled here rather than pushed up
    into every node or conflated with Validate's charge-level repair
    loop. A stub LLM's `respond` callable is invoked once per attempt if
    it keeps failing, same as a real flaky model would be re-asked.
    """
    from langchain_core.messages import HumanMessage, SystemMessage
    from pydantic import ValidationError

    structured_llm = llm.with_structured_output(schema)
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

    last_error: Exception | None = None
    for _ in range(MAX_STRUCTURED_CALL_ATTEMPTS):
        try:
            return structured_llm.invoke(messages)
        except ValidationError as exc:
            last_error = exc
    raise last_error
