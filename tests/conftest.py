from collections.abc import Callable, Iterator
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from market_lens.storage import Event, get_sessionmaker, init_db

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_config_file() -> Path:
    return FIXTURES_DIR / "sample_config.yaml"


@pytest.fixture
def sqlite_db_url(tmp_path) -> str:
    return f"sqlite:///{tmp_path / 'test.db'}"


@pytest.fixture
def db_session(sqlite_db_url) -> Iterator[Session]:
    init_db(sqlite_db_url)
    with get_sessionmaker(sqlite_db_url)() as session:
        yield session


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
