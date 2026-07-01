from datetime import datetime, timezone

from sqlalchemy import select

from market_lens.collectors.prices import load_histdata_m1
from market_lens.storage import Price

UTC = timezone.utc


def test_load_histdata_m1(db_session, histdata_csv):
    count = load_histdata_m1(db_session, histdata_csv, "EUR/USD")

    bars = db_session.scalars(select(Price).order_by(Price.ts_utc)).all()

    assert count == 3
    assert len(bars) == 3
    assert bars[0].pair == "EUR/USD"
    assert bars[0].ts_utc == datetime(2026, 1, 28, 19, 0, tzinfo=UTC)  # 14:00 EST -> 19:00 UTC
    assert bars[0].open == 1.08500
    assert bars[0].close == 1.08580
