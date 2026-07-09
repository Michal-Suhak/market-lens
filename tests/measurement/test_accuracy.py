import pytest

from market_lens.measurement.accuracy import directional_accuracy, wilson_interval
from market_lens.measurement.frame import MeasurementRow


def _row(direction: str, realized: str | None) -> MeasurementRow:
    return MeasurementRow(
        event_id=1,
        model="m",
        pair="EUR/USD",
        ts_utc=None,
        direction=direction,
        score=0.0,
        confidence=0.5,
        surprise=None,
        realized_direction=realized,
        ret_1h=None,
        ret_4h=None,
        ret_24h=None,
    )


def test_wilson_interval_matches_known_values():
    low, high = wilson_interval(7, 10)

    assert low == pytest.approx(0.39675, abs=1e-4)
    assert high == pytest.approx(0.89218, abs=1e-4)


def test_wilson_interval_empty_is_zero():
    assert wilson_interval(0, 0) == (0.0, 0.0)


def test_directional_accuracy_counts_hits():
    rows = [
        _row("up", "up"),
        _row("down", "down"),
        _row("up", "down"),
        _row("flat", "up"),
    ]

    result = directional_accuracy(rows)

    assert result.n == 4
    assert result.hits == 2
    assert result.accuracy == pytest.approx(0.5)
    assert 0.0 <= result.ci_low <= result.accuracy <= result.ci_high <= 1.0


def test_directional_accuracy_drops_gaps():
    rows = [
        _row("up", "up"),
        _row("down", None),
    ]

    result = directional_accuracy(rows)

    assert result.n == 1
    assert result.hits == 1
    assert result.accuracy == pytest.approx(1.0)


def test_directional_accuracy_no_rows():
    result = directional_accuracy([])

    assert result.n == 0
    assert result.accuracy is None
    assert result.ci_low == 0.0
    assert result.ci_high == 0.0
