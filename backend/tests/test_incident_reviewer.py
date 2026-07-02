from backend.app.agents.incident_reviewer import IncidentReviewerAgent
from backend.app.models.domain import Event


def test_incident_reviewer_queues_training_for_high_risk_event():
    event = Event(
        id="evt_high_risk",
        device_id="front_door_01",
        event_type="package_theft_risk",
        risk_score=0.82,
    )

    run = IncidentReviewerAgent().review(event)

    assert run.next_action == "queue_training_sample"
    assert run.metadata_json["self_correction"] is True
    assert run.metadata_json["proposed_label"] == "package_theft_risk"
    assert "human label" in run.recommendation


def test_incident_reviewer_monitors_low_risk_event():
    event = Event(
        id="evt_low_risk",
        device_id="front_door_01",
        event_type="visitor_detected",
        risk_score=0.2,
    )

    run = IncidentReviewerAgent().review(event)

    assert run.next_action == "monitor"
    assert run.metadata_json["self_correction"] is False
    assert run.recommendation == "Store event and continue monitoring."
