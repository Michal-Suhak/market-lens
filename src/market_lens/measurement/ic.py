from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from market_lens.measurement.frame import MeasurementRow


@dataclass(frozen=True)
class InformationCoefficient:
    """Rank correlation between predicted score and realized return over one horizon."""

    n: int
    ic: float | None


def _ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        average = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = average
        i = j + 1
    return ranks


def spearman(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    """Spearman rank correlation; None when undefined (fewer than 2 points or no variance)."""
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    rx, ry = _ranks(xs), _ranks(ys)
    mean_x = sum(rx) / len(rx)
    mean_y = sum(ry) / len(ry)
    cov = sum((a - mean_x) * (b - mean_y) for a, b in zip(rx, ry))
    var_x = sum((a - mean_x) ** 2 for a in rx)
    var_y = sum((b - mean_y) ** 2 for b in ry)
    if var_x == 0 or var_y == 0:
        return None
    return cov / (var_x * var_y) ** 0.5


def information_coefficient(
    rows: Iterable[MeasurementRow], *, horizon: str = "ret_1h"
) -> InformationCoefficient:
    """Spearman IC of score against the chosen horizon return; rows missing either are dropped."""
    pairs = [
        (row.score, getattr(row, horizon)) for row in rows if getattr(row, horizon) is not None
    ]
    scores = [score for score, _ in pairs]
    returns = [ret for _, ret in pairs]
    return InformationCoefficient(n=len(pairs), ic=spearman(scores, returns))
