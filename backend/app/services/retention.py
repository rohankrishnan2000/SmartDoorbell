from datetime import UTC, datetime, timedelta
from typing import Any

from backend.app.models.domain import DataRetentionPolicy


class RetentionPlanner:
    def build_plan(self, policy: DataRetentionPolicy) -> dict[str, Any]:
        now = datetime.now(UTC)
        media_cutoff = now - timedelta(days=policy.media_days)
        event_cutoff = now - timedelta(days=policy.event_days)
        audit_cutoff = now - timedelta(days=policy.audit_days)
        if policy.legal_hold:
            actions = [
                {
                    "action": "skip_delete",
                    "target": "all",
                    "reason": "Legal hold is enabled; retention job will report only.",
                }
            ]
        else:
            actions = [
                {"action": policy.deletion_mode, "target": "media", "older_than": media_cutoff.isoformat()},
                {"action": "archive", "target": "events", "older_than": event_cutoff.isoformat()},
                {"action": "compress", "target": "audit_logs", "older_than": audit_cutoff.isoformat()},
            ]
        return {
            "policy_name": policy.name,
            "media_cutoff_days": policy.media_days,
            "event_cutoff_days": policy.event_days,
            "audit_cutoff_days": policy.audit_days,
            "legal_hold": policy.legal_hold,
            "planned_actions": actions,
        }

