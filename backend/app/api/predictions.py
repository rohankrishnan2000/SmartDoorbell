from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.ml.occupancy import OccupancyPredictor
from backend.app.models.domain import Event, OccupancyPrediction
from backend.app.schemas.domain import OccupancyRead

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/occupancy", response_model=OccupancyRead)
def occupancy(device_id: str = "front_door_01", db: Session = Depends(get_db)) -> OccupancyRead:
    since = datetime.now(UTC) - timedelta(hours=6)
    recent_events = db.query(Event).filter(Event.device_id == device_id, Event.timestamp >= since).count()
    unlocks = db.query(Event).filter(Event.device_id == device_id, Event.lock_action == "unlock").count()
    result = OccupancyPredictor().predict(datetime.now(UTC), recent_events, unlocks)
    db.add(OccupancyPrediction(device_id=device_id, **{k: v for k, v in result.items() if k != "narrative"}))
    db.commit()
    return OccupancyRead(**result)

