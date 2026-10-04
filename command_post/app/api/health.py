from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    ctx = request.app.state.ctx
    return {
        "status": "ok",
        "mqtt_connected": ctx.mqtt.is_connected(),
        "mission_id": ctx.settings.mission_id,
        "ws_clients": len(ctx.ws._clients),  # noqa
    }