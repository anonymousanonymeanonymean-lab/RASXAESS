"""ID generation utilities."""
from __future__ import annotations

import uuid


def new_message_id() -> str:
    """Generate a globally unique message identifier."""
    return str(uuid.uuid4())


def new_boot_id() -> str:
    """Generate a new boot identifier for a device session."""
    return uuid.uuid4().hex[:8]