"""Writer Simulator — Phase B stub.

Emits MAVLink 2 frames in later phases.
"""
from __future__ import annotations

import logging
import time

from app.communication.simulated_radio import SimulatedRadio

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [WRITER-SIM] %(message)s")
    radio = SimulatedRadio()
    radio.connect()
    logger.info("Writer simulator ready (stub, no MAVLink yet)")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()