from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.domain import (
    AuditLog,
    DataRetentionPolicy,
    Device,
    EdgeCommand,
    FeatureFlag,
    IncidentCase,
    LabelingTask,
    Membership,
    ModelVersion,
    NotificationRule,
    Organization,
    UserAccount,
)
from backend.app.models.domain import Event
from backend.app.schemas.internal import (
    AccessDecisionRead,
    AuditLogRead,
    CreateIncidentCase,
    EdgeCommandRead,
    EdgeCommandRequest,
    FeatureFlagRead,
    IncidentCaseRead,
    InternalOverview,
    LabelingTaskRead,
    ModelVersionRead,
    NotificationPlan,
    PromoteModelRequest,
    RetentionPlanRead,
)
from backend.app.services.fleet_ops import FleetCommandCenter
from backend.app.services.internal_overview import build_internal_overview
from backend.app.services.model_registry import ModelRegistryGuard
from backend.app.services.notification_router import NotificationRouter
from backend.app.services.policy_engine import PolicyEngine
from backend.app.services.retention import RetentionPlanner

router = APIRouter(prefix="/internal", tags=["internal-platform"])


@router.get("/overview", response_model=InternalOverview)
def overview(db: Session = Depends(get_db)) -> InternalOverview:
    return InternalOverview(**build_internal_overview(db))


@router.get("/audit", response_model=list[AuditLogRead])
def audit_log(limit: int = 25, db: Session = Depends(get_db)) -> list[AuditLogRead]:
    rows = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).all()
    return [
        AuditLogRead(
            id=row.id,
            action=row.action,
            resource_type=row.resource_type,
            resource_id=row.resource_id,
            actor_id=row.actor_id,
            created_at=row.created_at,
            after=row.after,
        )
        for row in rows
    ]


@router.get("/feature-flags", response_model=list[FeatureFlagRead])
def feature_flags(db: Session = Depends(get_db)) -> list[FeatureFlagRead]:
    flags = db.query(FeatureFlag).order_by(FeatureFlag.key).all()
    return [
        FeatureFlagRead(
            key=flag.key,
            enabled=flag.enabled,
            rollout_percent=flag.rollout_percent,
            owner=flag.owner,
            rules=flag.rules,
        )
        for flag in flags
    ]


@router.get("/incidents", response_model=list[IncidentCaseRead])
def incidents(db: Session = Depends(get_db)) -> list[IncidentCaseRead]:
    rows = db.query(IncidentCase).order_by(desc(IncidentCase.created_at)).all()
    return [
        IncidentCaseRead(
            id=row.id,
            title=row.title,
            severity=row.severity,
            status=row.status,
            assigned_to=row.assigned_to,
            sla_due_at=row.sla_due_at,
            tags=row.tags,
            resolution=row.resolution,
        )
        for row in rows
    ]


@router.post("/incidents", response_model=IncidentCaseRead, status_code=201)
def create_incident(payload: CreateIncidentCase, db: Session = Depends(get_db)) -> IncidentCaseRead:
    org = db.query(Organization).first()
    if not org:
        raise HTTPException(status_code=400, detail="Organization seed data missing")
    case = IncidentCase(
        organization_id=org.id,
        event_id=payload.event_id,
        title=payload.title,
        severity=payload.severity,
        status="open",
        assigned_to="ops-oncall",
        sla_due_at=datetime.now(UTC) + timedelta(hours=2 if payload.severity == "critical" else 12),
        tags=payload.tags,
    )
    db.add(case)
    db.add(
        AuditLog(
            organization_id=org.id,
            actor_id="operator-demo",
            action="incident.create",
            resource_type="incident_case",
            resource_id=case.id,
            after={"title": case.title, "severity": case.severity, "tags": case.tags},
        )
    )
    db.commit()
    db.refresh(case)
    return IncidentCaseRead(
        id=case.id,
        title=case.title,
        severity=case.severity,
        status=case.status,
        assigned_to=case.assigned_to,
        sla_due_at=case.sla_due_at,
        tags=case.tags,
        resolution=case.resolution,
    )


@router.get("/notifications/plan/{event_id}", response_model=list[NotificationPlan])
def notification_plan(event_id: str, db: Session = Depends(get_db)) -> list[NotificationPlan]:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    plans = NotificationRouter().plan(event, db.query(NotificationRule).all())
    return [NotificationPlan(**plan.__dict__) for plan in plans]


@router.get("/model-registry", response_model=list[ModelVersionRead])
def model_registry(db: Session = Depends(get_db)) -> list[ModelVersionRead]:
    rows = db.query(ModelVersion).order_by(desc(ModelVersion.created_at)).all()
    return [
        ModelVersionRead(
            id=row.id,
            name=row.name,
            version=row.version,
            stage=row.stage,
            artifact_uri=row.artifact_uri,
            metrics=row.metrics,
            safety_review=row.safety_review,
        )
        for row in rows
    ]


@router.post("/model-registry/promote")
def promote_model(payload: PromoteModelRequest, db: Session = Depends(get_db)) -> dict:
    model = db.get(ModelVersion, payload.model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model version not found")
    decision = ModelRegistryGuard().evaluate_promotion(model, payload.target_stage)
    if decision.allowed:
        model.stage = payload.target_stage
        model.promoted_by = payload.approver
    org = db.query(Organization).first()
    if org:
        db.add(
            AuditLog(
                organization_id=org.id,
                actor_id=payload.approver,
                action="model.promote",
                resource_type="model_version",
                resource_id=model.id,
                after={
                    "allowed": decision.allowed,
                    "target_stage": payload.target_stage,
                    "followups": decision.required_followups,
                },
            )
        )
    db.commit()
    return {
        "allowed": decision.allowed,
        "reason": decision.reason,
        "required_followups": decision.required_followups,
        "stage": model.stage,
    }


@router.get("/labeling/tasks", response_model=list[LabelingTaskRead])
def labeling_tasks(queue: str | None = None, db: Session = Depends(get_db)) -> list[LabelingTaskRead]:
    query = db.query(LabelingTask).order_by(desc(LabelingTask.created_at))
    if queue:
        query = query.filter(LabelingTask.queue == queue)
    return [
        LabelingTaskRead(
            id=row.id,
            event_id=row.event_id,
            queue=row.queue,
            priority=row.priority,
            status=row.status,
            suggested_label=row.suggested_label,
            human_label=row.human_label,
            instructions=row.instructions,
        )
        for row in query.all()
    ]


@router.post("/fleet/devices/{device_id}/commands", response_model=EdgeCommandRead, status_code=201)
def queue_edge_command(
    device_id: str,
    payload: EdgeCommandRequest,
    db: Session = Depends(get_db),
) -> EdgeCommandRead:
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    try:
        command = FleetCommandCenter().queue_command(
            device,
            payload.command_type,
            payload.payload,
            payload.issued_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.add(command)
    db.commit()
    db.refresh(command)
    return EdgeCommandRead(
        id=command.id,
        device_id=command.device_id,
        command_type=command.command_type,
        payload=command.payload,
        status=command.status,
        issued_by=command.issued_by,
        issued_at=command.issued_at,
    )


@router.get("/retention/plan", response_model=RetentionPlanRead)
def retention_plan(db: Session = Depends(get_db)) -> RetentionPlanRead:
    policy = db.query(DataRetentionPolicy).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Retention policy not found")
    return RetentionPlanRead(**RetentionPlanner().build_plan(policy))


@router.get("/access/decision", response_model=AccessDecisionRead)
def access_decision(
    email: str = Query(default="ops@sentinel.local"),
    action: str = Query(default="command"),
    resource: str = Query(default="locks"),
    db: Session = Depends(get_db),
) -> AccessDecisionRead:
    user = db.query(UserAccount).filter(UserAccount.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    membership = db.query(Membership).filter(Membership.user_id == user.id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    decision = PolicyEngine().decide(
        actor=user.email,
        role=membership.role,
        action=action,
        resource=resource,
        extra_scopes=membership.scopes,
    )
    return AccessDecisionRead(**decision.__dict__)

