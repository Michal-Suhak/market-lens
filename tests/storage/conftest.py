from collections.abc import Callable
from datetime import datetime, timezone

import pytest

from market_lens.storage import Document, Event, Outcome, Prediction, Price


@pytest.fixture
def make_event() -> Callable[..., Event]:
    def _make(**overrides) -> Event:
        defaults = {
            "institution": "FED",
            "event_type": "FOMC",
            "currency": "USD",
            "ts_utc": datetime(2026, 1, 28, 19, 0, tzinfo=timezone.utc),
            "forecast": 5.5,
            "actual": 5.5,
        }
        return Event(**{**defaults, **overrides})

    return _make


@pytest.fixture
def make_document() -> Callable[..., Document]:
    def _make(**overrides) -> Document:
        defaults = {
            "institution": "FED",
            "doc_type": "FOMC",
            "published_ts_utc": datetime(2026, 1, 28, 19, 0, tzinfo=timezone.utc),
            "text": "The Committee decided to maintain the target range.",
        }
        return Document(**{**defaults, **overrides})

    return _make


@pytest.fixture
def make_price() -> Callable[..., Price]:
    def _make(**overrides) -> Price:
        defaults = {
            "pair": "EUR/USD",
            "ts_utc": datetime(2026, 1, 28, 19, 0, tzinfo=timezone.utc),
            "open": 1.0850,
            "high": 1.0860,
            "low": 1.0845,
            "close": 1.0858,
        }
        return Price(**{**defaults, **overrides})

    return _make


@pytest.fixture
def make_prediction(make_event) -> Callable[..., Prediction]:
    def _make(**overrides) -> Prediction:
        defaults = {
            "event": make_event(),
            "tone": "hawkish",
            "direction": "down_eurusd",
            "confidence": 0.84,
            "score": 0.62,
            "model": "gemini-2.5-flash",
            "ts_utc": datetime(2026, 1, 28, 19, 0, tzinfo=timezone.utc),
        }
        return Prediction(**{**defaults, **overrides})

    return _make


@pytest.fixture
def make_outcome(make_event) -> Callable[..., Outcome]:
    def _make(**overrides) -> Outcome:
        defaults = {
            "event": make_event(),
            "pair": "EUR/USD",
            "ret_1h": 0.0012,
            "ret_4h": 0.0020,
            "ret_24h": 0.0035,
            "realized_direction": "up",
        }
        return Outcome(**{**defaults, **overrides})

    return _make
