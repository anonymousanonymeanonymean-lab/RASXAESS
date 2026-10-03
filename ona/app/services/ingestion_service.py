"""Main ingestion service.

Phase B: interface only. Wiring in Phase F.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class IngestionService:
    """Receive → Validate → Normalize → Process → Store → Outbox."""

    def handle_radio_packet(self, raw: bytes, source_hint: str | None = None) -> None:
        raise NotImplementedError