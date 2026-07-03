from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


class Prediction(Base):
    """An LLM prediction for an event: tone, direction and confidence logged at t0."""

    __tablename__ = "predictions"
    __table_args__ = (UniqueConstraint("event_id", "model", name="uq_prediction_event_model"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    tone: Mapped[str]
    direction: Mapped[str]
    confidence: Mapped[float]
    score: Mapped[float]
    model: Mapped[str]
    ts_utc: Mapped[datetime] = mapped_column(UTCDateTime)  # prediction time (t0), UTC

    event: Mapped[Event] = relationship()


class Outcome(Base):
    """Realized price moves after an event, per currency pair."""

    __tablename__ = "outcomes"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), primary_key=True)
    pair: Mapped[str] = mapped_column(primary_key=True)
    ret_1h: Mapped[float | None]
    ret_4h: Mapped[float | None]
    ret_24h: Mapped[float | None]
    realized_direction: Mapped[str | None]

    event: Mapped[Event] = relationship()


class LlmCacheEntry(Base):
    """A cached LLM response keyed by a hash of the request."""

    __tablename__ = "llm_cache"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(Text)
