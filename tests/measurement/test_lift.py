import pytest

from market_lens.measurement.frame import MeasurementRow
from market_lens.measurement.lift import coin_flip_lift, sign_direction, surprise_sign_lift


def _row(direction: str, realized: str | None, surprise: float | None) -> MeasurementRow:
    return MeasurementRow(
        event_id=1,
        model="m",
        pair="EUR/USD",
        ts_utc=None,
        direction=direction,
        score=0.0,
        confidence=0.5,
        surprise=surprise,
        realized_direction=realized,
        ret_1h=None,
        ret_4h=None,
        ret_24h=None,
    )


def test_sign_direction_maps_sign():
    assert sign_direction(0.3) == "up"
    assert sign_direction(-0.3) == "down"
    assert sign_direction(0.0) == "flat"
    assert sign_direction(None) is None


def test_surprise_lift_zero_when_signal_equals_baseline():
    rows = [
        _row("up", "up", surprise=0.2),
        _row("down", "up", surprise=-0.2),
    ]

    result = surprise_sign_lift(rows)

    assert result.system_accuracy == result.baseline_accuracy
    assert result.lift == pytest.approx(0.0)


def test_surprise_lift_positive_when_system_beats_baseline():
    rows = [
        _row("up", "up", surprise=-0.2),
        _row("up", "up", surprise=-0.2),
    ]

    result = surprise_sign_lift(rows)

    assert result.system_accuracy == pytest.approx(1.0)
    assert result.baseline_accuracy == pytest.approx(0.0)
    assert result.lift == pytest.approx(1.0)


def test_surprise_lift_drops_rows_without_surprise():
    rows = [_row("up", "up", surprise=None)]

    result = surprise_sign_lift(rows)

    assert result.n == 0
    assert result.lift is None


def test_coin_flip_lift_against_half():
    rows = [
        _row("up", "up", surprise=None),
        _row("down", "down", surprise=None),
        _row("up", "down", surprise=None),
        _row("down", "up", surprise=None),
    ]

    result = coin_flip_lift(rows)

    assert result.system_accuracy == pytest.approx(0.5)
    assert result.baseline_accuracy == pytest.approx(0.5)
    assert result.lift == pytest.approx(0.0)
