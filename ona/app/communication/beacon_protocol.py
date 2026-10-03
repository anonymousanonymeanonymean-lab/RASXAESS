"""Beacon Protocol v1.0 — encoder/decoder interface.

Phase B: interface stub only. Full binary implementation in Phase D.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class BeaconFrame:
    """Decoded Beacon Protocol v1.0 frame."""
    version: int
    message_type: int
    source_id: str
    boot_id: str
    sequence_number: int
    timestamp: int
    payload: bytes
    crc: int


class BeaconProtocol:
    """Encoder/decoder for Beacon Protocol v1.0."""

    def decode(self, raw: bytes) -> Optional[BeaconFrame]:
        raise NotImplementedError("BeaconProtocol.decode not implemented yet")

    def encode(self, frame: BeaconFrame) -> bytes:
        raise NotImplementedError("BeaconProtocol.encode not implemented yet")