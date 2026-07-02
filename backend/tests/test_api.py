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


def test_create_event_scores_package_theft_risk():
    response = client.post(
        "/events",
        json={
            "device_id": "front_door_01",
            "event_type": "motion_only",
            "confidence": 0.9,
            "detections": [
                {"label": "person", "confidence": 0.9, "bbox": [100, 50, 300, 700]},
            ],
            "metadata": {"package_waiting": True},
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["event_type"] == "package_theft_risk"
    assert payload["severity"] in {"warning", "critical"}
    assert payload["notification_sent"] is True
    assert payload["detections"][0]["label"] == "person"


def test_missing_event_returns_404():
    response = client.get("/events/not-a-real-event")
    assert response.status_code == 404
