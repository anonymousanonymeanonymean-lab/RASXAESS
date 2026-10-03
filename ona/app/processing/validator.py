"""Message validation pipeline interface."""
from __future__ import annotations

from enum import Enum


class ValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID_CRC = "INVALID_CRC"
    UNKNOWN_SOURCE = "UNKNOWN_SOURCE"
    DUPLICATE = "DUPLICATE"
    STALE = "STALE"
    INVALID_SCHEMA = "INVALID_SCHEMA"
    INVALID_COORDINATE = "INVALID_COORDINATE"
    INVALID_SEQUENCE = "INVALID_SEQUENCE"
    UNSUPPORTED_PROTOCOL = "UNSUPPORTED_PROTOCOL"


class MessageValidator:
    """Validates incoming messages through the pipeline.

    Phase B: interface only. Implementation in Phase F.
    """

    def validate(self, raw: bytes, source_hint: str | None = None) -> ValidationStatus:
        raise NotImplementedError