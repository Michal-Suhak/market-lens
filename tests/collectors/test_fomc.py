from datetime import date, datetime, timezone

from sqlalchemy import select

from market_lens.collectors.fomc import (
    build_fomc_events,
    compute_surprise,
    fetch_fomc_events,
    load_fomc_events,
)
from market_lens.storage import Event

UTC = timezone.utc


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_compute_surprise():
    assert compute_surprise(4.75, 4.50) == -0.25
    assert compute_surprise(None, 4.50) is None
    assert compute_surprise(4.75, None) is None


def test_build_fomc_events_utc_and_surprise():
    dates = [date(2026, 1, 28), date(2026, 6, 17)]
    rate = {date(2026, 1, 28): 4.50, date(2026, 6, 17): 3.75}
    forecasts = {date(2026, 1, 28): 4.75}

    events = build_fomc_events(dates, rate, forecasts)

    assert events[0].ts_utc == datetime(2026, 1, 28, 19, 0, tzinfo=UTC)  # 14:00 EST -> 19:00 UTC
    assert events[1].ts_utc == datetime(2026, 6, 17, 18, 0, tzinfo=UTC)  # 14:00 EDT -> 18:00 UTC
    assert events[0].surprise == -0.25
    assert events[1].surprise is None


def test_load_fomc_events(db_session):
    dates = [date(2026, 1, 28), date(2026, 6, 17)]
    events = build_fomc_events(dates, {date(2026, 1, 28): 4.50})

    count = load_fomc_events(db_session, events)

    stored = db_session.scalars(select(Event).order_by(Event.ts_utc)).all()
    assert count == 2
    assert len(stored) == 2
    assert stored[0].institution == "FED"
    assert stored[0].actual == 4.50
    assert stored[1].actual is None


def test_fetch_fomc_events(monkeypatch):
    dates_payload = {"release_dates": [{"date": "2026-01-28"}, {"date": "2026-06-17"}]}
    obs_payload = {
        "observations": [
            {"date": "2026-01-28", "value": "4.50"},
            {"date": "2026-06-17", "value": "3.75"},
        ]
    }

    def fake_get(url, params=None, timeout=None):
        payload = dates_payload if "release/dates" in url else obs_payload
        return _FakeResponse(payload)

    monkeypatch.setattr("market_lens.collectors.fomc.requests.get", fake_get)

    events = fetch_fomc_events("dummy-key")

    assert len(events) == 2
    assert events[0].ts_utc == datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    assert events[0].actual == 4.50
    assert events[1].actual == 3.75
    assert events[0].forecast is None
