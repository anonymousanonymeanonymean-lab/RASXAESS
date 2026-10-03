"""Serial LoRa radio backend (SX1262 via ESP32 UART bridge).

Phase B: interface stub. Full implementation in later phase.
"""
from __future__ import annotations

import logging
from typing import Optional

from app.communication.radio_interface import RadioInterface, RadioPacket
from app.config.settings import RadioConfig

logger = logging.getLogger(__name__)


class SerialLoRaRadio(RadioInterface):
    """LoRa radio over USB/UART."""

    def __init__(self, config: RadioConfig) -> None:
        self._config = config
        self._connected = False

    @property
    def name(self) -> str:
        return "SerialLoRaRadio"

    def connect(self) -> bool:
        # TODO Phase H: open serial port, handshake with ESP32 bridge.
        logger.warning("SerialLoRaRadio.connect() not implemented yet")
        return False

    def disconnect(self) -> None:
        self._connected = False

    def send(self, data: bytes) -> bool:
        raise NotImplementedError("SerialLoRaRadio.send not implemented yet")

    def receive(self, timeout: float = 1.0) -> Optional[RadioPacket]:
        raise NotImplementedError("SerialLoRaRadio.receive not implemented yet")

    def is_connected(self) -> bool:
        return self._connected