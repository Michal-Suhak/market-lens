from __future__ import annotations

from collections.abc import Iterator
from datetime import timedelta, timezone, tzinfo
from pathlib import Path

from sqlalchemy.orm import Session

from market_lens.storage import Price
from market_lens.utils import parse_utc

HISTDATA_TS_FORMAT = "%Y%m%d %H%M%S"
HISTDATA_TZ = timezone(timedelta(hours=-5))  # HistData M1 uses EST without DST


def parse_histdata_m1(
    csv_path: str | Path, pair: str, *, source_tz: tzinfo = HISTDATA_TZ
) -> Iterator[Price]:
    for line in Path(csv_path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        ts, open_, high, low, close, *_ = line.split(";")
        yield Price(
            pair=pair,
            ts_utc=parse_utc(ts, fmt=HISTDATA_TS_FORMAT, assume_tz=source_tz),
            open=float(open_),
            high=float(high),
            low=float(low),
            close=float(close),
        )


def load_histdata_m1(
    session: Session, csv_path: str | Path, pair: str, *, source_tz: tzinfo = HISTDATA_TZ
) -> int:
    """Load a HistData M1 CSV for one pair into the prices table; return the bar count."""
    bars = list(parse_histdata_m1(csv_path, pair, source_tz=source_tz))
    session.add_all(bars)
    session.commit()
    return len(bars)
