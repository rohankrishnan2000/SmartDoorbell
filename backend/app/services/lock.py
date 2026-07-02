from backend.app.core.config import get_settings


class AugustLockService:
    """Adapter boundary for August OAuth/API calls.

    The current implementation is a safe dry-run that records intent without touching a real lock.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.state = "locked"

    async def command(self, action: str, reason: str, probability_home: float) -> dict:
        accepted = action in {"lock", "unlock"}
        if action == "unlock" and probability_home < 0.55:
            accepted = False
            summary = "Unlock blocked by occupancy safety gate."
        else:
            self.state = "locked" if action == "lock" else "unlocked"
            summary = f"Dry-run August {action} accepted for reason: {reason}."
        return {
            "lock_id": self.settings.august_lock_id,
            "action": action,
            "accepted": accepted,
            "state": self.state,
            "safety_summary": summary,
        }

