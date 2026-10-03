"""Coordinate transformation manager.

CRITICAL RULE: never invent GPS coordinates.
Only transform LOCAL(ENU) → WGS84 if the frame relationship is validated.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from app.config.settings import FrameConfig

logger = logging.getLogger(__name__)


@dataclass
class CoordinateResult:
    frame_id: str
    coordinate_reference: str  # "ENU" | "WGS84"
    local_x: Optional[float] = None
    local_y: Optional[float] = None
    local_z: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    uncertainty_m: Optional[float] = None


class CoordinateManager:
    """Manages coordinate frames and transformations.

    Phase B: interface only. Implementation in Phase F.
    """

    def __init__(self, frames: list[FrameConfig]) -> None:
        self._frames = {f.frame_id: f for f in frames}

    def register_frame(self, frame: FrameConfig) -> None:
        self._frames[frame.frame_id] = frame

    def transform(self, frame_id: str,
                  local_x: float, local_y: float, local_z: float) -> CoordinateResult:
        """Transform local ENU coords to WGS84 if possible, else keep local."""
        raise NotImplementedError