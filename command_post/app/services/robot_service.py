"""Robot upsert from positions topic."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, select

from app.models import Robot


class RobotService:
    def upsert(self, session: Session, data: dict[str, Any]) -> Robot:
        robot_id = data["source_id"] if "robot_id" not in data else data["robot_id"]
        existing = session.get(Robot, robot_id)
        r = existing or Robot(
            robot_id=robot_id,
            mission_id=data.get("mission_id", "mission_default"),
            robot_type=data.get("robot_type", "WRITER"),
        )
        r.status = data.get("status", r.status)
        r.frame_id = data.get("frame_id", r.frame_id)
        r.local_x = data.get("local_x", r.local_x)
        r.local_y = data.get("local_y", r.local_y)
        r.local_z = data.get("local_z", r.local_z)
        r.latitude = data.get("latitude", r.latitude)
        r.longitude = data.get("longitude", r.longitude)
        r.battery = data.get("battery", r.battery)
        r.communication_status = data.get("communication_status", "ONLINE")
        r.last_seen = datetime.now(timezone.utc)
        session.merge(r)
        session.commit()
        session.refresh(r)
        return r

    def list(self, session: Session) -> list[Robot]:
        return list(session.exec(select(Robot)))