"""Event ingestion + aging classification."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, select

from app.aging import AgingPolicy
from app.models import Event

logger = logging.getLogger(__name__)


class EventService:
    def __init__(self, policy: AgingPolicy) -> None:
        self.policy = policy

    def upsert(self, session: Session, data: dict[str, Any]) -> tuple[Event, bool]:
        """Insert or update. Returns (event, is_new)."""
        event_id = data["message_id"]
        existing = session.get(Event, event_id)
        is_new = existing is None

        ts = data["event_timestamp"]
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        rts = data.get("received_timestamp") or datetime.now(timezone.utc)
        if isinstance(rts, str):
            rts = datetime.fromisoformat(rts.replace("Z", "+00:00"))

        state, _ = self.policy.classify(ts)

        ev = Event(
            event_id=event_id,
            mission_id=data.get("mission_id", "mission_default"),
            source_id=data.get("source_id", "UNKNOWN"),
            source_type=data.get("source_type", "BEACON"),
            event_type=data.get("event_type", "UNKNOWN"),
            event_timestamp=ts,
            received_timestamp=rts,
            frame_id=data.get("frame_id"),
            coordinate_reference=data.get("coordinate_reference", "ENU"),
            local_x=data.get("local_x"),
            local_y=data.get("local_y"),
            local_z=data.get("local_z"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            altitude=data.get("altitude"),
            severity=data.get("severity", "MEDIUM"),
            confidence=float(data.get("confidence", 0.0)),
            priority=data.get("priority", "NORMAL"),
            status=state.value,
            payload_json=json.dumps(data.get("payload", {})),
        )
        session.merge(ev)
        session.commit()
        session.refresh(ev)
        return ev, is_new

    def list(self, session: Session,
             mission_id: str | None = None,
             limit: int = 500) -> list[Event]:
        stmt = select(Event).order_by(Event.event_timestamp.desc()).limit(limit)
        if mission_id:
            stmt = stmt.where(Event.mission_id == mission_id)
        return list(session.exec(stmt))

    def to_dict(self, ev: Event) -> dict[str, Any]:
        state, age = self.policy.classify(ev.event_timestamp)
        try:
            payload = json.loads(ev.payload_json)
        except Exception:
            payload = {}
        return {
            "event_id": ev.event_id,
            "mission_id": ev.mission_id,
            "source_id": ev.source_id,
            "source_type": ev.source_type,
            "event_type": ev.event_type,
            "event_timestamp": ev.event_timestamp.isoformat(),
            "received_timestamp": ev.received_timestamp.isoformat(),
            "age_seconds": age,
            "status": state.value,
            "frame_id": ev.frame_id,
            "coordinate_reference": ev.coordinate_reference,
            "local_x": ev.local_x,
            "local_y": ev.local_y,
            "local_z": ev.local_z,
            "latitude": ev.latitude,
            "longitude": ev.longitude,
            "altitude": ev.altitude,
            "severity": ev.severity,
            "confidence": ev.confidence,
            "priority": ev.priority,
            "payload": payload,
        }