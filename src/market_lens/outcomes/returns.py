from __future__ import annotations

import math
from collections.abc import Iterable
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from market_lens.outcomes.mid_price import DEFAULT_TOLERANCE, get_mid_price
from market_lens.utils import add_hours

DIRECTION_WINDOW_HOURS = 1  # realized_direction is taken from the 1h return


def log_return(price_t0: float | None, price_t1: float | None) -> float | None:
    if price_t0 is None or price_t1 is None:
        return None
    return math.log(price_t1 / price_t0)


def realized_direction(ret: float | None) -> str | None:
    if ret is None:
        return None
    if ret > 0:
        return "up"
    if ret < 0:
        return "down"
    return "flat"


def compute_returns(
    session: Session,
    pair: str,
    t0: datetime,
    windows_hours: Iterable[int],
    *,
    tolerance: timedelta = DEFAULT_TOLERANCE,
) -> dict[int, float | None]:
    """Log return from t0 to t0+h for each window h; a value is None if either price is missing."""
    price_t0 = get_mid_price(session, pair, t0, tolerance=tolerance)
    return {
        hours: log_return(
            price_t0, get_mid_price(session, pair, add_hours(t0, hours), tolerance=tolerance)
        )
        for hours in windows_hours
    }
