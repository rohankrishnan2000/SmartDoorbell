from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_events_seeded():
    response = client.get("/events")
    assert response.status_code == 200
    assert len(response.json()) >= 1

