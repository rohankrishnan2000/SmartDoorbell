from sqlalchemy.orm import Session

from backend.app.models.domain import (
    ApiKey,
    AuditLog,
    DeadLetterMessage,
    Device,
    EdgeCommand,
    FeatureFlag,
    IncidentCase,
    JobRun,
    LabelingTask,
    ModelVersion,
    NotificationRule,
    Organization,
    SloMetric,
    UserAccount,
)


def build_internal_overview(db: Session) -> dict:
    org = db.query(Organization).first()
    latest_slo = db.query(SloMetric).order_by(SloMetric.created_at.desc()).first()
    return {
        "organization": {
            "id": org.id if org else "demo",
            "name": org.name if org else "Sentinel Demo",
            "plan": org.plan if org else "prototype",
            "users": db.query(UserAccount).count(),
            "api_keys": db.query(ApiKey).count(),
        },
        "fleet": {
            "devices": db.query(Device).count(),
            "queued_commands": db.query(EdgeCommand).filter(EdgeCommand.status == "queued").count(),
            "feature_flags": db.query(FeatureFlag).count(),
        },
        "security": {
            "open_incidents": db.query(IncidentCase).filter(IncidentCase.status != "resolved").count(),
            "audit_events": db.query(AuditLog).count(),
            "dead_letters": db.query(DeadLetterMessage).count(),
            "notification_rules": db.query(NotificationRule).count(),
        },
        "mlops": {
            "registered_models": db.query(ModelVersion).count(),
            "open_labeling_tasks": db.query(LabelingTask).filter(LabelingTask.status == "open").count(),
        },
        "operations": {
            "job_runs": db.query(JobRun).count(),
            "latest_slo": {
                "service": latest_slo.service if latest_slo else "none",
                "target": latest_slo.target if latest_slo else 0,
                "actual": latest_slo.actual if latest_slo else 0,
                "burn_rate": latest_slo.burn_rate if latest_slo else 0,
            },
        },
    }

