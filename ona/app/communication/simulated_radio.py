"""Simulated radio backend.

Uses an in-process queue. Simulators push packets here.
Phase B: functional for injection of test packets.
"""
from __future__ import annotations

import logging
import queue
from typing import Optional

from app.communication.radio_interface import RadioInterface, RadioPacket

logger = logging.getLogger(__name__)


class SimulatedRadio(RadioInterface):
    """In-memory simulated radio."""

    def __init__(self) -> None:
        self._connected = False
        self._rx: "queue.Queue[RadioPacket]" = queue.Queue()
        self._tx: "queue.Queue[bytes]" = queue.Queue()

    @property
    def name(self) -> str:
        return "SimulatedRadio"

    def connect(self) -> bool:
        self._connected = True
        logger.info("SimulatedRadio connected")
        return True

    def disconnect(self) -> None:
        self._connected = False
        logger.info("SimulatedRadio disconnected")

    def send(self, data: bytes) -> bool:
        if not self._connected:
            return False
        self._tx.put(data)
        return True

    def receive(self, timeout: float = 1.0) -> Optional[RadioPacket]:
        try:
            return self._rx.get(timeout=timeout)
        except queue.Empty:
            return None

    def is_connected(self) -> bool:
        return self._connected

    # ---- Simulation helpers -------------------------------------------

    def inject(self, packet: RadioPacket) -> None:
        """Push a packet into the receive queue (for simulators/tests)."""
        self._rx.put(packet)

    def drain_tx(self) -> list[bytes]:
        """Return and clear all transmitted packets (for simulators/tests)."""
        out: list[bytes] = []
        while True:
            try:
                out.append(self._tx.get_nowait())
            except queue.Empty:
                break
        return out