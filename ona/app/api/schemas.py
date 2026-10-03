"""Pydantic response schemas for the REST API."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    radio_connected: bool
    mqtt_connected: bool
    database_ok: bool


class StatusResponse(BaseModel):
    version: str
    mission_id: str
    environment: str
    details: dict[str, Any] = {}