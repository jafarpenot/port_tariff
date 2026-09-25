"""extraction/llm.py's structured_call(): the rate-limit retry-with-backoff
added after a live 429 on GPT-6 Luna. No real API calls — a stub LLM
raises a fake 429-shaped exception, and time.sleep is monkeypatched so
the test doesn't actually wait out the backoff.
"""

from pydantic import BaseModel

from extraction.llm import MAX_RATE_LIMIT_RETRIES, structured_call


class _Answer(BaseModel):
    value: int


class _FakeRateLimitError(Exception):
    """Mirrors what openai.RateLimitError/anthropic.RateLimitError both
    set: a `status_code` attribute, which is all structured_call() checks —
    provider-agnostic on purpose, no real SDK exception imported here."""

    status_code = 429


class _StubStructuredLLM:
    def __init__(self, respond):
        self._respond = respond

    def invoke(self, messages):
        return self._respond()


class _StubLLM:
    def __init__(self, respond):
        self._respond = respond

    def with_structured_output(self, schema, **kwargs):
        return _StubStructuredLLM(self._respond)


def test_retries_after_a_rate_limit_error_and_then_succeeds(monkeypatch):
    sleeps = []
    monkeypatch.setattr("extraction.llm.time.sleep", lambda seconds: sleeps.append(seconds))

    calls = {"n": 0}

    def respond():
        calls["n"] += 1
        if calls["n"] == 1:
            raise _FakeRateLimitError()
        return _Answer(value=42)

    result = structured_call(_StubLLM(respond), _Answer, "system", "user")
    assert result.value == 42
    assert calls["n"] == 2
    assert sleeps == [15]  # first backoff


def test_backoff_doubles_on_each_retry(monkeypatch):
    sleeps = []
    monkeypatch.setattr("extraction.llm.time.sleep", lambda seconds: sleeps.append(seconds))

    def respond():
        raise _FakeRateLimitError()

    try:
        structured_call(_StubLLM(respond), _Answer, "system", "user")
    except _FakeRateLimitError:
        pass
    assert sleeps == [15, 30, 60][:MAX_RATE_LIMIT_RETRIES]


def test_rate_limit_retries_are_exhausted_and_then_the_error_propagates(monkeypatch):
    monkeypatch.setattr("extraction.llm.time.sleep", lambda seconds: None)

    def respond():
        raise _FakeRateLimitError()

    try:
        structured_call(_StubLLM(respond), _Answer, "system", "user")
        assert False, "expected _FakeRateLimitError to propagate"
    except _FakeRateLimitError:
        pass


def test_a_non_rate_limit_error_propagates_immediately_no_retry():
    def respond():
        raise RuntimeError("not a rate limit")

    try:
        structured_call(_StubLLM(respond), _Answer, "system", "user")
        assert False, "expected RuntimeError to propagate"
    except RuntimeError:
        pass
