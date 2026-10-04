"""Mission state."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Session

from app.models import Mission


class MissionService:
    def ensure(self, session: Session, mission_id: str,
               name: str, environment: str) -> Mission:
        m = session.get(Mission, mission_id)
        if m is None:
            m = Mission(id=mission_id, name=name, environment=environment)
            session.add(m)
            session.commit()
            session.refresh(m)
        return m

    def get(self, session: Session, mission_id: str) -> Mission | None:
        return session.get(Mission, mission_id)

    def set_status(self, session: Session, mission_id: str, status: str) -> Mission | None:
        m = session.get(Mission, mission_id)
        if m is None:
            return None
        m.status = status
        m.updated_at = datetime.now(timezone.utc)
        session.add(m)
        session.commit()
        session.refresh(m)
        return m