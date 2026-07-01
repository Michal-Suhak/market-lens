from pathlib import Path

from sqlalchemy import inspect, text

from market_lens.storage import get_sessionmaker, init_db


def test_init_db_creates_empty_database(sqlite_db_url):
    engine = init_db(sqlite_db_url)
    db_file = Path(sqlite_db_url.removeprefix("sqlite:///"))
    assert db_file.exists()
    assert inspect(engine).get_table_names() == []


def test_session_executes_query(sqlite_db_url):
    init_db(sqlite_db_url)
    session_factory = get_sessionmaker(sqlite_db_url)
    with session_factory() as session:
        assert session.execute(text("select 1")).scalar() == 1
