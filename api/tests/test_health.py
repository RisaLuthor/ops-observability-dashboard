import importlib
from fastapi.testclient import TestClient


def test_health(monkeypatch):
    monkeypatch.setenv("OPS_API_TOKEN", "testtoken")  # harmless, keeps config consistent

    import src.main
    importlib.reload(src.main)

    client = TestClient(src.main.app)

    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True