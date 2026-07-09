from __future__ import annotations

from pydantic import ValidationError

from market_lens.llm.base import LLMClient
from market_lens.prediction.schema import PredictionOutput


def generate_prediction(llm: LLMClient, prompt: str, *, max_attempts: int = 3) -> PredictionOutput:
    """Ask the LLM for a PredictionOutput, retrying while its JSON fails validation."""
    for attempt in range(1, max_attempts + 1):
        try:
            return llm.structured(prompt, PredictionOutput)
        except ValidationError:
            if attempt == max_attempts:
                raise
    raise AssertionError("unreachable")
