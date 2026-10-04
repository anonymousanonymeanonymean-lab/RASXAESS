"""Async MQTT ingestion. Bridges broker → services → WebSocket."""
from __future__ import annotations

import asyncio
import json
import logging
import ssl
from typing import Callable, Optional

import paho.mqtt.client as mqtt

from app.config import Settings

logger = logging.getLogger(__name__)


class MQTTIngestor:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Optional[mqtt.Client] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._connected = False
        self._handlers: dict[str, Callable[[dict], None]] = {}

    # ---------- API ----------
    def register(self, topic_suffix: str, handler: Callable[[dict], None]) -> None:
        """Register handler for `ona/v1/{mission}/<suffix>`."""
        self._handlers[topic_suffix] = handler

    def is_connected(self) -> bool:
        return self._connected

    # ---------- Lifecycle ----------
    async def start(self) -> None:
        if not self._settings.mqtt_enabled or not self._settings.mqtt_broker:
            logger.warning("MQTT disabled or broker empty — skipping")
            return

        self._loop = asyncio.get_running_loop()
        client_id = self._settings.mqtt_client_id
        try:
            self._client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=client_id,
                protocol=mqtt.MQTTv5,
            )
        except Exception:
            self._client = mqtt.Client(client_id=client_id)

        if self._settings.mqtt_username:
            self._client.username_pw_set(
                self._settings.mqtt_username,
                self._settings.mqtt_password,
            )

        if self._settings.mqtt_tls:
            ctx = ssl.create_default_context()
            if self._settings.mqtt_ca_cert:
                ctx.load_verify_locations(self._settings.mqtt_ca_cert)
            else:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            self._client.tls_set_context(ctx)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

        try:
            self._client.connect_async(
                self._settings.mqtt_broker, self._settings.mqtt_port, 60
            )
            self._client.loop_start()
            logger.info("MQTT connecting to %s:%d",
                        self._settings.mqtt_broker, self._settings.mqtt_port)
        except Exception as exc:
            logger.error("MQTT connect_async failed: %s", exc)

    async def stop(self) -> None:
        if self._client is not None:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:
                pass

    # ---------- Callbacks ----------
    def _topic_base(self) -> str:
        return f"ona/v1/{self._settings.mission_id}"

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        self._connected = True
        base = self._topic_base()
        for suffix in self._handlers.keys():
            topic = f"{base}/{suffix}"
            client.subscribe(topic, qos=self._settings.mqtt_qos)
            logger.info("Subscribed to %s", topic)

    def _on_disconnect(self, client, userdata, rc, properties=None):
        self._connected = False
        logger.warning("MQTT disconnected rc=%s", rc)

    def _on_message(self, client, userdata, msg):
        suffix = msg.topic.rsplit("/", 1)[-1]
        handler = self._handlers.get(suffix)
        if handler is None:
            return
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as exc:
            logger.warning("Bad JSON on %s: %s", msg.topic, exc)
            return

        # Dispatch into the asyncio loop
        if self._loop is not None:
            self._loop.call_soon_threadsafe(handler, payload)

    # ---------- Publish ----------
    def publish(self, topic_suffix: str, payload: dict) -> None:
        if self._client is None or not self._connected:
            return
        topic = f"{self._topic_base()}/{topic_suffix}"
        self._client.publish(topic, json.dumps(payload), qos=self._settings.mqtt_qos)