from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from market_lens.storage import Event, Outcome, Prediction


@dataclass(frozen=True)
class MeasurementRow:
    """A prediction joined to its realized outcome for one event and pair."""

    event_id: int
    model: str
    pair: str
    ts_utc: datetime
    direction: str  # predicted direction
    score: float
    confidence: float
    surprise: float | None
    realized_direction: str | None
    ret_1h: float | None
    ret_4h: float | None
    ret_24h: float | None


def build_frame(session: Session, *, pair: str, model: str | None = None) -> list[MeasurementRow]:
    """Join predictions to outcomes on event_id for one pair; only measurable events remain."""
    stmt = (
        select(Prediction, Outcome, Event.surprise)
        .join(Outcome, Outcome.event_id == Prediction.event_id)
        .join(Event, Event.id == Prediction.event_id)
        .where(Outcome.pair == pair)
    )
    if model is not None:
        stmt = stmt.where(Prediction.model == model)

    rows = []
    for prediction, outcome, surprise in session.execute(stmt):
        rows.append(
            MeasurementRow(
                event_id=prediction.event_id,
                model=prediction.model,
                pair=outcome.pair,
                ts_utc=prediction.ts_utc,
                direction=prediction.direction,
                score=prediction.score,
                confidence=prediction.confidence,
                surprise=surprise,
                realized_direction=outcome.realized_direction,
                ret_1h=outcome.ret_1h,
                ret_4h=outcome.ret_4h,
                ret_24h=outcome.ret_24h,
            )
        )
    return rows
