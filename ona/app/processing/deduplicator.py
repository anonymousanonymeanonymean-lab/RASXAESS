"""Duplicate detection."""
from __future__ import annotations


class Deduplicator:
    """Detect duplicate messages using message identity.

    message identity = mission_id + source_id + boot_id + sequence_number

    Phase B: interface only. Implementation in Phase F.
    """

    def is_duplicate(self, mission_id: str, source_id: str,
                     boot_id: str, sequence_number: int) -> bool:
        raise NotImplementedError