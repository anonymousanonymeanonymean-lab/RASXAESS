from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint():
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"


def test_events_endpoint_empty():
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/api/events")
        assert r.status_code == 200
        assert r.json() == []