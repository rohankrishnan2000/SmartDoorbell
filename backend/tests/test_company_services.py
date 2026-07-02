from datetime import UTC, datetime

from backend.app.services.compliance_center import ComplianceCenter, DataExportRequest
from backend.app.services.release_manager import ReleaseCandidate, ReleaseManager, ReleaseRisk
from backend.app.services.support_tools import SupportTooling
from backend.app.services.usage_metering import MeterName, UsageMeter
from backend.app.workers.scheduler import WorkerScheduler


def test_usage_meter_blocks_hard_limit():
    decision = UsageMeter().project(MeterName.AGENT_REVIEW, current_usage=19_999, increment=2)
    assert decision.accepted is False
    assert decision.billable_overage > 0


def test_compliance_export_manifest_redacts_sensitive_fields():
    manifest = ComplianceCenter().build_export_manifest(
        DataExportRequest(
            organization_id="org_demo",
            subject_email="owner@sentinel.local",
            requested_by="privacy@sentinel.local",
            include_media=True,
        )
    )
    assert manifest.files
    assert any("blurred" in redaction for redaction in manifest.redactions)


def test_release_manager_blocks_high_risk_without_canary():
    result = ReleaseManager().evaluate(
        ReleaseCandidate(
            name="edge-risk-pipeline",
            version="2026.07.01",
            services=["api", "edge"],
            migrations=["002_internal_platform.sql"],
            feature_flags=["backup_verified"],
            model_versions=["model_risk_001"],
            risk=ReleaseRisk.HIGH,
        )
    )
    assert result.allowed is False
    assert len(result.blockers) >= 2


def test_support_session_is_limited_and_redacted():
    session = SupportTooling().create_limited_session("owner@sentinel.local", "debug missed alert")
    assert "clip_path" in session.redacted_fields
    assert "billing_usage" in session.allowed_views


def test_worker_scheduler_finds_minute_jobs():
    plans = WorkerScheduler().due_jobs(datetime(2026, 7, 1, 12, 34, tzinfo=UTC))
    assert any(plan.job_name == "edge-heartbeat-sweeper" for plan in plans)

