"""Message router: decides MQTT topic and priority."""
from __future__ import annotations

from enum import Enum


class Priority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class MessageRouter:
    """Route messages to appropriate MQTT topics with priority.

    Phase B: interface only. Implementation in Phase G.
    """

    def route(self, message: object) -> tuple[str, Priority]:
        raise NotImplementedError