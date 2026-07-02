from datetime import datetime, timedelta, timezone

from market_lens.replay.prices import available_prices

UTC = timezone.utc


def test_available_prices_excludes_bars_after_as_of(db_session, make_price):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    db_session.add_all(
        [
            make_price(ts_utc=t0 - timedelta(hours=1), close=1.10),
            make_price(ts_utc=t0, close=1.11),
            make_price(ts_utc=t0 + timedelta(hours=1), close=1.12),
        ]
    )
    db_session.commit()

    bars = available_prices(db_session, "EUR/USD", t0)

    assert [bar.ts_utc for bar in bars] == [t0 - timedelta(hours=1), t0]
