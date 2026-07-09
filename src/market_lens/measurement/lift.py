from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from market_lens.measurement.frame import MeasurementRow

COIN_FLIP_ACCURACY = 0.5


@dataclass(frozen=True)
class Lift:
    """System hit rate against a baseline over the same events, and the gap between them."""

    n: int
    system_accuracy: float | None
    baseline_accuracy: float | None
    lift: float | None


def sign_direction(value: float | None) -> str | None:
    if value is None:
        return None
    if value > 0:
        return "up"
    if value < 0:
        return "down"
    return "flat"


def _hit_rate(hits: int, n: int) -> float | None:
    return hits / n if n else None


def surprise_sign_lift(rows: Iterable[MeasurementRow]) -> Lift:
    """Lift of the system over predicting direction from the sign of the numeric surprise."""
    scored = [
        row for row in rows if row.realized_direction is not None and row.surprise is not None
    ]
    n = len(scored)
    system_hits = sum(1 for row in scored if row.direction == row.realized_direction)
    baseline_hits = sum(
        1 for row in scored if sign_direction(row.surprise) == row.realized_direction
    )
    system = _hit_rate(system_hits, n)
    baseline = _hit_rate(baseline_hits, n)
    lift = system - baseline if system is not None and baseline is not None else None
    return Lift(n=n, system_accuracy=system, baseline_accuracy=baseline, lift=lift)


def coin_flip_lift(rows: Iterable[MeasurementRow], *, baseline: float = COIN_FLIP_ACCURACY) -> Lift:
    """Lift of the system over a fixed coin-flip hit rate."""
    scored = [row for row in rows if row.realized_direction is not None]
    n = len(scored)
    system_hits = sum(1 for row in scored if row.direction == row.realized_direction)
    system = _hit_rate(system_hits, n)
    lift = system - baseline if system is not None else None
    return Lift(n=n, system_accuracy=system, baseline_accuracy=baseline, lift=lift)
