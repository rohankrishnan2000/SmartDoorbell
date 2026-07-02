from edge.events.decision_engine import EventDecisionEngine
from edge.inference.yolo_model import DetectionResult


def detection(label: str, confidence: float) -> DetectionResult:
    return DetectionResult(label=label, confidence=confidence, bbox=(0, 0, 100, 100))


def test_decision_engine_filters_low_confidence_detections():
    decision = EventDecisionEngine(min_confidence=0.8).decide(
        [detection("person", 0.79), detection("package", 0.6)]
    )

    assert decision.should_notify is False
    assert decision.event_type == "motion_only"
    assert decision.severity == "info"
    assert decision.reasons == []


def test_decision_engine_flags_person_near_waiting_package():
    decision = EventDecisionEngine(min_confidence=0.65).decide(
        [detection("person", 0.91), detection("package", 0.82)],
        package_waiting=True,
    )

    assert decision.should_notify is True
    assert decision.event_type == "package_theft_risk"
    assert decision.severity == "warning"
    assert "person_near_waiting_package" in decision.reasons
    assert decision.risk_score >= 0.62


def test_decision_engine_suppresses_notifications_during_cooldown():
    engine = EventDecisionEngine(min_confidence=0.65, cooldown_seconds=60)

    first = engine.decide([detection("person", 0.9)])
    second = engine.decide([detection("person", 0.9)])

    assert first.should_notify is True
    assert second.should_notify is False
    assert second.reasons == ["person_in_roi"]
