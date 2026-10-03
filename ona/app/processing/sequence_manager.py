"""Per-source sequence tracking."""
from __future__ import annotations


class SequenceManager:
    """Track per-source sequence numbers and detect gaps/out-of-order.

    Phase B: interface only. Implementation in Phase F.
    """

    def check(self, source_id: str, boot_id: str, sequence_number: int) -> bool:
        raise NotImplementedError