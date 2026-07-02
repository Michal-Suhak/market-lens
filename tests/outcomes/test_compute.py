import math
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from market_lens.outcomes.compute import save_outcome
from market_lens.storage import Outcome

UTC = timezone.utc


def test_build_and_save_outcome(db_session, make_event, make_price):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    event = make_event(ts_utc=t0)
    db_session.add_all(
        [
            event,
            make_price(ts_utc=t0, close=1.10),
            make_price(ts_utc=t0 + timedelta(hours=1), close=1.11),
            make_price(ts_utc=t0 + timedelta(hours=4), close=1.09),
            make_price(ts_utc=t0 + timedelta(hours=24), close=1.12),
        ]
    )
    db_session.commit()

    save_outcome(db_session, event, "EUR/USD")
    db_session.expire_all()

    stored = db_session.scalars(select(Outcome)).one()
    assert stored.pair == "EUR/USD"
    assert stored.ret_1h == pytest.approx(math.log(1.11 / 1.10))
    assert stored.ret_4h == pytest.approx(math.log(1.09 / 1.10))
    assert stored.ret_24h == pytest.approx(math.log(1.12 / 1.10))
    assert stored.realized_direction == "up"
    assert stored.event.institution == "FED"


def test_missing_windows_become_null(db_session, make_event, make_price):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    event = make_event(ts_utc=t0)
    db_session.add_all(
        [
            event,
            make_price(ts_utc=t0, close=1.10),
            make_price(ts_utc=t0 + timedelta(hours=1), close=1.11),
        ]
    )
    db_session.commit()

    save_outcome(db_session, event, "EUR/USD")
    db_session.expire_all()

    stored = db_session.scalars(select(Outcome)).one()
    assert stored.ret_1h == pytest.approx(math.log(1.11 / 1.10))
    assert stored.ret_4h is None
    assert stored.ret_24h is None
    assert stored.realized_direction == "up"


def test_event_with_no_prices_does_not_crash(db_session, make_event):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    event = make_event(ts_utc=t0)
    db_session.add(event)
    db_session.commit()

    save_outcome(db_session, event, "EUR/USD")
    db_session.expire_all()

    stored = db_session.scalars(select(Outcome)).one()
    assert stored.ret_1h is None
    assert stored.ret_4h is None
    assert stored.ret_24h is None
    assert stored.realized_direction is None
