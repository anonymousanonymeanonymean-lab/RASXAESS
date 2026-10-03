"""Command Post Simulator — Phase B stub.

Subscribes to MQTT topics in Phase H.
"""
from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [CMD-POST-SIM] %(message)s")
    logger.info("Command Post simulator ready (stub, no MQTT yet)")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()