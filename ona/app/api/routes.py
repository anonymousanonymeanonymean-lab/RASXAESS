"""FastAPI routes.

Phase B: minimal health/status endpoints. Full endpoints in later phases.
"""
from __future__ import annotations

from fastapi import APIRouter, Request

from app import __version__
from app.api.schemas import HealthResponse, StatusResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    state = request.app.state.ona
    snap = state.health.snapshot(
        radio_connected=state.radio.is_connected(),
        mqtt_connected=state.mqtt.is_connected() if state.mqtt else False,
        database_ok=state.db.health_check(),
    )
    return HealthResponse(
        status="ok",
        uptime_seconds=snap.uptime_seconds,
        radio_connected=snap.radio_connected,
        mqtt_connected=snap.mqtt_connected,
        database_ok=snap.database_ok,
    )


@router.get("/status", response_model=StatusResponse)
async def status(request: Request) -> StatusResponse:
    state = request.app.state.ona
    return StatusResponse(
        version=__version__,
        mission_id=state.settings.mission.id,
        environment=state.settings.mission.environment,
        details={
            "radio_backend": state.radio.name,
            "devices": [d.device_id for d in state.device_registry.all()],
        },
    )