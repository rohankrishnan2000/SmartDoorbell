from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class DataExportRequest:
    organization_id: str
    subject_email: str
    requested_by: str
    include_media: bool = False
    include_audit: bool = True


@dataclass(frozen=True)
class DataExportManifest:
    export_id: str
    subject_email: str
    created_at: datetime
    files: list[dict]
    redactions: list[str]
    expires_in_hours: int


class ComplianceCenter:
    def build_export_manifest(self, request: DataExportRequest) -> DataExportManifest:
        files = [
            {"path": "profile/user.json", "classification": "personal_data"},
            {"path": "events/events.jsonl", "classification": "security_events"},
            {"path": "labels/labeling_tasks.jsonl", "classification": "ml_feedback"},
        ]
        if request.include_audit:
            files.append({"path": "audit/audit_logs.jsonl", "classification": "operational_audit"})
        if request.include_media:
            files.append({"path": "media/redacted_event_clips.zip", "classification": "biometric_sensitive"})
        return DataExportManifest(
            export_id=f"dsar_{abs(hash((request.organization_id, request.subject_email))) % 10_000_000}",
            subject_email=request.subject_email,
            created_at=datetime.now(UTC),
            files=files,
            redactions=[
                "Webhook secrets are excluded.",
                "Other household members are blurred in exported media.",
                "Internal risk-threshold configuration is summarized but not raw-exported.",
            ],
            expires_in_hours=72,
        )

    def privacy_review_checklist(self, feature_key: str) -> dict:
        checks = [
            {"name": "data_minimization", "required": True},
            {"name": "consent_flow", "required": feature_key == "familiar_visitor_recognition"},
            {"name": "retention_mapping", "required": True},
            {"name": "human_override", "required": "unlock" in feature_key},
            {"name": "model_card_updated", "required": feature_key.startswith("model_")},
        ]
        return {
            "feature_key": feature_key,
            "checks": checks,
            "blocking_checks": [check["name"] for check in checks if check["required"]],
        }

