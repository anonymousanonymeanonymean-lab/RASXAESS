"""Time utilities. All timestamps are UTC."""
from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


def to_iso(dt: datetime) -> str:
    """Serialize datetime to ISO-8601 UTC string."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def from_epoch(seconds: float) -> datetime:
    """Convert epoch seconds to UTC datetime."""
    return datetime.fromtimestamp(seconds, tz=timezone.utc)


def age_seconds(event_ts: datetime, received_ts: datetime) -> float:
    """Return age in seconds between two UTC datetimes."""
    return (received_ts - event_ts).total_seconds()