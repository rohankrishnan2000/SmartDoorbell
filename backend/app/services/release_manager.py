from dataclasses import dataclass
from enum import StrEnum


class ReleaseRisk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ReleaseCandidate:
    name: str
    version: str
    services: list[str]
    migrations: list[str]
    feature_flags: list[str]
    model_versions: list[str]
    risk: ReleaseRisk


@dataclass(frozen=True)
class ReleaseGateResult:
    allowed: bool
    candidate: str
    blockers: list[str]
    rollout_plan: list[str]


class ReleaseManager:
    def evaluate(self, candidate: ReleaseCandidate) -> ReleaseGateResult:
        blockers: list[str] = []
        if candidate.migrations and "backup_verified" not in candidate.feature_flags:
            blockers.append("Database migrations require backup_verified flag.")
        if candidate.risk == ReleaseRisk.HIGH and "canary_enabled" not in candidate.feature_flags:
            blockers.append("High-risk release requires canary_enabled flag.")
        if candidate.model_versions and "model_rollback_ready" not in candidate.feature_flags:
            blockers.append("Model release requires rollback artifact.")

        rollout_plan = [
            "deploy_to_internal_demo",
            "run_smoke_tests",
            "enable_5_percent_canary",
            "watch_slo_burn_rate_for_30_minutes",
            "expand_to_50_percent",
            "promote_to_full_rollout",
        ]
        return ReleaseGateResult(
            allowed=not blockers,
            candidate=f"{candidate.name}@{candidate.version}",
            blockers=blockers,
            rollout_plan=rollout_plan,
        )

