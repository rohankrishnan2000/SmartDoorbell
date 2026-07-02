from fastapi import APIRouter

from backend.app.schemas.domain import LockCommand, LockCommandResult
from backend.app.services.lock import AugustLockService

router = APIRouter(prefix="/locks", tags=["locks"])
lock_service = AugustLockService()


@router.post("/front-door/command", response_model=LockCommandResult)
async def command_lock(payload: LockCommand) -> LockCommandResult:
    probability_home = 0.78 if payload.require_home_prediction else 1.0
    result = await lock_service.command(payload.action, payload.reason, probability_home)
    return LockCommandResult(**result)

