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
MAX_TRANSIENT_ERROR_RETRIES = 3
TRANSIENT_ERROR_BACKOFF_SECONDS = 15  # doubles each retry: 15s, 30s, 60s


def _is_transient_error(exc: Exception) -> bool:
    """Provider-agnostic by design, two different ways for two different
    error shapes. A 429 rate limit: both openai's and anthropic's SDKs
    set `status_code` on their own API error classes — checked by
    attribute, not either SDK's specific exception type. A timeout:
    found live (a 28-minute run died on one call that outlasted
    DEFAULT_REQUEST_TIMEOUT_SECONDS) — this never got an HTTP response
    at all, so it has no status_code; langchain_core.exceptions.
    ModelTimeoutError is the taxonomy both providers' wrappers use for
    exactly this, so checking that stays provider-agnostic too."""
    from langchain_core.exceptions import ModelTimeoutError

    return getattr(exc, "status_code", None) == 429 or isinstance(exc, ModelTimeoutError)


def structured_call(llm: Any, schema: Type[T], system_prompt: str, user_prompt: str | list) -> T:
    """One structured-output call: system + user message in, a validated
    instance of `schema` out. `user_prompt` is usually plain text, but
    Map/Extract pass a list of content blocks (langchain_core's standard
    multimodal shape — a text block plus a `{"type": "file", ...}` PDF
    attachment) to send real PDF pages instead of flattened text;
    HumanMessage.content accepts either natively, so nothing else here
    needs to know or care which one it got.

    A stub `llm` for tests only needs to implement
    `.with_structured_output(schema).invoke(messages)` — the same
    minimal surface tariffs/nlp.py's tests already stub.

    Retries on a schema-validation failure (observed live: the model
    occasionally wraps its answer in a spurious extra key, or returns a
    string where a list was asked for) — this is API-call flakiness, not
    a business-logic problem, so it's handled here rather than pushed up
    into every node or conflated with Validate's charge-level repair
    loop. A stub LLM's `respond` callable is invoked once per attempt if
    it keeps failing, same as a real flaky model would be re-asked.

    Each retry after a `ValidationError` appends the exact validation
    error to the conversation before re-asking — found live: without
    this, a retry was a blind re-roll of the same messages, hoping for a
    different answer by chance (confirmed: a modifier the model had
    already read correctly still failed pydantic's "exactly one of
    adjustment_percentage/adjustment_flat_amount/raw_description" check
    on all 3 attempts, because it was never told which of the three
    conditions it violated). Feeding the error back turns each retry
    into an actual correction attempt instead.

    Also retries, with exponential backoff, on a transient error — a 429
    rate limit (several charges extracting in parallel burst past the
    account's tokens-per-minute limit) or a request timeout (one call
    outlasted DEFAULT_REQUEST_TIMEOUT_SECONDS and killed a 28-minute run
    outright) — a separate budget from `MAX_STRUCTURED_CALL_ATTEMPTS`,
    since waiting out either isn't a schema-validation attempt and
    shouldn't consume one.
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
    transient_retries = 0
    attempts = 0
    while attempts < MAX_STRUCTURED_CALL_ATTEMPTS:
        try:
            return structured_llm.invoke(messages)
        except ValidationError as exc:
            last_error = exc
            attempts += 1
            if attempts < MAX_STRUCTURED_CALL_ATTEMPTS:
                messages.append(
                    HumanMessage(
                        content=(
                            "Your previous answer failed schema validation with this error:\n"
                            f"{exc}\n\n"
                            "Correct the problem and send a complete, valid answer — don't "
                            "just describe the fix, produce the corrected structured output."
                        )
                    )
                )
        except Exception as exc:
            if not _is_transient_error(exc) or transient_retries >= MAX_TRANSIENT_ERROR_RETRIES:
                raise
            transient_retries += 1
            time.sleep(TRANSIENT_ERROR_BACKOFF_SECONDS * (2 ** (transient_retries - 1)))
    raise last_error
