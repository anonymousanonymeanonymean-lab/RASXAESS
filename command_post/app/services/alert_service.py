"""Alert creation from high/critical events."""
from __future__ import annotations

import uuid
import logging

from sqlmodel import Session, select

from app.models import Alert, Event

logger = logging.getLogger(__name__)

AUTO_ALERT_SEVERITIES = {"HIGH", "CRITICAL"}


class AlertService:
    def maybe_create(self, session: Session, ev: Event) -> Alert | None:
        if ev.severity not in AUTO_ALERT_SEVERITIES:
            return None

        # Dedup by event_id
        stmt = select(Alert).where(Alert.event_id == ev.event_id)
        if session.exec(stmt).first() is not None:
            return None

        alert = Alert(
            alert_id=str(uuid.uuid4()),
            mission_id=ev.mission_id,
            event_id=ev.event_id,
            severity=ev.severity,
            message=f"{ev.event_type} detected by {ev.source_id}",
            status="OPEN",
        )
        session.add(alert)
        session.commit()
        session.refresh(alert)
        return alert

    def list(self, session: Session, mission_id: str | None = None) -> list[Alert]:
        stmt = select(Alert).order_by(Alert.created_at.desc()).limit(200)
        if mission_id:
            stmt = stmt.where(Alert.mission_id == mission_id)
        return list(session.exec(stmt))

    def ack(self, session: Session, alert_id: str) -> Alert | None:
        a = session.get(Alert, alert_id)
        if a is None:
            return None
        a.status = "ACK"
        session.add(a)
        session.commit()
        session.refresh(a)
        return a

    def resolve(self, session: Session, alert_id: str) -> Alert | None:
        a = session.get(Alert, alert_id)
        if a is None:
            return None
        a.status = "RESOLVED"
        session.add(a)
        session.commit()
        session.refresh(a)
        return a