from dataclasses import dataclass
from typing import Any

from backend.app.models.domain import Event, NotificationRule


@dataclass(frozen=True)
class NotificationPlanResult:
    rule_name: str
    channels: list[dict[str, Any]]
    escalation_minutes: int | None
    reason: str


class NotificationRouter:
    def plan(self, event: Event, rules: list[NotificationRule]) -> list[NotificationPlanResult]:
        plans: list[NotificationPlanResult] = []
        for rule in rules:
            if not rule.enabled:
                continue
            match = rule.match or {}
            min_risk = float(match.get("min_risk_score", 0))
            severities = set(match.get("severities", []))
            event_types = set(match.get("event_types", []))
            risk_matches = event.risk_score >= min_risk
            severity_matches = bool(severities and event.severity in severities)
            if not risk_matches and not severity_matches:
                continue
            if severities and event.severity not in severities:
                continue
            if event_types and event.event_type not in event_types:
                continue
            escalation_minutes = rule.escalation.get("after_minutes") if rule.escalation else None
            reason = f"{event.event_type} matched {rule.name} at risk {event.risk_score:.0%}."
            plans.append(
                NotificationPlanResult(
                    rule_name=rule.name,
                    channels=rule.channels,
                    escalation_minutes=escalation_minutes,
                    reason=reason,
                )
            )
        return plans
