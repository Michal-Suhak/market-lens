from datetime import datetime, timedelta, timezone

from market_lens.outcomes.mid_price import get_mid_price

UTC = timezone.utc


def test_exact_bar(db_session, make_price):
    ts = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    db_session.add(make_price(ts_utc=ts, close=1.0850))
    db_session.commit()

    price = get_mid_price(db_session, "EUR/USD", ts)

    assert price == 1.0850


def test_nearest_bar_when_no_exact_match(db_session, make_price):
    db_session.add(make_price(ts_utc=datetime(2026, 1, 28, 18, 59, tzinfo=UTC), close=1.0840))
    db_session.commit()

    price = get_mid_price(db_session, "EUR/USD", datetime(2026, 1, 28, 19, 0, tzinfo=UTC))

    assert price == 1.0840


def test_picks_closest_of_several(db_session, make_price):
    ts = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    db_session.add(make_price(ts_utc=ts - timedelta(seconds=40), close=1.0840))
    db_session.add(make_price(ts_utc=ts + timedelta(seconds=20), close=1.0860))
    db_session.commit()

    price = get_mid_price(db_session, "EUR/USD", ts)

    assert price == 1.0860


def test_gap_returns_none(db_session, make_price):
    db_session.add(make_price(ts_utc=datetime(2026, 1, 28, 12, 0, tzinfo=UTC), close=1.0800))
    db_session.commit()

    price = get_mid_price(db_session, "EUR/USD", datetime(2026, 1, 28, 19, 0, tzinfo=UTC))

    assert price is None
