from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from market_lens.config import load_config
from market_lens.outcomes.compute import compute_all_outcomes
from market_lens.storage import Outcome

UTC = timezone.utc


@pytest.mark.parametrize(
    "close_1h, expected_direction",
    [
        (1.11, "up"),
        (1.09, "down"),
        (1.10, "flat"),
    ],
)
def test_compute_outcomes_direction_for_config_pairs(
    db_session, make_event, make_price, close_1h, expected_direction
):
    pairs = load_config().pairs
    primary = pairs[0]
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    db_session.add_all(
        [
            make_event(ts_utc=t0),
            make_price(pair=primary, ts_utc=t0, close=1.10),
            make_price(pair=primary, ts_utc=t0 + timedelta(hours=1), close=close_1h),
        ]
    )
    db_session.commit()

    count = compute_all_outcomes(db_session, pairs)

    outcomes = db_session.scalars(select(Outcome)).all()
    assert count == len(pairs)
    assert {o.pair for o in outcomes} == set(pairs)
    primary_outcome = next(o for o in outcomes if o.pair == primary)
    assert primary_outcome.realized_direction == expected_direction


def test_compute_outcomes_flags_gaps_as_null(db_session, make_event, make_price):
    pairs = load_config().pairs
    primary = pairs[0]
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    db_session.add_all(
        [
            make_event(ts_utc=t0),
            make_price(pair=primary, ts_utc=t0, close=1.10),
        ]
    )
    db_session.commit()

    compute_all_outcomes(db_session, pairs)

    primary_outcome = next(o for o in db_session.scalars(select(Outcome)) if o.pair == primary)
    assert primary_outcome.ret_1h is None
    assert primary_outcome.ret_4h is None
    assert primary_outcome.ret_24h is None
    assert primary_outcome.realized_direction is None
