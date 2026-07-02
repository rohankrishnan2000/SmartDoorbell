from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True)
class SupportSession:
    session_id: str
    user_email: str
    reason: str
    expires_at: datetime
    allowed_views: list[str]
    redacted_fields: list[str]


class SupportTooling:
    def create_limited_session(self, user_email: str, reason: str) -> SupportSession:
        return SupportSession(
            session_id=f"support_{abs(hash((user_email, reason))) % 10_000_000}",
            user_email=user_email,
            reason=reason,
            expires_at=datetime.now(UTC) + timedelta(minutes=30),
            allowed_views=["device_health", "event_metadata", "notification_status", "billing_usage"],
            redacted_fields=["clip_path", "snapshot_path", "webhook_secret", "api_key_hash"],
        )

    def troubleshooting_bundle(self, device_id: str) -> dict:
        return {
            "device_id": device_id,
            "sections": [
                "last_100_edge_logs",
                "camera_reconnect_history",
                "model_latency_histogram",
                "thermal_throttling_report",
                "queued_commands",
                "recent_audit_logs",
            ],
            "safe_to_share": True,
            "redaction_policy": "remove_network_credentials_and_media",
        }

