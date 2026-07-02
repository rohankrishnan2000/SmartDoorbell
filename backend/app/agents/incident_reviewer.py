from backend.app.models.domain import AgentRun, Event


class IncidentReviewerAgent:
    """Mock agent that explains and critiques high-risk events."""

    def review(self, event: Event) -> AgentRun:
        if event.risk_score >= 0.65:
            recommendation = "Notify owner, keep lock engaged, preserve clip, and ask for a human label."
            critique = "The model may over-weight night lighting and dwell time; compare against similar benign visits."
            next_action = "queue_training_sample"
        else:
            recommendation = "Store event and continue monitoring."
            critique = "No immediate correction required."
            next_action = "monitor"

        return AgentRun(
            event_id=event.id,
            agent_name="incident-reviewer",
            recommendation=recommendation,
            critique=critique,
            next_action=next_action,
            metadata_json={
                "self_correction": next_action == "queue_training_sample",
                "proposed_label": event.event_type,
                "risk_score": event.risk_score,
            },
        )

