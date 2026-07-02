from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from market_lens.outcomes.returns import (
    DIRECTION_WINDOW_HOURS,
    compute_returns,
    realized_direction,
)
from market_lens.storage import Event, Outcome

OUTCOME_WINDOWS_HOURS = (1, 4, 24)


def _outcome_fields(session: Session, event: Event, pair: str) -> dict[str, float | str | None]:
    rets = compute_returns(session, pair, event.ts_utc, OUTCOME_WINDOWS_HOURS)
    return {
        "ret_1h": rets[1],
        "ret_4h": rets[4],
        "ret_24h": rets[24],
        "realized_direction": realized_direction(rets[DIRECTION_WINDOW_HOURS]),
    }


def build_outcome(session: Session, event: Event, pair: str) -> Outcome:
    return Outcome(event=event, pair=pair, **_outcome_fields(session, event, pair))


def save_outcome(session: Session, event: Event, pair: str) -> Outcome:
    """Compute and persist the outcome for an event/pair; missing prices become NULL, no crash."""
    outcome = build_outcome(session, event, pair)
    session.add(outcome)
    session.commit()
    return outcome


def upsert_outcome(session: Session, event: Event, pair: str) -> Outcome:
    """Compute the outcome and insert it, or update the existing row for (event, pair)."""
    fields = _outcome_fields(session, event, pair)
    outcome = session.get(Outcome, (event.id, pair))
    if outcome is None:
        outcome = Outcome(event_id=event.id, pair=pair, **fields)
        session.add(outcome)
    else:
        for name, value in fields.items():
            setattr(outcome, name, value)
    return outcome


def compute_all_outcomes(session: Session, pairs: Iterable[str]) -> int:
    """Compute (or refresh) outcomes for every event and pair; return the number written."""
    pairs = list(pairs)
    count = 0
    for event in session.scalars(select(Event)):
        for pair in pairs:
            upsert_outcome(session, event, pair)
            count += 1
    session.commit()
    return count
