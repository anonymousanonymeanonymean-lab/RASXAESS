"""Internal data model: MissionMessage and related dataclasses.

This model is independent of any radio protocol.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from app.utils.time import utc_now


@dataclass
class MissionMessage:
    """Protocol-independent internal representation of a mission message."""

    # IDENTITY
    message_id: str
    mission_id: str
    source_id: str
    source_type: str          # BEACON | WRITER
    protocol: str             # BEACON_V1 | MAVLINK2
    protocol_version: str

    # SEQUENCING
    boot_id: str
    sequence_number: int

    # TIME
    event_timestamp: datetime
    received_timestamp: datetime = field(default_factory=utc_now)

    # FRAME
    frame_id: Optional[str] = None
    coordinate_reference: str = "ENU"   # ENU | WGS84

    # POSITION
    local_x: Optional[float] = None
    local_y: Optional[float] = None
    local_z: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None

    # EVENT
    event_type: Optional[str] = None
    severity: Optional[str] = None
    confidence: Optional[float] = None

    # PROCESSING
    integrity_status: str = "OK"
    processing_status: str = "ACCEPTED"
    validation_status: str = "VALID"
    priority: str = "NORMAL"

    # RAW
    raw_payload: bytes = b""

    # MISC
    payload: dict[str, Any] = field(default_factory=dict)