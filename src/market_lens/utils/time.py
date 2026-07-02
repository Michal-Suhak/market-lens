from __future__ import annotations

from datetime import datetime, timedelta, timezone, tzinfo

UTC = timezone.utc


def to_utc(dt: datetime, *, assume_tz: tzinfo = UTC) -> datetime:
    """Return dt as a UTC-aware datetime; naive input is interpreted as assume_tz."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=assume_tz)
    return dt.astimezone(UTC)


def parse_utc(value: str, *, fmt: str | None = None, assume_tz: tzinfo = UTC) -> datetime:
    """Parse a timestamp string to a UTC-aware datetime (ISO 8601 unless fmt is given)."""
    dt = datetime.strptime(value, fmt) if fmt else datetime.fromisoformat(value)
    return to_utc(dt, assume_tz=assume_tz)


def add_hours(t0: datetime, hours: float) -> datetime:
    """Add an elapsed-time window to t0 in UTC; stays correct across DST transitions."""
    return to_utc(t0) + timedelta(hours=hours)
