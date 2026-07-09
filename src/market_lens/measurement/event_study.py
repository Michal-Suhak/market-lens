from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.orm import Session

from market_lens.measurement.frame import MeasurementRow
from market_lens.outcomes.mid_price import DEFAULT_TOLERANCE, get_mid_price
from market_lens.outcomes.returns import log_return
from market_lens.utils.time import add_hours

DEFAULT_OFFSETS_HOURS = (-4, -1, 0, 1, 4, 24)


@dataclass(frozen=True)
class EventStudyPath:
    """Mean log-return path around t0 for one prediction bucket."""

    bucket: str
    n: int
    offsets_hours: list[float]
    mean_return: list[float | None]


def by_direction(row: MeasurementRow) -> str:
    return row.direction


def event_study_paths(
    session: Session,
    rows: Iterable[MeasurementRow],
    *,
    pair: str,
    offsets_hours: Sequence[float] = DEFAULT_OFFSETS_HOURS,
    bucket: Callable[[MeasurementRow], str] = by_direction,
    tolerance: timedelta = DEFAULT_TOLERANCE,
) -> list[EventStudyPath]:
    """Average the log-return path relative to t0 across events, grouped by prediction bucket."""
    grouped: dict[str, list[MeasurementRow]] = defaultdict(list)
    for row in rows:
        grouped[bucket(row)].append(row)

    paths = []
    for name in sorted(grouped):
        group = grouped[name]
        mean_return = []
        for hours in offsets_hours:
            returns = []
            for row in group:
                price_t0 = get_mid_price(session, pair, row.ts_utc, tolerance=tolerance)
                price_h = get_mid_price(
                    session, pair, add_hours(row.ts_utc, hours), tolerance=tolerance
                )
                ret = log_return(price_t0, price_h)
                if ret is not None:
                    returns.append(ret)
            mean_return.append(sum(returns) / len(returns) if returns else None)
        paths.append(
            EventStudyPath(
                bucket=name,
                n=len(group),
                offsets_hours=list(offsets_hours),
                mean_return=mean_return,
            )
        )
    return paths
