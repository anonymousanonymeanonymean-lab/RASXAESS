"""Abstract radio interface.

All radio backends (serial LoRa, simulated) MUST implement this interface.
The rest of the ONA core depends only on this abstraction.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.utils.time import utc_now


@dataclass
class RadioPacket:
    """A raw radio packet received from the radio backend."""
    data: bytes
    received_at: datetime = field(default_factory=utc_now)
    rssi: Optional[float] = None
    snr: Optional[float] = None


class RadioInterface(ABC):
    """Abstract base class for all radio backends."""

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection. Return True on success."""

    @abstractmethod
    def disconnect(self) -> None:
        """Close the connection."""

    @abstractmethod
    def send(self, data: bytes) -> bool:
        """Send raw bytes. Return True on success."""

    @abstractmethod
    def receive(self, timeout: float = 1.0) -> Optional[RadioPacket]:
        """Receive one packet or None on timeout."""

    @abstractmethod
    def is_connected(self) -> bool:
        """Return current connection state."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable backend name."""