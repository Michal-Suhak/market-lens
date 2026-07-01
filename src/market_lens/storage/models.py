from __future__ import annotations

from datetime import datetime

from sqlalchemy import UniqueConstraint
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
