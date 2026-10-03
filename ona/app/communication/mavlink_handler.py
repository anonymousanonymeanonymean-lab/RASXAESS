"""MAVLink 2 handler interface.

Phase B: interface stub. Full integration in Phase E.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class MAVLinkHandler:
    """Receives, decodes and validates MAVLink 2 messages."""

    def decode(self, raw: bytes) -> Optional[dict[str, Any]]:
        raise NotImplementedError("MAVLinkHandler.decode not implemented yet")