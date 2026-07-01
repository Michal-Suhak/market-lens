from __future__ import annotations

from datetime import datetime

from sqlalchemy import Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from market_lens.storage.db import Base
from market_lens.storage.types import UTCDateTime


class Event(Base):
    """A macro event (e.g. an FOMC decision) with its consensus and realized numbers."""

    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("institution", "event_type", "ts_utc", name="uq_event_natural_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    institution: Mapped[str]
    event_type: Mapped[str]
    currency: Mapped[str]
    ts_utc: Mapped[datetime] = mapped_column(UTCDateTime)  # event publication time, UTC
    forecast: Mapped[float | None]  # consensus number before the release
    actual: Mapped[float | None]  # realized number
    surprise: Mapped[float | None]  # actual - forecast, computed later


class Document(Base):
    """A central-bank document (e.g. an FOMC statement) indexed for RAG."""

    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint(
            "institution", "doc_type", "published_ts_utc", name="uq_document_natural_key"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    institution: Mapped[str]
    doc_type: Mapped[str]
    published_ts_utc: Mapped[datetime] = mapped_column(UTCDateTime)  # publication time, UTC
    text: Mapped[str] = mapped_column(Text)


class Price(Base):
    """A one-minute OHLC mid-price bar for a currency pair."""

    __tablename__ = "prices"

    pair: Mapped[str] = mapped_column(primary_key=True)
    ts_utc: Mapped[datetime] = mapped_column(UTCDateTime, primary_key=True)  # bar start, UTC
    open: Mapped[float]
    high: Mapped[float]
    low: Mapped[float]
    close: Mapped[float]
