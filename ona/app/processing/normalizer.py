"""Normalizer: protocol message → internal MissionMessage."""
from __future__ import annotations


class MessageNormalizer:
    """Convert protocol-specific messages into MissionMessage.

    Phase B: interface only. Implementation in Phase F.
    """

    def normalize(self, raw: object) -> object:
        raise NotImplementedError