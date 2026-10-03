"""Store-and-forward outbox service.

Phase B: interface only. Implementation in Phase G.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class OutboxService:
    """Persistent queue with retry, backoff, priority."""

    def enqueue(self, message_id: str, topic: str, payload: bytes,
                priority: str = "NORMAL") -> None:
        raise NotImplementedError

    def process_pending(self) -> None:
        raise NotImplementedError