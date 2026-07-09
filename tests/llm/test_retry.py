import pytest
from tenacity import wait_none

from market_lens.llm.base import LLMClient, RateLimitError
from market_lens.llm.retry import RetryingLLMClient


class _FlakyClient(LLMClient):
    def __init__(self, fail_times: int, response: str = "ok"):
        self._fail_times = fail_times
        self._response = response
        self.calls = 0

    def complete(self, prompt: str) -> str:
        self.calls += 1
        if self.calls <= self._fail_times:
            raise RateLimitError("429")
        return self._response


class _RecordingClient(LLMClient):
    def __init__(self, response: str = "ok"):
        self._response = response
        self.received: list[str] = []

    def complete(self, prompt: str) -> str:
        self.received.append(prompt)
        return self._response


class _AuthErrorClient(LLMClient):
    def __init__(self):
        self.calls = 0

    def complete(self, prompt: str) -> str:
        self.calls += 1
        raise ValueError("bad credentials")


def test_succeeds_on_first_try_without_retrying():
    inner = _FlakyClient(fail_times=0)
    client = RetryingLLMClient(inner, wait=wait_none())

    assert client.complete("p") == "ok"
    assert inner.calls == 1


def test_retries_on_rate_limit_then_succeeds():
    inner = _FlakyClient(fail_times=2)
    client = RetryingLLMClient(inner, max_attempts=5, wait=wait_none())

    assert client.complete("predict") == "ok"
    assert inner.calls == 3


def test_returns_inner_value_after_retry():
    inner = _FlakyClient(fail_times=1, response="hawkish")
    client = RetryingLLMClient(inner, max_attempts=3, wait=wait_none())

    assert client.complete("p") == "hawkish"


def test_forwards_prompt_to_inner():
    inner = _RecordingClient()
    client = RetryingLLMClient(inner, wait=wait_none())

    client.complete("read the statement")

    assert inner.received == ["read the statement"]


def test_succeeds_on_the_last_allowed_attempt():
    inner = _FlakyClient(fail_times=2)
    client = RetryingLLMClient(inner, max_attempts=3, wait=wait_none())

    assert client.complete("p") == "ok"
    assert inner.calls == 3


def test_reraises_rate_limit_after_exhausting_attempts():
    inner = _FlakyClient(fail_times=10)
    client = RetryingLLMClient(inner, max_attempts=3, wait=wait_none())

    with pytest.raises(RateLimitError):
        client.complete("predict")

    assert inner.calls == 3


def test_retries_exactly_max_attempts_times():
    inner = _FlakyClient(fail_times=100)
    client = RetryingLLMClient(inner, max_attempts=4, wait=wait_none())

    with pytest.raises(RateLimitError):
        client.complete("p")

    assert inner.calls == 4


def test_max_attempts_one_does_not_retry():
    inner = _FlakyClient(fail_times=1)
    client = RetryingLLMClient(inner, max_attempts=1, wait=wait_none())

    with pytest.raises(RateLimitError):
        client.complete("p")

    assert inner.calls == 1


def test_non_rate_limit_error_is_not_retried():
    inner = _AuthErrorClient()
    client = RetryingLLMClient(inner, max_attempts=5, wait=wait_none())

    with pytest.raises(ValueError):
        client.complete("predict")

    assert inner.calls == 1
