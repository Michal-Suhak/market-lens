from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from market_lens.storage import Price


def available_prices(session: Session, pair: str, as_of: datetime) -> list[Price]:
    """Price bars for pair knowable at a point in time — only bars with ts_utc <= as_of."""
    return list(
        session.scalars(
            select(Price).where(Price.pair == pair, Price.ts_utc <= as_of).order_by(Price.ts_utc)
        )
    )
