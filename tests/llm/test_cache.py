from market_lens.llm.base import LLMClient
from market_lens.llm.cache import CachingLLMClient, InMemoryLlmCache, SqlLlmCache, cache_key


class _CountingClient(LLMClient):
    def __init__(self, response: str):
        self._response = response
        self.calls = 0

    def complete(self, prompt: str, *, temperature: float = 0.0) -> str:
        self.calls += 1
        return self._response


class _SequenceClient(LLMClient):
    def __init__(self):
        self.calls = 0

    def complete(self, prompt: str, *, temperature: float = 0.0) -> str:
        self.calls += 1
        return f"response-{self.calls}"


def test_second_identical_call_hits_cache():
    inner = _CountingClient("hawkish")
    client = CachingLLMClient(inner, InMemoryLlmCache())

    first = client.complete("read this statement")
    second = client.complete("read this statement")

    assert first == second == "hawkish"
    assert inner.calls == 1


def test_cache_returns_the_first_response_not_a_fresh_one():
    inner = _SequenceClient()
    client = CachingLLMClient(inner, InMemoryLlmCache())

    first = client.complete("p")
    second = client.complete("p")

    assert first == "response-1"
    assert second == "response-1"
    assert inner.calls == 1


def test_different_prompt_is_a_cache_miss():
    inner = _CountingClient("x")
    client = CachingLLMClient(inner, InMemoryLlmCache())

    client.complete("a")
    client.complete("b")

    assert inner.calls == 2


def test_different_temperature_is_a_cache_miss():
    inner = _CountingClient("x")
    client = CachingLLMClient(inner, InMemoryLlmCache())

    client.complete("p", temperature=0.0)
    client.complete("p", temperature=0.7)

    assert inner.calls == 2


def test_distinct_prompts_are_cached_independently():
    inner = _SequenceClient()
    client = CachingLLMClient(inner, InMemoryLlmCache())

    a1 = client.complete("a")
    b1 = client.complete("b")
    a2 = client.complete("a")

    assert a1 == "response-1"
    assert b1 == "response-2"
    assert a2 == "response-1"
    assert inner.calls == 2


def test_caching_with_sql_backend_persists_the_hit(db_session):
    inner = _CountingClient("dovish")
    client = CachingLLMClient(inner, SqlLlmCache(db_session))

    client.complete("statement")
    client.complete("statement")

    assert inner.calls == 1


def test_cache_persists_across_client_instances(db_session):
    first_run = _CountingClient("cached-answer")
    CachingLLMClient(first_run, SqlLlmCache(db_session)).complete("p")
    assert first_run.calls == 1

    second_run = _CountingClient("would-be-new-answer")
    result = CachingLLMClient(second_run, SqlLlmCache(db_session)).complete("p")

    assert result == "cached-answer"
    assert second_run.calls == 0


def test_sql_cache_get_set_and_overwrite(db_session):
    cache = SqlLlmCache(db_session)

    assert cache.get("k") is None
    cache.set("k", "v")
    assert cache.get("k") == "v"
    cache.set("k", "v2")
    assert cache.get("k") == "v2"


def test_cache_key_is_stable_for_same_input():
    assert cache_key("prompt", 0.0) == cache_key("prompt", 0.0)


def test_cache_key_differs_for_prompt_and_temperature():
    assert cache_key("a", 0.0) != cache_key("b", 0.0)
    assert cache_key("a", 0.0) != cache_key("a", 0.5)
