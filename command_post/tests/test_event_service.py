from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Session

from app.aging import AgingPolicy
from app.db import init_db
from app.services.event_service import EventService


def test_event_upsert(tmp_path):
    db = str(tmp_path / "t.db")
    engine = init_db(db)
    svc = EventService(AgingPolicy())

    data = {
        "message_id": "m1",
        "mission_id": "mission_default",
        "source_id": "BEACON_01",
        "event_type": "GAS",
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
        "severity": "HIGH",
        "confidence": 0.9,
    }
    with Session(engine) as s:
        ev, is_new = svc.upsert(s, data)
        assert is_new is True
        assert ev.event_id == "m1"

        # Duplicate
        ev2, is_new2 = svc.upsert(s, data)
        assert is_new2 is False
        assert ev2.event_id == "m1"