from fastapi.testclient import TestClient


def test_health():
    from src.main import app
    client = TestClient(app)

    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True
