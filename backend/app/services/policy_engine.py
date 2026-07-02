from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AccessDecision:
    actor: str
    action: str
    resource: str
    allowed: bool
    matched_scope: str | None
    reason: str


ROLE_SCOPES = {
    "owner": {"*"},
    "admin": {
        "events:read",
        "events:write",
        "devices:read",
        "devices:write",
        "locks:command",
        "incidents:write",
        "models:promote",
        "audit:read",
    },
    "operator": {
        "events:read",
        "devices:read",
        "locks:command",
        "incidents:write",
        "labels:write",
    },
    "viewer": {"events:read", "devices:read"},
    "ml_engineer": {"events:read", "labels:write", "models:read", "models:promote"},
}


class PolicyEngine:
    def allowed_scopes(self, role: str, extra_scopes: list[str] | None = None) -> set[str]:
        scopes = set(ROLE_SCOPES.get(role, set()))
        scopes.update(extra_scopes or [])
        return scopes

    def decide(
        self,
        actor: str,
        role: str,
        action: str,
        resource: str,
        extra_scopes: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> AccessDecision:
        scopes = self.allowed_scopes(role, extra_scopes)
        if "*" in scopes:
            return AccessDecision(actor, action, resource, True, "*", "Owner scope grants access.")

        required = f"{resource}:{action}"
        if required in scopes:
            return AccessDecision(actor, action, resource, True, required, "Exact scope matched.")

        if context and context.get("break_glass") and role in {"admin", "operator"}:
            return AccessDecision(
                actor,
                action,
                resource,
                True,
                "break_glass",
                "Emergency break-glass path accepted and must be audited.",
            )

        return AccessDecision(actor, action, resource, False, None, f"Missing required scope {required}.")


class FeatureFlagEvaluator:
    def is_enabled(self, key: str, enabled: bool, rollout_percent: int, subject_id: str) -> bool:
        if not enabled:
            return False
        bucket = sum(ord(char) for char in f"{key}:{subject_id}") % 100
        return bucket < rollout_percent

