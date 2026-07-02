from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from market_lens.storage import get_sessionmaker, init_db

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
