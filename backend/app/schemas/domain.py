from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DetectionRead(BaseModel):
    label: str
    confidence: float
    bbox: list[int] = Field(min_length=4, max_length=4)
    track_id: str | None = None


class EventCreate(BaseModel):
    device_id: str
    event_type: str
    confidence: float = 0.0
    detections: list[DetectionRead] = []
    snapshot_path: str | None = None
    clip_path: str | None = None
    metadata: dict[str, Any] = {}


class EventRead(BaseModel):
    id: str
    device_id: str
    event_type: str
    severity: str
    timestamp: datetime
    confidence: float
    risk_score: float
    summary: str
    snapshot_path: str | None
    clip_path: str | None
    notification_sent: bool
    lock_action: str | None
    detections: list[DetectionRead]
    metadata: dict[str, Any]


class DeviceRead(BaseModel):
    id: str
    name: str
    location: str
    camera_source: str
    status: str
    firmware_version: str
    battery_percent: int
    temperature_c: float
    config: dict[str, Any]
    last_seen_at: datetime


class OccupancyRead(BaseModel):
    probability_home: float
    confidence: float
    horizon_minutes: int
    features: dict[str, Any]
    narrative: str


class LockCommand(BaseModel):
    action: str = Field(pattern="^(lock|unlock)$")
    reason: str = "manual dashboard command"
    require_home_prediction: bool = True


class LockCommandResult(BaseModel):
    lock_id: str
    action: str
    accepted: bool
    state: str
    safety_summary: str


class AgentReviewRead(BaseModel):
    id: str
    agent_name: str
    status: str
    recommendation: str
    critique: str
    next_action: str
    metadata: dict[str, Any]

