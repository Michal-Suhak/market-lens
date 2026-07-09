from __future__ import annotations

import csv
import json
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from market_lens.measurement.accuracy import directional_accuracy
from market_lens.measurement.calibration import calibration
from market_lens.measurement.event_study import DEFAULT_OFFSETS_HOURS, event_study_paths
from market_lens.measurement.frame import build_frame
from market_lens.measurement.ic import information_coefficient
from market_lens.measurement.lift import coin_flip_lift, surprise_sign_lift


def build_report(
    session: Session,
    *,
    pair: str,
    model: str | None = None,
    horizon: str = "ret_1h",
    n_bins: int = 10,
    offsets_hours: Sequence[float] = DEFAULT_OFFSETS_HOURS,
) -> dict[str, Any]:
    """Compose every measurement metric for one pair and model into a serializable report."""
    rows = build_frame(session, pair=pair, model=model)
    return {
        "pair": pair,
        "model": model,
        "horizon": horizon,
        "n": len(rows),
        "accuracy": asdict(directional_accuracy(rows)),
        "information_coefficient": asdict(information_coefficient(rows, horizon=horizon)),
        "calibration": asdict(calibration(rows, n_bins=n_bins)),
        "lift": {
            "surprise_sign": asdict(surprise_sign_lift(rows)),
            "coin_flip": asdict(coin_flip_lift(rows)),
        },
        "event_study": [
            asdict(path)
            for path in event_study_paths(session, rows, pair=pair, offsets_hours=offsets_hours)
        ],
    }


def write_json(report: dict[str, Any], path: str | Path) -> Path:
    """Write the report as pretty JSON and return the path."""
    path = Path(path)
    path.write_text(json.dumps(report, indent=2, sort_keys=True))
    return path


def write_frame_csv(
    session: Session, path: str | Path, *, pair: str, model: str | None = None
) -> Path:
    """Write the per-event joined frame as CSV for external plotting; return the path."""
    path = Path(path)
    rows = build_frame(session, pair=pair, model=model)
    fieldnames = [
        "event_id",
        "model",
        "pair",
        "ts_utc",
        "direction",
        "score",
        "confidence",
        "surprise",
        "realized_direction",
        "ret_1h",
        "ret_4h",
        "ret_24h",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            record = asdict(row)
            record["ts_utc"] = row.ts_utc.isoformat() if row.ts_utc is not None else ""
            writer.writerow(record)
    return path
