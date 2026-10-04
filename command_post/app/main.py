"""Command Post — FastAPI entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app import __version__
from app.aging import AgingPolicy
from app.api import alerts, beacons, events, health, mission, network, robots, ws
from app.config import load_settings
from app.db import get_engine, init_db
from app.logging_config import configure_logging
from app.mqtt_client import MQTTIngestor
from app.services.alert_service import AlertService
from app.services.beacon_service import BeaconService
from app.services.event_service import EventService
from app.services.mission_service import MissionService
from app.services.robot_service import RobotService
from app.ws_manager import WSManager

logger = logging.getLogger(__name__)


class AppContext:
    def __init__(self) -> None:
        self.settings = load_settings()
        self.policy = AgingPolicy(
            new_s=self.settings.aging_new_seconds,
            active_s=self.settings.aging_active_seconds,
            recent_s=self.settings.aging_recent_seconds,
            stale_s=self.settings.aging_stale_seconds,
        )
        self.events = EventService(self.policy)
        self.alerts = AlertService()
        self.robots = RobotService()
        self.beacons = BeaconService()
        self.mission = MissionService()
        self.ws = WSManager()
        self.mqtt = MQTTIngestor(self.settings)


async def _handle_event(ctx: AppContext, payload: dict) -> None:
    with Session(get_engine()) as session:
        ev, is_new = ctx.events.upsert(session, payload)
        alert = ctx.alerts.maybe_create(session, ev)
        ev_dict = ctx.events.to_dict(ev)
    await ctx.ws.broadcast("NEW_EVENT" if is_new else "EVENT_UPDATED", ev_dict)
    if alert is not None:
        await ctx.ws.broadcast("ALERT_CREATED", alert.model_dump(mode="json"))
    # ACK back to ONA
    ctx.mqtt.publish("ack", {
        "ack_message_id": ev.event_id,
        "ack_status": "RECEIVED",
        "ack_timestamp": ev.received_timestamp.isoformat(),
    })


async def _handle_positions(ctx: AppContext, payload: dict) -> None:
    with Session(get_engine()) as session:
        r = ctx.robots.upsert(session, payload)
    await ctx.ws.broadcast("ROBOT_UPDATED", r.model_dump(mode="json"))


async def _handle_status(ctx: AppContext, payload: dict) -> None:
    """Status topic: may contain beacon info."""
    if "beacon_id" in payload:
        with Session(get_engine()) as session:
            b = ctx.beacons.upsert(session, payload)
        await ctx.ws.broadcast("BEACON_UPDATED", b.model_dump(mode="json"))
    else:
        await ctx.ws.broadcast("MISSION_UPDATED", payload)


async def _handle_devices(ctx: AppContext, payload: dict) -> None:
    if "source_id" in payload and "target_id" in payload:
        with Session(get_engine()) as session:
            lk = ctx.beacons.upsert_link(session, payload)
        await ctx.ws.broadcast("NETWORK_UPDATED", lk.model_dump(mode="json"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    ctx = AppContext()
    configure_logging(ctx.settings.log_level)
    logger.info("Command Post v%s starting (mission=%s)",
                __version__, ctx.settings.mission_id)

    init_db(ctx.settings.db_path)

    with Session(get_engine()) as session:
        ctx.mission.ensure(session, ctx.settings.mission_id,
                           ctx.settings.mission_name,
                           ctx.settings.environment)

    # Register MQTT handlers. Because paho callback runs in a thread,
    # we schedule the coroutine on the loop.
    import asyncio
    loop = asyncio.get_running_loop()

    def wrap(fn):
        def _dispatch(payload: dict) -> None:
            asyncio.run_coroutine_threadsafe(fn(ctx, payload), loop)
        return _dispatch

    ctx.mqtt.register("events",    wrap(_handle_event))
    ctx.mqtt.register("positions", wrap(_handle_positions))
    ctx.mqtt.register("status",    wrap(_handle_status))
    ctx.mqtt.register("devices",   wrap(_handle_devices))

    await ctx.mqtt.start()
    app.state.ctx = ctx
    try:
        yield
    finally:
        await ctx.mqtt.stop()
        logger.info("Command Post shutting down")


def create_app() -> FastAPI:
    app = FastAPI(title="Command Post — The Living Map",
                  version=__version__, lifespan=lifespan)

    # CORS: applied after settings load inside lifespan.
    # Use a small middleware that reads from app.state lazily.
    @app.middleware("http")
    async def _cors(request, call_next):
        resp = await call_next(request)
        origin = request.headers.get("origin", "")
        ctx = getattr(app.state, "ctx", None)
        if ctx and origin in ctx.settings.cors_origins:
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Access-Control-Allow-Credentials"] = "true"
            resp.headers["Access-Control-Allow-Headers"] = "*"
            resp.headers["Access-Control-Allow-Methods"] = "*"
        return resp

    app.include_router(health.router, tags=["health"])
    app.include_router(mission.router, prefix="/api", tags=["mission"])
    app.include_router(events.router, prefix="/api", tags=["events"])
    app.include_router(robots.router, prefix="/api", tags=["robots"])
    app.include_router(beacons.router, prefix="/api", tags=["beacons"])
    app.include_router(alerts.router, prefix="/api", tags=["alerts"])
    app.include_router(network.router, prefix="/api", tags=["network"])
    app.include_router(ws.router)
    return app


app = create_app()