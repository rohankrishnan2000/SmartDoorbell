from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrainingProposal:
    dataset_path: Path
    reason: str
    priority: str
    suggested_action: str


class SelfCorrectionLoop:
    """Turns agent critiques and human labels into retraining proposals."""

    def propose(self, event_type: str, risk_score: float, human_label: str | None) -> TrainingProposal:
        mismatch = human_label is not None and human_label != event_type
        priority = "high" if mismatch or risk_score >= 0.75 else "medium"
        reason = "label_mismatch" if mismatch else "high_uncertainty_or_high_risk"
        return TrainingProposal(
            dataset_path=Path("data/training/doorbell-feedback.jsonl"),
            reason=reason,
            priority=priority,
            suggested_action="fine_tune_theft_classifier" if priority == "high" else "add_to_eval_set",
        )

