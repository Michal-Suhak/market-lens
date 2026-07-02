from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from market_lens.config import load_config


class Base(DeclarativeBase):
    pass


def _resolve_url(database_url: str | None) -> str:
    return database_url or load_config().secrets.database_url


def get_engine(database_url: str | None = None) -> Engine:
    return create_engine(_resolve_url(database_url))


def get_sessionmaker(database_url: str | None = None) -> sessionmaker:
    return sessionmaker(bind=get_engine(database_url))


def init_db(database_url: str | None = None) -> Engine:
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    return engine
