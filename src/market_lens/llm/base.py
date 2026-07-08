from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class RateLimitError(Exception):
    """Raised by a provider when the API reports rate limiting (HTTP 429)."""


class LLMClient(ABC):
    @property
    def model(self) -> str:
        return "unknown"

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Return the model's raw text response for a prompt."""

    def structured(self, prompt: str, schema: type[T]) -> T:
        """Parse and validate the model's JSON response into an instance of schema."""
        return schema.model_validate_json(self.complete(prompt))
