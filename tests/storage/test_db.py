from pathlib import Path

from sqlalchemy import inspect, text

from market_lens.storage import init_db


def test_init_db_creates_schema(sqlite_db_url):
    engine = init_db(sqlite_db_url)

    db_file = Path(sqlite_db_url.removeprefix("sqlite:///"))
    assert db_file.exists()
    assert "events" in inspect(engine).get_table_names()


def test_session_executes_query(db_session):
    result = db_session.execute(text("select 1")).scalar()

    assert result == 1
