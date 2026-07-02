from __future__ import annotations

from sqlalchemy.orm import Session

from market_lens.outcomes.returns import (
    DIRECTION_WINDOW_HOURS,
    compute_returns,
    realized_direction,
)
from market_lens.storage import Event, Outcome

OUTCOME_WINDOWS_HOURS = (1, 4, 24)


def build_outcome(session: Session, event: Event, pair: str) -> Outcome:
    rets = compute_returns(session, pair, event.ts_utc, OUTCOME_WINDOWS_HOURS)
    return Outcome(
        event=event,
        pair=pair,
        ret_1h=rets[1],
        ret_4h=rets[4],
        ret_24h=rets[24],
        realized_direction=realized_direction(rets[DIRECTION_WINDOW_HOURS]),
    )


def save_outcome(session: Session, event: Event, pair: str) -> Outcome:
    """Compute and persist the outcome for an event/pair; missing prices become NULL, no crash."""
    outcome = build_outcome(session, event, pair)
    session.add(outcome)
    session.commit()
    return outcome
