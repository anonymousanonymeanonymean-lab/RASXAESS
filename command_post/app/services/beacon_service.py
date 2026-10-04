"""Beacon upsert from events/status."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, select

from app.models import Beacon, NetworkLink


class BeaconService:
    def upsert(self, session: Session, data: dict[str, Any]) -> Beacon:
        beacon_id = data["beacon_id"]
        existing = session.get(Beacon, beacon_id)
        b = existing or Beacon(
            beacon_id=beacon_id,
            mission_id=data.get("mission_id", "mission_default"),
        )
        b.status = data.get("status", b.status)
        b.frame_id = data.get("frame_id", b.frame_id)
        b.local_x = data.get("local_x", b.local_x)
        b.local_y = data.get("local_y", b.local_y)
        b.local_z = data.get("local_z", b.local_z)
        b.battery = data.get("battery", b.battery)
        b.hop_count = data.get("hop_count", b.hop_count)
        b.parent_id = data.get("parent_id", b.parent_id)
        b.rssi = data.get("rssi", b.rssi)
        b.snr = data.get("snr", b.snr)
        b.last_seen = datetime.now(timezone.utc)
        session.merge(b)
        session.commit()
        session.refresh(b)
        return b

    def list(self, session: Session) -> list[Beacon]:
        return list(session.exec(select(Beacon)))

    def upsert_link(self, session: Session, data: dict[str, Any]) -> NetworkLink:
        link_id = f"{data['source_id']}->{data['target_id']}"
        existing = session.get(NetworkLink, link_id)
        lk = existing or NetworkLink(
            link_id=link_id,
            mission_id=data.get("mission_id", "mission_default"),
            source_id=data["source_id"],
            target_id=data["target_id"],
        )
        lk.rssi = data.get("rssi", lk.rssi)
        lk.snr = data.get("snr", lk.snr)
        lk.status = data.get("status", "UP")
        lk.last_seen = datetime.now(timezone.utc)
        session.merge(lk)
        session.commit()
        session.refresh(lk)
        return lk

    def list_links(self, session: Session) -> list[NetworkLink]:
        return list(session.exec(select(NetworkLink)))