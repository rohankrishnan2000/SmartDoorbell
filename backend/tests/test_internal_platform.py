from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.model_registry import ModelRegistryGuard
from backend.app.services.notification_router import NotificationRouter
from backend.app.services.policy_engine import PolicyEngine
from backend.app.services.retention import RetentionPlanner

client = TestClient(app)


def test_internal_overview_has_company_platform_counts():
    response = client.get("/internal/overview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["organization"]["users"] >= 3
    assert payload["security"]["notification_rules"] >= 2
    assert payload["mlops"]["registered_models"] >= 2


def test_operator_can_command_locks_but_not_promote_models():
    engine = PolicyEngine()
    lock_decision = engine.decide("ops@sentinel.local", "operator", "command", "locks")
    model_decision = engine.decide("ops@sentinel.local", "operator", "promote", "models")
    assert lock_decision.allowed is True
    assert model_decision.allowed is False


def test_internal_notification_plan_for_seed_event():
    response = client.get("/internal/notifications/plan/evt_risk_002")
    assert response.status_code == 200
    plans = response.json()
    assert any(plan["rule_name"] == "Critical security escalation" for plan in plans)


def test_model_promotion_guard_blocks_unsafe_production():
    models = client.get("/internal/model-registry").json()
    candidate = next(model for model in models if model["id"] == "model_risk_001")
    response = client.post(
        "/internal/model-registry/promote",
        json={"model_id": candidate["id"], "target_stage": "production", "approver": "ml@sentinel.local"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["allowed"] is False
    assert payload["required_followups"]


def test_retention_plan_endpoint():
    response = client.get("/internal/retention/plan")
    assert response.status_code == 200
    payload = response.json()
    assert payload["policy_name"] == "Local-first residential privacy baseline"
    assert payload["planned_actions"]


def test_service_classes_are_importable_for_resume_depth():
    assert NotificationRouter
    assert ModelRegistryGuard
    assert RetentionPlanner

