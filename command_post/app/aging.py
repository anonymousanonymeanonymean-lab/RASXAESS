"""Message aging policy. Configurable thresholds."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum


class AgingState(str, Enum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    RECENT = "RECENT"
    STALE = "STALE"
    EXPIRED = "EXPIRED"


class AgingPolicy:
    def __init__(self,
                 new_s: int = 10,
                 active_s: int = 60,
                 recent_s: int = 300,
                 stale_s: int = 900) -> None:
        self.new_s = new_s
        self.active_s = active_s
        self.recent_s = recent_s
        self.stale_s = stale_s

    def classify(self, event_timestamp: datetime,
                 now: datetime | None = None) -> tuple[AgingState, float]:
        now = now or datetime.now(timezone.utc)
        if event_timestamp.tzinfo is None:
            event_timestamp = event_timestamp.replace(tzinfo=timezone.utc)
        age = (now - event_timestamp).total_seconds()

        if age <= self.new_s:
            state = AgingState.NEW
        elif age <= self.active_s:
            state = AgingState.ACTIVE
        elif age <= self.recent_s:
            state = AgingState.RECENT
        elif age <= self.stale_s:
            state = AgingState.STALE
        else:
            state = AgingState.EXPIRED
        return state, age