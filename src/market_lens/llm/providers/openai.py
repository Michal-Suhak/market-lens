from __future__ import annotations

from openai import OpenAI
from openai import RateLimitError as OpenAIRateLimitError

from market_lens.llm.base import LLMClient, RateLimitError

OPENAI_MODEL = "gpt-4o-mini"  # swap for another OpenAI model if quality/cost changes


class OpenAIClient(LLMClient):
    def __init__(
        self,
        api_key: str,
        *,
        model: str = OPENAI_MODEL,
        temperature: float = 0.0,
        client: OpenAI | None = None,
    ):
        self._model = model
        self._temperature = temperature
        self._client = client if client is not None else OpenAI(api_key=api_key)

    def complete(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._temperature,
            )
        except OpenAIRateLimitError as exc:
            raise RateLimitError(str(exc)) from exc
        return response.choices[0].message.content
