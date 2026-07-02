from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.app.agents.incident_reviewer import IncidentReviewerAgent
from backend.app.db.session import get_db
from backend.app.ml.risk import RobberyRiskModel
from backend.app.models.domain import Detection, Event
from backend.app.schemas.domain import AgentReviewRead, EventCreate, EventRead
from backend.app.services.serialization import event_to_read

router = APIRouter(prefix="/events", tags=["events"])
risk_model = RobberyRiskModel()


@router.get("", response_model=list[EventRead])
def list_events(limit: int = 20, db: Session = Depends(get_db)) -> list[EventRead]:
    events = db.query(Event).order_by(desc(Event.timestamp)).limit(limit).all()
    return [event_to_read(event) for event in events]


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: str, db: Session = Depends(get_db)) -> EventRead:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event_to_read(event)


@router.post("", response_model=EventRead, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)) -> EventRead:
    assessment = risk_model.score(
        [d.model_dump() for d in payload.detections],
        hour=datetime.now().hour,
        package_waiting=bool(payload.metadata.get("package_waiting", False)),
    )
    event = Event(
        device_id=payload.device_id,
        event_type=assessment.event_type,
        severity=assessment.severity,
        confidence=payload.confidence,
        risk_score=assessment.risk_score,
        summary=assessment.summary,
        snapshot_path=payload.snapshot_path,
        clip_path=payload.clip_path,
        notification_sent=assessment.risk_score >= 0.55,
        metadata_json=payload.metadata,
    )
    db.add(event)
    db.flush()
    for detection in payload.detections:
        x1, y1, x2, y2 = detection.bbox
        db.add(
            Detection(
                event_id=event.id,
                label=detection.label,
                confidence=detection.confidence,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                track_id=detection.track_id,
            )
        )
    db.commit()
    db.refresh(event)
    return event_to_read(event)


@router.post("/{event_id}/agent-review", response_model=AgentReviewRead)
def review_event(event_id: str, db: Session = Depends(get_db)) -> AgentReviewRead:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    run = IncidentReviewerAgent().review(event)
    db.add(run)
    db.commit()
    db.refresh(run)
    return AgentReviewRead(
        id=run.id,
        agent_name=run.agent_name,
        status=run.status,
        recommendation=run.recommendation,
        critique=run.critique,
        next_action=run.next_action,
        metadata=run.metadata_json,
    )


@router.websocket("/ws")
async def events_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        await websocket.send_json({"type": "connected", "message": "Doorbell event stream ready"})
        while True:
            await websocket.receive_text()
            await websocket.send_json({"type": "heartbeat", "message": "No live camera connected yet"})
    except WebSocketDisconnect:
        return

