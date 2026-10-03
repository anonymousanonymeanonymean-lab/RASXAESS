"""Health monitoring service."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class HealthSnapshot:
    uptime_seconds: float
    radio_connected: bool
    mqtt_connected: bool
    database_ok: bool
    outbox_pending: int = 0
    last_beacon_message_at: str | None = None
    last_writer_message_at: str | None = None
    components: dict[str, Any] = field(default_factory=dict)


class HealthMonitor:
    """Aggregates health information."""

    def __init__(self) -> None:
        self._started = time.time()

    def snapshot(self, radio_connected: bool, mqtt_connected: bool,
                 database_ok: bool) -> HealthSnapshot:
        return HealthSnapshot(
            uptime_seconds=time.time() - self._started,
            radio_connected=radio_connected,
            mqtt_connected=mqtt_connected,
            database_ok=database_ok,
        )