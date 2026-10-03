"""Device Registry service.

Phase B: in-memory registry loaded from config. Persistence in Phase C.
"""
from __future__ import annotations

import logging

from app.config.settings import DeviceConfig

logger = logging.getLogger(__name__)


class DeviceRegistry:
    """Authorized devices."""

    def __init__(self, devices: list[DeviceConfig]) -> None:
        self._devices = {d.device_id: d for d in devices}

    def is_known(self, device_id: str) -> bool:
        return device_id in self._devices

    def get(self, device_id: str) -> DeviceConfig | None:
        return self._devices.get(device_id)

    def all(self) -> list[DeviceConfig]:
        return list(self._devices.values())