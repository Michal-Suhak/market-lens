from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import requests
from sqlalchemy.orm import Session

from market_lens.storage import Event
from market_lens.utils import to_utc

FRED_BASE = "https://api.stlouisfed.org/fred"
FOMC_RELEASE_ID = 101  # "FOMC Press Release" — one release date per meeting, holds included
TARGET_RATE_SERIES = "DFEDTARU"
FOMC_ANNOUNCEMENT_ET = time(14, 0)  # statement released at 2:00 PM Eastern
EASTERN = ZoneInfo("America/New_York")


def compute_surprise(forecast: float | None, actual: float | None) -> float | None:
    if forecast is None or actual is None:
        return None
    return actual - forecast


def build_fomc_events(
    dates: Iterable[date],
    rate_by_date: Mapping[date, float],
    forecasts: Mapping[date, float] | None = None,
) -> list[Event]:
    forecasts = forecasts or {}
    events = []
    for meeting in dates:
        forecast = forecasts.get(meeting)
        actual = rate_by_date.get(meeting)
        events.append(
            Event(
                institution="FED",
                event_type="FOMC",
                currency="USD",
                ts_utc=to_utc(datetime.combine(meeting, FOMC_ANNOUNCEMENT_ET), assume_tz=EASTERN),
                forecast=forecast,
                actual=actual,
                surprise=compute_surprise(forecast, actual),
            )
        )
    return events


def fetch_fomc_events(
    api_key: str, *, forecasts: Mapping[date, float] | None = None
) -> list[Event]:
    dates = _fetch_fomc_dates(api_key)
    rate_by_date = _fetch_target_rate(api_key)
    return build_fomc_events(dates, rate_by_date, forecasts)


def load_fomc_events(session: Session, events: Iterable[Event]) -> int:
    events = list(events)
    session.add_all(events)
    session.commit()
    return len(events)


def _fetch_fomc_dates(api_key: str) -> list[date]:
    params = {"release_id": FOMC_RELEASE_ID, "api_key": api_key, "file_type": "json"}
    resp = requests.get(f"{FRED_BASE}/release/dates", params=params, timeout=30)
    resp.raise_for_status()
    return [date.fromisoformat(row["date"]) for row in resp.json()["release_dates"]]


def _fetch_target_rate(api_key: str) -> dict[date, float]:
    params = {"series_id": TARGET_RATE_SERIES, "api_key": api_key, "file_type": "json"}
    resp = requests.get(f"{FRED_BASE}/series/observations", params=params, timeout=30)
    resp.raise_for_status()
    return {
        date.fromisoformat(obs["date"]): float(obs["value"])
        for obs in resp.json()["observations"]
        if obs["value"] != "."
    }
