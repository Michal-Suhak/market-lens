import pytest

from market_lens.measurement.calibration import brier_score, calibration
from market_lens.measurement.frame import MeasurementRow


def _row(confidence: float, direction: str, realized: str | None) -> MeasurementRow:
    return MeasurementRow(
        event_id=1,
        model="m",
        pair="EUR/USD",
        ts_utc=None,
        direction=direction,
        score=0.0,
        confidence=confidence,
        surprise=None,
        realized_direction=realized,
        ret_1h=None,
        ret_4h=None,
        ret_24h=None,
    )


def test_brier_perfect_confident_is_zero():
    rows = [_row(1.0, "up", "up"), _row(1.0, "down", "down")]

    assert brier_score(rows) == pytest.approx(0.0)


def test_brier_half_confidence_coin_flip():
    rows = [_row(0.5, "up", "up"), _row(0.5, "up", "down")]

    assert brier_score(rows) == pytest.approx(0.25)


def test_brier_matches_calibrated_expectation():
    rows = [_row(0.7, "up", "up") for _ in range(7)]
    rows += [_row(0.7, "up", "down") for _ in range(3)]

    assert brier_score(rows) == pytest.approx(0.21)


def test_brier_none_without_scored_rows():
    assert brier_score([_row(0.7, "up", None)]) is None


def test_calibration_bins_report_confidence_and_accuracy():
    rows = [_row(0.7, "up", "up") for _ in range(7)]
    rows += [_row(0.7, "up", "down") for _ in range(3)]

    result = calibration(rows, n_bins=10)

    assert result.n == 10
    assert result.brier == pytest.approx(0.21)
    bucket = result.bins[7]
    assert bucket.count == 10
    assert bucket.mean_confidence == pytest.approx(0.7)
    assert bucket.accuracy == pytest.approx(0.7)
    assert bucket.lower == pytest.approx(0.7)
    assert bucket.upper == pytest.approx(0.8)


def test_calibration_empty_bins_are_none():
    result = calibration([_row(0.05, "up", "up")], n_bins=10)

    assert result.bins[0].count == 1
    assert result.bins[5].count == 0
    assert result.bins[5].mean_confidence is None
    assert result.bins[5].accuracy is None
