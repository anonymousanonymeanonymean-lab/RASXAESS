"""ONA application entry point.

Phase B: boots configuration, logging, database, radio stub, REST API.
Radio/MQTT/processing loops are wired but not yet active.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app import __version__
from app.api.routes import router
from app.communication.mqtt_client import MQTTClient
from app.communication.radio_interface import RadioInterface
from app.communication.serial_radio import SerialLoRaRadio
from app.communication.simulated_radio import SimulatedRadio
from app.config.logging import configure_logging
from app.config.settings import Settings, load_settings
from app.database.database import Database
from app.services.device_service import DeviceRegistry
from app.services.health_service import HealthMonitor

logger = logging.getLogger(__name__)


def _build_radio(settings: Settings) -> RadioInterface:
    backend = settings.radio.backend.lower()
    if backend == "serial":
        return SerialLoRaRadio(settings.radio)
    return SimulatedRadio()


class ONAState:
    """Holds runtime singletons attached to FastAPI app.state."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.db = Database(settings.database.path)
        self.radio = _build_radio(settings)
        self.mqtt = MQTTClient(settings.mqtt)
        self.device_registry = DeviceRegistry(settings.devices)
        self.health = HealthMonitor()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    configure_logging(settings.log_level)

    logger.info("ONA v%s starting (component=ONA)", __version__)
    state = ONAState(settings)
    app.state.ona = state

    # Bootstrap
    state.db.connect()
    if not state.db.health_check():
        logger.error("Database health check failed at boot")
    state.radio.connect()
    # MQTT connection is attempted but not required for boot.
    # Full outbox/sync loop arrives in Phase G/H.

    logger.info("ONA booted (component=ONA, event=BOOT, status=OK)")
    try:
        yield
    finally:
        logger.info("ONA shutting down (component=ONA, event=SHUTDOWN)")
        state.radio.disconnect()
        if state.mqtt.is_connected():
            state.mqtt.disconnect()
        state.db.close()


def create_app() -> FastAPI:
    app = FastAPI(title="ONA — Outside Network Area",
                  version=__version__,
                  lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()


def run() -> None:
    settings = load_settings()
    configure_logging(settings.log_level)
    uvicorn.run(
        "app.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=False,
        log_config=None,
    )


if __name__ == "__main__":
    run()