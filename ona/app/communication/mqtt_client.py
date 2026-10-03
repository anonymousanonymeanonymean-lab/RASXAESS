"""MQTT/TLS client interface.

Phase B: interface stub. Full implementation in Phase H.
"""
from __future__ import annotations

import logging
from typing import Optional

from app.config.settings import MqttConfig

logger = logging.getLogger(__name__)


class MQTTClient:
    """MQTT over TLS client for ONA → Command Post."""

    def __init__(self, config: MqttConfig) -> None:
        self._config = config
        self._connected = False

    def connect(self) -> bool:
        logger.warning("MQTTClient.connect() not implemented yet")
        return False

    def disconnect(self) -> None:
        self._connected = False

    def publish(self, topic: str, payload: bytes, qos: int = 1) -> bool:
        raise NotImplementedError("MQTTClient.publish not implemented yet")

    def is_connected(self) -> bool:
        return self._connected