from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

from market_lens.measurement.frame import MeasurementRow

Z_95 = 1.96  # normal quantile for a 95% two-sided interval


@dataclass(frozen=True)
class Accuracy:
    """Directional hit rate with a Wilson score confidence interval."""

    n: int
    hits: int
    accuracy: float | None
    ci_low: float
    ci_high: float


def wilson_interval(hits: int, n: int, *, z: float = Z_95) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion; (0, 0) when there are no trials."""
    if n == 0:
        return (0.0, 0.0)
    p = hits / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = z / denom * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return (center - margin, center + margin)


def directional_accuracy(rows: Iterable[MeasurementRow], *, z: float = Z_95) -> Accuracy:
    """Share of predictions whose direction matches the realized move; gaps are dropped."""
    scored = [row for row in rows if row.realized_direction is not None]
    n = len(scored)
    hits = sum(1 for row in scored if row.direction == row.realized_direction)
    accuracy = hits / n if n else None
    ci_low, ci_high = wilson_interval(hits, n, z=z)
    return Accuracy(n=n, hits=hits, accuracy=accuracy, ci_low=ci_low, ci_high=ci_high)
