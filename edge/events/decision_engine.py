from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from edge.inference.yolo_model import DetectionResult


@dataclass
class Decision:
    should_notify: bool
    event_type: str
    severity: str
    risk_score: float
    reasons: list[str]


class EventDecisionEngine:
    def __init__(self, min_confidence: float = 0.65, cooldown_seconds: int = 45) -> None:
        self.min_confidence = min_confidence
        self.cooldown = timedelta(seconds=cooldown_seconds)
        self.last_notification_at: datetime | None = None

    def decide(self, detections: list[DetectionResult], package_waiting: bool = False) -> Decision:
        now = datetime.now(UTC)
        filtered = [d for d in detections if d.confidence >= self.min_confidence]
        labels = {d.label for d in filtered}
        reasons: list[str] = []
        risk = max([d.confidence for d in filtered] or [0.0]) * 0.45

        if "person" in labels:
            reasons.append("person_in_roi")
            risk += 0.18
        if "package" in labels:
            reasons.append("package_visible")
        if package_waiting and "person" in labels:
            reasons.append("person_near_waiting_package")
            risk += 0.22

        in_cooldown = self.last_notification_at is not None and now - self.last_notification_at < self.cooldown
        should_notify = bool(reasons) and not in_cooldown
        if should_notify:
            self.last_notification_at = now

        event_type = "package_theft_risk" if package_waiting and "person" in labels else "visitor_detected" if "person" in labels else "motion_only"
        severity = "warning" if risk >= 0.62 else "info"
        return Decision(should_notify, event_type, severity, round(min(risk, 0.99), 2), reasons)

