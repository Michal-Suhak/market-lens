from __future__ import annotations

from groq import Groq
from groq import RateLimitError as GroqRateLimitError

from market_lens.llm.base import LLMClient, RateLimitError

GROQ_MODEL = "llama-3.3-70b-versatile"  # swap for another Groq model if quality/limits change


class GroqClient(LLMClient):
    def __init__(
        self,
        api_key: str,
        *,
        model: str = GROQ_MODEL,
        temperature: float = 0.0,
        client: Groq | None = None,
    ):
        self._model = model
        self._temperature = temperature
        self._client = client if client is not None else Groq(api_key=api_key)

    @property
    def model(self) -> str:
        return self._model

    def complete(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._temperature,
            )
        except GroqRateLimitError as exc:
            raise RateLimitError(str(exc)) from exc
        return response.choices[0].message.content
