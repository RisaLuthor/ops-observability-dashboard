import importlib
from fastapi.testclient import TestClient


def make_client(monkeypatch, *, token="testtoken", db_path=None):
    # Set env FIRST
    monkeypatch.setenv("OPS_API_TOKEN", token)
    if db_path is not None:
        monkeypatch.setenv("EVENTS_DB_PATH", str(db_path))

    # Import via package path (stable in CI when running from repo root)
    import api.src.events_store as events_store
    import api.src.main as main

    # Reload so modules re-read env vars
    importlib.reload(events_store)
    importlib.reload(main)

    return TestClient(main.app)


def test_post_event_requires_token(monkeypatch, tmp_path):
    client = make_client(monkeypatch, db_path=tmp_path / "events.db")

    r = client.post(
        "/events",
        json={
            "level": "INFO",
            "type": "OPS",
            "service": "api",
            "message": "hello",
            "meta": {"k": "v"},
        },
    )
    assert r.status_code == 401


def test_post_event_and_list(monkeypatch, tmp_path):
    client = make_client(monkeypatch, db_path=tmp_path / "events.db")

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
    assert len(items) >= 1