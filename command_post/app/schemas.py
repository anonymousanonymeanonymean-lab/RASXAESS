"""Pydantic schemas for API + MQTT payloads."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class EventIn(BaseModel):
    message_id: str
    mission_id: str
    source_id: str
    source_type: str = "BEACON"
    message_type: str = "EVENT"
    boot_id: Optional[str] = None
    sequence_number: Optional[int] = None
    event_timestamp: datetime
    received_timestamp: Optional[datetime] = None
    frame_id: Optional[str] = None
    coordinate_reference: str = "ENU"
    local_x: Optional[float] = None
    local_y: Optional[float] = None
    local_z: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    event_type: str
    severity: str = "MEDIUM"
    confidence: float = 0.0
    priority: str = "NORMAL"
    payload: dict[str, Any] = Field(default_factory=dict)


class EventOut(BaseModel):
    event_id: str
    mission_id: str
    source_id: str
    event_type: str
    event_timestamp: datetime
    received_timestamp: datetime
    age_seconds: float
    status: str
    frame_id: Optional[str]
    coordinate_reference: str
    local_x: Optional[float]
    local_y: Optional[float]
    local_z: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    altitude: Optional[float]
    severity: str
    confidence: float
    priority: str
    payload: dict[str, Any] = {}


class RobotOut(BaseModel):
    robot_id: str
    robot_type: str
    status: str
    frame_id: Optional[str]
    local_x: Optional[float]
    local_y: Optional[float]
    local_z: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    battery: Optional[float]
    last_seen: datetime
    communication_status: str


class BeaconOut(BaseModel):
    beacon_id: str
    status: str
    frame_id: Optional[str]
    local_x: Optional[float]
    local_y: Optional[float]
    local_z: Optional[float]
    battery: Optional[float]
    hop_count: Optional[int]
    parent_id: Optional[str]
    rssi: Optional[float]
    snr: Optional[float]
    last_seen: datetime


class AlertOut(BaseModel):
    alert_id: str
    mission_id: str
    event_id: Optional[str]
    severity: str
    message: str
    status: str
    created_at: datetime


class LinkOut(BaseModel):
    link_id: str
    source_id: str
    target_id: str
    rssi: Optional[float]
    snr: Optional[float]
    status: str
    last_seen: datetime


class MissionOut(BaseModel):
    id: str
    name: str
    environment: str
    status: str
    created_at: datetime
    updated_at: datetime