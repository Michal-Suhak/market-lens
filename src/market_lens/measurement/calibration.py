from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from market_lens.measurement.frame import MeasurementRow


@dataclass(frozen=True)
class CalibrationBin:
    """One confidence bucket of a reliability curve."""

    lower: float
    upper: float
    count: int
    mean_confidence: float | None
    accuracy: float | None


@dataclass(frozen=True)
class Calibration:
    """Brier score and reliability-curve bins over scored predictions."""

    n: int
    brier: float | None
    bins: list[CalibrationBin]


def _scored(rows: Iterable[MeasurementRow]) -> list[tuple[float, int]]:
    return [
        (row.confidence, int(row.direction == row.realized_direction))
        for row in rows
        if row.realized_direction is not None
    ]


def _brier(scored: list[tuple[float, int]]) -> float | None:
    if not scored:
        return None
    return sum((confidence - correct) ** 2 for confidence, correct in scored) / len(scored)


def brier_score(rows: Iterable[MeasurementRow]) -> float | None:
    """Mean squared error between confidence and the correctness indicator; None if no rows."""
    return _brier(_scored(rows))


def calibration(rows: Iterable[MeasurementRow], *, n_bins: int = 10) -> Calibration:
    """Bucket predictions by confidence and report per-bin mean confidence vs observed accuracy."""
    scored = _scored(rows)
    buckets: list[list[tuple[float, int]]] = [[] for _ in range(n_bins)]
    for confidence, correct in scored:
        index = min(int(confidence * n_bins), n_bins - 1)
        buckets[index].append((confidence, correct))

    bins = []
    for index, bucket in enumerate(buckets):
        count = len(bucket)
        mean_confidence = sum(c for c, _ in bucket) / count if count else None
        accuracy = sum(k for _, k in bucket) / count if count else None
        bins.append(
            CalibrationBin(
                lower=index / n_bins,
                upper=(index + 1) / n_bins,
                count=count,
                mean_confidence=mean_confidence,
                accuracy=accuracy,
            )
        )
    return Calibration(n=len(scored), brier=_brier(scored), bins=bins)
