"""Database models."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON, Text


def _utcnow() -> datetime:
    from datetime import timezone
    return datetime.now(timezone.utc)


class Mission(SQLModel, table=True):
    id: str = Field(primary_key=True)             # mission_id
    name: str
    environment: str
    status: str = "active"
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class Event(SQLModel, table=True):
    event_id: str = Field(primary_key=True)       # = message_id
    mission_id: str = Field(index=True)
    source_id: str = Field(index=True)
    source_type: str = "BEACON"
    event_type: str = Field(index=True)
    event_timestamp: datetime = Field(index=True)
    received_timestamp: datetime = Field(default_factory=_utcnow)
    frame_id: Optional[str] = None
    coordinate_reference: str = "ENU"
    local_x: Optional[float] = None
    local_y: Optional[float] = None
    local_z: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    severity: str = "MEDIUM"
    confidence: float = 0.0
    priority: str = "NORMAL"
    status: str = "ACTIVE"                        # computed aging
    payload_json: str = Field(default="{}", sa_column=Column(Text))


class Robot(SQLModel, table=True):
    robot_id: str = Field(primary_key=True)
    mission_id: str = Field(index=True)
    robot_type: str                                # WRITER | EXECUTOR
    status: str = "UNKNOWN"
    frame_id: Optional[str] = None
    local_x: Optional[float] = None
    local_y: Optional[float] = None
    local_z: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    battery: Optional[float] = None
    last_seen: datetime = Field(default_factory=_utcnow)
    communication_status: str = "UNKNOWN"


class Beacon(SQLModel, table=True):
    beacon_id: str = Field(primary_key=True)
    mission_id: str = Field(index=True)
    status: str = "UNKNOWN"
    frame_id: Optional[str] = None
    local_x: Optional[float] = None
    local_y: Optional[float] = None
    local_z: Optional[float] = None
    battery: Optional[float] = None
    hop_count: Optional[int] = None
    parent_id: Optional[str] = None
    rssi: Optional[float] = None
    snr: Optional[float] = None
    last_seen: datetime = Field(default_factory=_utcnow)


class NetworkLink(SQLModel, table=True):
    link_id: str = Field(primary_key=True)
    mission_id: str = Field(index=True)
    source_id: str
    target_id: str
    rssi: Optional[float] = None
    snr: Optional[float] = None
    status: str = "UP"
    last_seen: datetime = Field(default_factory=_utcnow)


class Alert(SQLModel, table=True):
    alert_id: str = Field(primary_key=True)
    mission_id: str = Field(index=True)
    event_id: Optional[str] = Field(default=None, index=True)
    severity: str = Field(index=True)
    message: str
    status: str = "OPEN"                           # OPEN | ACK | RESOLVED
    created_at: datetime = Field(default_factory=_utcnow)