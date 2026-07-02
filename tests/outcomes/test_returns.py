import math
from datetime import datetime, timedelta, timezone

import pytest

from market_lens.outcomes.returns import compute_returns, log_return, realized_direction

UTC = timezone.utc


def test_log_return_manual():
    assert log_return(1.10, 1.11) == pytest.approx(math.log(1.11 / 1.10))
    assert log_return(None, 1.11) is None
    assert log_return(1.10, None) is None


def test_realized_direction():
    assert realized_direction(0.01) == "up"
    assert realized_direction(-0.01) == "down"
    assert realized_direction(0.0) == "flat"
    assert realized_direction(None) is None


def test_compute_returns_manual_values(db_session, make_price):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    db_session.add_all(
        [
            make_price(ts_utc=t0, close=1.10),
            make_price(ts_utc=t0 + timedelta(hours=1), close=1.11),
            make_price(ts_utc=t0 + timedelta(hours=4), close=1.09),
            make_price(ts_utc=t0 + timedelta(hours=24), close=1.10),
        ]
    )
    db_session.commit()

    rets = compute_returns(db_session, "EUR/USD", t0, [1, 4, 24])

    assert rets[1] == pytest.approx(math.log(1.11 / 1.10))
    assert rets[4] == pytest.approx(math.log(1.09 / 1.10))
    assert rets[24] == pytest.approx(0.0, abs=1e-12)
    assert realized_direction(rets[1]) == "up"


def test_return_is_none_when_a_price_is_missing(db_session, make_price):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    db_session.add(make_price(ts_utc=t0, close=1.10))
    db_session.commit()

    rets = compute_returns(db_session, "EUR/USD", t0, [1])

    assert rets[1] is None
