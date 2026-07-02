from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class InternalOverview(BaseModel):
    organization: dict[str, Any]
    fleet: dict[str, Any]
    security: dict[str, Any]
    mlops: dict[str, Any]
    operations: dict[str, Any]


class AuditLogRead(BaseModel):
    id: str
    action: str
    resource_type: str
    resource_id: str
    actor_id: str | None
    created_at: datetime
    after: dict[str, Any]


class FeatureFlagRead(BaseModel):
    key: str
    enabled: bool
    rollout_percent: int
    owner: str
    rules: dict[str, Any]


class IncidentCaseRead(BaseModel):
    id: str
    title: str
    severity: str
    status: str
    assigned_to: str | None
    sla_due_at: datetime | None
    tags: list[str]
    resolution: str | None


class CreateIncidentCase(BaseModel):
    event_id: str | None = None
    title: str
    severity: str = "info"
    tags: list[str] = []


class NotificationPlan(BaseModel):
    rule_name: str
    channels: list[dict[str, Any]]
    escalation_minutes: int | None
    reason: str


class ModelVersionRead(BaseModel):
    id: str
    name: str
    version: str
    stage: str
    artifact_uri: str
    metrics: dict[str, Any]
    safety_review: dict[str, Any]


class PromoteModelRequest(BaseModel):
    model_id: str
    target_stage: str = Field(pattern="^(staging|production|archived)$")
    approver: str = "ml-platform-demo"


class LabelingTaskRead(BaseModel):
    id: str
    event_id: str
    queue: str
    priority: str
    status: str
    suggested_label: str
    human_label: str | None
    instructions: str


class EdgeCommandRequest(BaseModel):
    command_type: str
    payload: dict[str, Any] = {}
    issued_by: str = "operator-demo"


class EdgeCommandRead(BaseModel):
    id: str
    device_id: str
    command_type: str
    payload: dict[str, Any]
    status: str
    issued_by: str
    issued_at: datetime


class RetentionPlanRead(BaseModel):
    policy_name: str
    media_cutoff_days: int
    event_cutoff_days: int
    audit_cutoff_days: int
    legal_hold: bool
    planned_actions: list[dict[str, Any]]


class AccessDecisionRead(BaseModel):
    actor: str
    action: str
    resource: str
    allowed: bool
    matched_scope: str | None
    reason: str

