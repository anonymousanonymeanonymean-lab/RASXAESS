"""Beacon Simulator — Phase B stub.

Injects packets into a SimulatedRadio. Full Beacon Protocol encoding in Phase D.
"""
from __future__ import annotations

import logging
import time

from app.communication.radio_interface import RadioPacket
from app.communication.simulated_radio import SimulatedRadio

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [BEACON-SIM] %(message)s")
    radio = SimulatedRadio()
    radio.connect()
    logger.info("Beacon simulator ready (stub, no encoding yet)")
    # Phase D will emit real Beacon Protocol v1.0 frames here.
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()