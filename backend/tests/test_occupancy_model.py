from datetime import UTC, datetime

from backend.app.ml.occupancy import OccupancyPredictor


def test_occupancy_predictor_reports_likely_home_for_active_evening():
    result = OccupancyPredictor().predict(
        datetime(2026, 7, 1, 19, 30, tzinfo=UTC),
        recent_events=10,
        door_unlocks_today=3,
    )

    assert result["probability_home"] >= 0.62
    assert result["confidence"] == 0.72
    assert result["features"]["calendar_prior"] == "weekday-evening"
    assert result["narrative"] == "Likely occupied"


def test_occupancy_predictor_clamps_quiet_low_activity_probability():
    result = OccupancyPredictor().predict(
        datetime(2026, 7, 1, 2, 15, tzinfo=UTC),
        recent_events=0,
        door_unlocks_today=0,
    )

    assert 0.08 <= result["probability_home"] <= 0.94
    assert result["confidence"] == 0.51
    assert result["features"]["calendar_prior"] == "baseline"
    assert result["narrative"] == "Uncertain occupancy"
