from datetime import datetime, timezone

from market_lens.measurement.event_study import event_study_paths
from market_lens.measurement.frame import MeasurementRow
from market_lens.utils.time import add_hours

UTC = timezone.utc
OFFSETS = (-4, -1, 0, 1, 4, 24)


def _row(ts, direction: str) -> MeasurementRow:
    return MeasurementRow(
        event_id=1,
        model="m",
        pair="EUR/USD",
        ts_utc=ts,
        direction=direction,
        score=0.0,
        confidence=0.5,
        surprise=None,
        realized_direction=None,
        ret_1h=None,
        ret_4h=None,
        ret_24h=None,
    )


def _seed_drift(db_session, make_price, t0):
    for hours in OFFSETS:
        db_session.add(
            make_price(pair="EUR/USD", ts_utc=add_hours(t0, hours), close=1.10 + 0.001 * hours)
        )


def test_upward_drift_gives_a_rising_mean_path(db_session, make_price):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    _seed_drift(db_session, make_price, t0)
    db_session.commit()

    paths = event_study_paths(db_session, [_row(t0, "up")], pair="EUR/USD", offsets_hours=OFFSETS)

    path = paths[0]
    assert path.bucket == "up"
    assert path.mean_return[OFFSETS.index(0)] == 0.0
    assert path.mean_return == sorted(path.mean_return)
    assert path.mean_return[0] < 0.0 < path.mean_return[-1]


def test_buckets_are_split_by_prediction(db_session, make_price):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    _seed_drift(db_session, make_price, t0)
    db_session.commit()

    paths = event_study_paths(
        db_session,
        [_row(t0, "up"), _row(t0, "down")],
        pair="EUR/USD",
        offsets_hours=OFFSETS,
    )

    assert [p.bucket for p in paths] == ["down", "up"]
    assert all(p.n == 1 for p in paths)


def test_missing_prices_yield_none(db_session):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)

    paths = event_study_paths(db_session, [_row(t0, "up")], pair="EUR/USD", offsets_hours=OFFSETS)

    assert paths[0].mean_return == [None] * len(OFFSETS)
