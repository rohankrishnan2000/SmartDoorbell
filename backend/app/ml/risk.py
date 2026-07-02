from dataclasses import dataclass


@dataclass(frozen=True)
class RiskAssessment:
    event_type: str
    severity: str
    risk_score: float
    summary: str


class RobberyRiskModel:
    """Deterministic stand-in for a future temporal/video model."""

    suspicious_labels = {"person", "backpack", "crowbar", "vehicle"}

    def score(self, detections: list[dict], hour: int, package_waiting: bool = False) -> RiskAssessment:
        labels = {d["label"] for d in detections}
        max_conf = max([d.get("confidence", 0.0) for d in detections] or [0.0])
        after_dark = hour >= 21 or hour <= 5
        person_count = sum(1 for d in detections if d["label"] == "person")

        score = max_conf * 0.45
        score += 0.18 if after_dark else 0.0
        score += 0.2 if package_waiting and "person" in labels else 0.0
        score += 0.1 if person_count > 1 else 0.0
        score = min(round(score, 2), 0.99)

        if "package" in labels and "person" in labels:
            event_type = "delivery_detected"
        elif package_waiting and "person" in labels:
            event_type = "package_theft_risk"
        elif score >= 0.72:
            event_type = "robbery_risk"
        elif "person" in labels:
            event_type = "visitor_detected"
        else:
            event_type = "motion_only"

        severity = "critical" if score >= 0.78 else "warning" if score >= 0.55 else "info"
        summary = f"{event_type.replace('_', ' ').title()} with {score:.0%} risk confidence."
        return RiskAssessment(event_type, severity, score, summary)

