from __future__ import annotations

from google import genai
from google.genai import types
from google.genai.errors import ClientError

from market_lens.llm.base import LLMClient, RateLimitError

GEMINI_MODEL = "gemini-2.5-flash"  # swap for another Gemini model if quality/limits change


class GeminiClient(LLMClient):
    def __init__(
        self,
        api_key: str,
        *,
        model: str = GEMINI_MODEL,
        temperature: float = 0.0,
        client: genai.Client | None = None,
    ):
        self._model = model
        self._temperature = temperature
        self._client = client if client is not None else genai.Client(api_key=api_key)

    def complete(self, prompt: str) -> str:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=self._temperature),
            )
        except ClientError as exc:
            if exc.code == 429:
                raise RateLimitError(str(exc)) from exc
            raise
        return response.text
