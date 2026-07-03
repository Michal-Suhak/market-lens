from __future__ import annotations

import hashlib
from typing import Protocol

from sqlalchemy.orm import Session

from market_lens.llm.base import LLMClient
from market_lens.storage import LlmCacheEntry


class LLMCache(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str) -> None: ...


class InMemoryLlmCache:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def set(self, key: str, value: str) -> None:
        self._store[key] = value


class SqlLlmCache:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, key: str) -> str | None:
        entry = self._session.get(LlmCacheEntry, key)
        return entry.value if entry is not None else None

    def set(self, key: str, value: str) -> None:
        entry = self._session.get(LlmCacheEntry, key)
        if entry is None:
            self._session.add(LlmCacheEntry(key=key, value=value))
        else:
            entry.value = value
        self._session.commit()


def cache_key(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()


class CachingLLMClient(LLMClient):
    def __init__(self, inner: LLMClient, cache: LLMCache) -> None:
        self._inner = inner
        self._cache = cache

    def complete(self, prompt: str) -> str:
        key = cache_key(prompt)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        value = self._inner.complete(prompt)
        self._cache.set(key, value)
        return value
