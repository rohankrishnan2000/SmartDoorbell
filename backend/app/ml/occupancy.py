from datetime import datetime
from math import cos, pi


class OccupancyPredictor:
    """Feature-based placeholder for a future household-presence model."""

    def predict(self, when: datetime, recent_events: int, door_unlocks_today: int) -> dict:
        hour = when.hour + when.minute / 60
        evening_signal = (cos((hour - 19) / 24 * 2 * pi) + 1) / 2
        morning_signal = (cos((hour - 7) / 24 * 2 * pi) + 1) / 2
        activity_signal = min(recent_events / 12, 1) * 0.18
        unlock_signal = min(door_unlocks_today / 4, 1) * 0.16
        probability = min(0.94, max(0.08, 0.22 + evening_signal * 0.3 + morning_signal * 0.08 + activity_signal + unlock_signal))
        confidence = 0.72 if recent_events > 0 else 0.51
        return {
            "probability_home": round(probability, 2),
            "confidence": confidence,
            "horizon_minutes": 60,
            "features": {
                "hour": round(hour, 2),
                "recent_events": recent_events,
                "door_unlocks_today": door_unlocks_today,
                "calendar_prior": "weekday-evening" if 16 <= hour <= 22 else "baseline",
            },
            "narrative": "Likely occupied" if probability >= 0.62 else "Uncertain occupancy",
        }

