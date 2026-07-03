from __future__ import annotations

from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from tenacity.wait import wait_base

from market_lens.llm.base import LLMClient, RateLimitError


class RetryingLLMClient(LLMClient):
    def __init__(
        self, inner: LLMClient, *, max_attempts: int = 5, wait: wait_base | None = None
    ) -> None:
        self._inner = inner
        self._retrying = Retrying(
            retry=retry_if_exception_type(RateLimitError),
            stop=stop_after_attempt(max_attempts),
            wait=wait if wait is not None else wait_exponential(multiplier=1, max=30),
            reraise=True,
        )

    def complete(self, prompt: str, *, temperature: float = 0.0) -> str:
        return self._retrying(self._inner.complete, prompt, temperature=temperature)
