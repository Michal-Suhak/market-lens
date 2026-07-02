from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from market_lens.storage import Price

DEFAULT_TOLERANCE = timedelta(minutes=1)


def get_mid_price(
    session: Session, pair: str, ts: datetime, *, tolerance: timedelta = DEFAULT_TOLERANCE
) -> float | None:
    """Mid (close) price for pair nearest to ts within tolerance; None when no bar is that close."""
    bars = session.scalars(
        select(Price).where(
            Price.pair == pair,
            Price.ts_utc >= ts - tolerance,
            Price.ts_utc <= ts + tolerance,
        )
    ).all()
    if not bars:
        return None
    return min(bars, key=lambda bar: abs(bar.ts_utc - ts)).close
