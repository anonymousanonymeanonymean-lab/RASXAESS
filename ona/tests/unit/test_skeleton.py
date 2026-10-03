"""Phase B skeleton tests: configuration, DB, health, API."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.config.settings import Settings, load_settings
from app.database.database import Database
from app.main import create_app


def test_settings_load_defaults() -> None:
    s = load_settings()
    assert isinstance(s, Settings)
    assert s.mission.id
    assert s.radio.backend in ("simulated", "serial")


def test_database_health_check(tmp_db_path: str) -> None:
    db = Database(tmp_db_path)
    db.connect()
    assert db.health_check() is True
    db.close()


def test_health_endpoint(tmp_db_path: str) -> None:
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert "uptime_seconds" in body


def test_status_endpoint() -> None:
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/status")
        assert r.status_code == 200
        body = r.json()
        assert "version" in body
        assert "mission_id" in body