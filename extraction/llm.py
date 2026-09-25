"""LLM client factory and a small structured-call helper, mirroring
tariffs.nlp's pattern: dependency-injectable so tests pass a stub
instead of making a real API call (specs/EXTRACTION_SPEC.md §9 — pipeline
tests must not require network access or an API key).
"""

from __future__ import annotations

import time
from typing import Any, Type, TypeVar

from pydantic import BaseModel

DEFAULT_MODEL = "gpt-6-luna"  # OpenAI, not Anthropic — a deliberate, extraction-only cost
# choice (~20x cheaper per token than Claude Sonnet 5); the calculator's own LLM calls
# (tariffs/nlp.py) are unaffected and stay on langchain-anthropic. Needs OPENAI_API_KEY,
# not ANTHROPIC_API_KEY, in the environment.
DEFAULT_REQUEST_TIMEOUT_SECONDS = 120  # ChatOpenAI's own default is None — unbounded — and a
# stalled connection (observed live on the Anthropic client this replaced: a seeded-error
# eval run sat on one open TCP connection for 58 minutes doing nothing) then hangs forever
# instead of failing loudly.

T = TypeVar("T", bound=BaseModel)


def default_llm(model: str = DEFAULT_MODEL, timeout: float = DEFAULT_REQUEST_TIMEOUT_SECONDS) -> Any:
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model=model, timeout=timeout)


MAX_STRUCTURED_CALL_ATTEMPTS = 3
MAX_RATE_LIMIT_RETRIES = 3
RATE_LIMIT_BACKOFF_SECONDS = 15  # doubles each retry: 15s, 30s, 60s


def _is_rate_limit_error(exc: Exception) -> bool:
    """Provider-agnostic by design: both openai's and anthropic's SDKs
    set `status_code` on their own API error classes — checked by
    attribute, not by importing either SDK's specific exception type
    here (extraction/llm.py stays provider-agnostic everywhere else)."""
    return getattr(exc, "status_code", None) == 429


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

    Also retries, with exponential backoff, on a 429 rate-limit response
    (observed live on GPT-6 Luna: several charges extracting in parallel
    burst past the account's tokens-per-minute limit) — a separate
    budget from `MAX_STRUCTURED_CALL_ATTEMPTS`, since waiting out a rate
    limit isn't a schema-validation attempt and shouldn't consume one.
    """
    from langchain_core.messages import HumanMessage, SystemMessage
    from pydantic import ValidationError

    # method="function_calling", not the provider default: OpenAI's own
    # default (the newer strict "json_schema" mode) rejects any
    # dynamically-keyed dict field outright (found live: both
    # ProposedRule.pricing_params and ChargeExtraction.per_port_rules
    # are exactly this shape) — every object in that mode must have a
    # fixed, enumerable set of property names. "function_calling" is
    # the older, looser mode both providers support, and is already
    # ChatAnthropic's own default — this makes OpenAI behave the same
    # way Claude always has in this project, not a new compromise.
    # Pydantic still validates the response either way (ValidationError
    # below still retries), just without the API also constraining
    # generation itself.
    structured_llm = llm.with_structured_output(schema, method="function_calling")
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

    last_error: Exception | None = None
    rate_limit_retries = 0
    attempts = 0
    while attempts < MAX_STRUCTURED_CALL_ATTEMPTS:
        try:
            return structured_llm.invoke(messages)
        except ValidationError as exc:
            last_error = exc
            attempts += 1
        except Exception as exc:
            if not _is_rate_limit_error(exc) or rate_limit_retries >= MAX_RATE_LIMIT_RETRIES:
                raise
            rate_limit_retries += 1
            time.sleep(RATE_LIMIT_BACKOFF_SECONDS * (2 ** (rate_limit_retries - 1)))
    raise last_error
