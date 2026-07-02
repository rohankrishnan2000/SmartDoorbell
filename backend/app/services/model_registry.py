from dataclasses import dataclass

from backend.app.models.domain import ModelVersion


@dataclass(frozen=True)
class PromotionDecision:
    allowed: bool
    reason: str
    required_followups: list[str]


class ModelRegistryGuard:
    def evaluate_promotion(self, model: ModelVersion, target_stage: str) -> PromotionDecision:
        metrics = model.metrics or {}
        safety = model.safety_review or {}
        followups: list[str] = []
        if metrics.get("precision_package_theft", 0) < 0.82:
            followups.append("Improve package-theft precision above 0.82.")
        if metrics.get("false_unlock_rate", 1) > 0.005:
            followups.append("Reduce false unlock rate below 0.5%.")
        if not safety.get("privacy_reviewed"):
            followups.append("Complete privacy review for visitor-recognition behavior.")
        if not safety.get("rollback_plan"):
            followups.append("Attach rollback plan before production promotion.")

        if target_stage == "production" and followups:
            return PromotionDecision(False, "Production gate blocked by model governance checks.", followups)
        return PromotionDecision(True, f"Model can move from {model.stage} to {target_stage}.", followups)

