from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# How the LLM reads the statement's monetary-policy stance:
#   hawkish - leaning to tighter policy (rate hikes, fighting inflation) -> usually USD-positive
#   dovish  - leaning to looser policy (rate cuts, supporting growth) -> usually USD-negative
#   neutral - balanced, no clear lean
Tone = Literal["hawkish", "dovish", "neutral"]

# Predicted move of the reference pair (e.g. EUR/USD) in the hours after the release:
#   up   - the pair rises (base currency strengthens vs USD)
#   down - the pair falls
#   flat - no meaningful move
Direction = Literal["up", "down", "flat"]


class PredictionOutput(BaseModel):
    tone: Tone
    direction: Direction
    confidence: float = Field(ge=0.0, le=1.0)
    score: float = Field(ge=-1.0, le=1.0)  # signed conviction: -1 strong down, +1 strong up
