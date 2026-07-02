from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.domain import Device
from backend.app.schemas.domain import DeviceRead
from backend.app.services.serialization import device_to_read

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=list[DeviceRead])
def list_devices(db: Session = Depends(get_db)) -> list[DeviceRead]:
    return [device_to_read(device) for device in db.query(Device).all()]


@router.patch("/{device_id}/config", response_model=DeviceRead)
def update_config(device_id: str, config: dict, db: Session = Depends(get_db)) -> DeviceRead:
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.config = {**device.config, **config}
    db.commit()
    db.refresh(device)
    return device_to_read(device)

