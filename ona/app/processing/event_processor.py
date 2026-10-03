"""Event enrichment."""
from __future__ import annotations


class EventProcessor:
    """Enrich events with severity, priority, deduplication.

    Phase B: interface only. Implementation in Phase G.
    """

    def process(self, message: object) -> object:
        raise NotImplementedError