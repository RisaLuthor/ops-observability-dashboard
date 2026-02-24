import os
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

def test_post_event_requires_token(monkeypatch):
    monkeypatch.setenv("OPS_API_TOKEN", "testtoken")

    r = client.post("/events", json={
        "level": "INFO",
        "type": "OPS",
        "service": "api",
        "message": "hello",
        "meta": {"k": "v"},
    })
    assert r.status_code == 401

def test_post_event_and_list(monkeypatch, tmp_path):
    monkeypatch.setenv("OPS_API_TOKEN", "testtoken")
    monkeypatch.setenv("EVENTS_DB_PATH", str(tmp_path / "events.db"))

    # reload store module with new env
    import importlib
    from src import events_store
    importlib.reload(events_store)
    from src.events_store import event_store  # noqa: F401

    r = client.post(
        "/events",
        headers={"X-Ops-Token": "testtoken"},
        json={
            "level": "WARN",
            "type": "AUDIT",
            "service": "api",
            "message": "something happened",
            "meta": {"request_id": "abc123"},
        },
    )
    assert r.status_code == 200
    created = r.json()
    assert created["level"] == "WARN"
    assert created["service"] == "api"
    assert created["meta"]["type"] == "AUDIT"

    g = client.get("/events?limit=10")
    assert g.status_code == 200
    items = g.json()
    assert isinstance(items, list)
