import pytest

from market_lens.measurement.frame import MeasurementRow
from market_lens.measurement.ic import information_coefficient, spearman


def _row(score: float, ret: float | None) -> MeasurementRow:
    return MeasurementRow(
        event_id=1,
        model="m",
        pair="EUR/USD",
        ts_utc=None,
        direction="up",
        score=score,
        confidence=0.5,
        surprise=None,
        realized_direction=None,
        ret_1h=ret,
        ret_4h=ret,
        ret_24h=ret,
    )


def test_spearman_perfect_monotonic_is_one():
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)


def test_spearman_perfect_inverse_is_minus_one():
    assert spearman([1, 2, 3, 4], [40, 30, 20, 10]) == pytest.approx(-1.0)


def test_spearman_handles_ties_via_average_ranks():
    assert spearman([1, 1, 2, 2], [1, 1, 2, 2]) == pytest.approx(1.0)


def test_spearman_undefined_cases():
    assert spearman([1], [1]) is None
    assert spearman([1, 2], [5, 5]) is None


def test_information_coefficient_perfect_monotonic():
    rows = [_row(0.1, 0.001), _row(0.2, 0.002), _row(0.9, 0.003)]

    result = information_coefficient(rows, horizon="ret_1h")

    assert result.n == 3
    assert result.ic == pytest.approx(1.0)


def test_information_coefficient_drops_missing_returns():
    rows = [_row(0.1, 0.001), _row(0.2, None), _row(0.9, 0.003)]

    result = information_coefficient(rows, horizon="ret_1h")

    assert result.n == 2
    assert result.ic == pytest.approx(1.0)
