from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from backend.app.models.domain import (
    AgentRun,
    ApiKey,
    AuditLog,
    AutomationPolicy,
    CaseNote,
    DataRetentionPolicy,
    DeadLetterMessage,
    Detection,
    Device,
    DeviceCertificate,
    EdgeCommand,
    Event,
    FeatureFlag,
    IncidentCase,
    JobRun,
    LabelingTask,
    Membership,
    ModelVersion,
    NotificationDelivery,
    NotificationRule,
    Organization,
    SloMetric,
    UserAccount,
    WebhookEndpoint,
)


def seed_demo_data(db: Session) -> None:
    if db.get(Device, "front_door_01"):
        seed_internal_data(db)
        return

    device = Device(
        id="front_door_01",
        name="Front Door Sentinel",
        location="Front porch",
        camera_source="demo://front-door",
        status="online",
        battery_percent=87,
        temperature_c=39.4,
        config={
            "min_confidence": 0.65,
            "cooldown_seconds": 45,
            "roi": [[0.18, 0.12], [0.86, 0.12], [0.92, 0.94], [0.08, 0.96]],
            "model": "yolo-doorbell-demo.onnx",
        },
    )
    db.add(device)

    now = datetime.now(UTC)
    events = [
        Event(
            id="evt_delivery_001",
            device_id="front_door_01",
            event_type="delivery_detected",
            severity="info",
            timestamp=now - timedelta(minutes=18),
            confidence=0.91,
            risk_score=0.33,
            summary="Courier detected with package near porch ROI.",
            snapshot_path="/media/events/demo_delivery.jpg",
            clip_path="/media/events/demo_delivery.mp4",
            notification_sent=True,
            metadata_json={"weather": "clear", "agent_notes": "Package placed inside safe zone."},
        ),
        Event(
            id="evt_risk_002",
            device_id="front_door_01",
            event_type="package_theft_risk",
            severity="warning",
            timestamp=now - timedelta(minutes=7),
            confidence=0.84,
            risk_score=0.71,
            summary="Person lingered near an unattended package after dark.",
            snapshot_path="/media/events/demo_risk.jpg",
            clip_path="/media/events/demo_risk.mp4",
            notification_sent=True,
            lock_action="kept_locked",
            metadata_json={"package_waiting": True, "dwell_seconds": 31, "lighting": "low"},
        ),
        Event(
            id="evt_unlock_003",
            device_id="front_door_01",
            event_type="known_visitor",
            severity="info",
            timestamp=now - timedelta(minutes=3),
            confidence=0.88,
            risk_score=0.18,
            summary="Trusted visitor matched policy; unlock requires dashboard approval.",
            snapshot_path="/media/events/demo_known.jpg",
            notification_sent=False,
            lock_action="unlock_ready",
            metadata_json={"recognition_mode": "consent-gated-placeholder", "policy": "manual_approval"},
        ),
    ]
    db.add_all(events)
    db.flush()

    db.add_all(
        [
            Detection(event_id="evt_delivery_001", label="person", confidence=0.91, x1=130, y1=80, x2=390, y2=680, track_id="trk_17"),
            Detection(event_id="evt_delivery_001", label="package", confidence=0.86, x1=430, y1=508, x2=620, y2=676, track_id="trk_18"),
            Detection(event_id="evt_risk_002", label="person", confidence=0.84, x1=250, y1=70, x2=512, y2=712, track_id="trk_23"),
            Detection(event_id="evt_risk_002", label="package", confidence=0.79, x1=518, y1=548, x2=692, y2=690, track_id="trk_18"),
            Detection(event_id="evt_unlock_003", label="person", confidence=0.88, x1=192, y1=92, x2=448, y2=704, track_id="trk_28"),
        ]
    )
    db.add(
        AgentRun(
            id="agent_review_001",
            event_id="evt_risk_002",
            agent_name="incident-reviewer",
            recommendation="Keep lock engaged, notify owner, and queue the clip for package-theft fine-tuning.",
            critique="Risk score relied heavily on low-light dwell time; request manual label before retraining.",
            next_action="queue_training_sample",
            metadata_json={"self_correction": "needs_human_label", "confidence_delta": -0.07},
        )
    )
    db.add(
        AutomationPolicy(
            name="Trusted visitor unlock proposal",
            trigger={"event_type": "known_visitor", "probability_home_gte": 0.7},
            action={"provider": "august", "command": "unlock", "mode": "approval_required"},
            safety_check={"deny_if": ["robbery_risk", "package_theft_risk"], "cooldown_seconds": 120},
        )
    )
    db.commit()
    seed_internal_data(db)


def seed_internal_data(db: Session) -> None:
    if db.get(Organization, "org_demo"):
        return

    now = datetime.now(UTC)
    org = Organization(
        id="org_demo",
        name="Sentinel Home Security Labs",
        plan="internal-platform-demo",
        region="us-west-2",
        data_residency="edge-primary-us-west",
        settings={
            "require_mfa": True,
            "break_glass_audit": True,
            "default_media_retention_days": 30,
            "privacy_mode": "local-first",
        },
    )
    owner = UserAccount(
        id="usr_owner",
        organization_id=org.id,
        email="owner@sentinel.local",
        display_name="Rohan Owner",
        mfa_enabled=True,
    )
    operator = UserAccount(
        id="usr_ops",
        organization_id=org.id,
        email="ops@sentinel.local",
        display_name="Ops Oncall",
        mfa_enabled=True,
    )
    ml_engineer = UserAccount(
        id="usr_ml",
        organization_id=org.id,
        email="ml@sentinel.local",
        display_name="ML Platform",
        mfa_enabled=True,
    )
    db.add_all([org, owner, operator, ml_engineer])
    db.add_all(
        [
            Membership(
                organization_id=org.id,
                user_id=owner.id,
                role="owner",
                scopes=["billing:write", "tenancy:write"],
            ),
            Membership(
                organization_id=org.id,
                user_id=operator.id,
                role="operator",
                scopes=["fleet:read", "notifications:write"],
            ),
            Membership(
                organization_id=org.id,
                user_id=ml_engineer.id,
                role="ml_engineer",
                scopes=["labels:read", "experiments:write"],
            ),
        ]
    )
    db.add_all(
        [
            ApiKey(
                organization_id=org.id,
                name="edge-ingest-front-door",
                key_prefix="sntl_edge_8f12",
                hashed_secret="sha256:demo-only-not-a-real-secret",
                scopes=["events:write", "devices:heartbeat", "media:write"],
                expires_at=now + timedelta(days=180),
            ),
            FeatureFlag(
                organization_id=org.id,
                key="agentic_incident_autoreview",
                enabled=True,
                rollout_percent=100,
                owner="ai-platform",
                rules={"min_risk_score": 0.55, "deny_event_types": ["known_visitor"]},
            ),
            FeatureFlag(
                organization_id=org.id,
                key="august_unlock_safety_gate_v2",
                enabled=True,
                rollout_percent=35,
                owner="smart-home-integrations",
                rules={"require_home_probability": 0.7, "require_manual_approval": True},
            ),
            FeatureFlag(
                organization_id=org.id,
                key="familiar_visitor_recognition",
                enabled=False,
                rollout_percent=0,
                owner="privacy-review",
                rules={"blocked_until": "consent-flow-complete"},
            ),
        ]
    )
    db.add_all(
        [
            IncidentCase(
                id="case_pkg_001",
                organization_id=org.id,
                event_id="evt_risk_002",
                title="Possible package theft attempt",
                severity="warning",
                status="triaged",
                assigned_to="ops@sentinel.local",
                sla_due_at=now + timedelta(hours=6),
                tags=["package", "night", "agent-reviewed"],
            ),
            CaseNote(
                case_id="case_pkg_001",
                author_id=operator.id,
                body="Agent flagged dwell time near package. Keep clip for label review before changing threshold.",
            ),
        ]
    )
    db.add_all(
        [
            NotificationRule(
                id="rule_critical_security",
                organization_id=org.id,
                name="Critical security escalation",
                match={"min_risk_score": 0.75, "severities": ["critical", "warning"]},
                channels=[
                    {"type": "push", "destination": "owner-phone"},
                    {"type": "sms", "destination": "+15555550100"},
                    {"type": "webhook", "destination": "security-war-room"},
                ],
                escalation={"after_minutes": 3, "repeat": 2, "fallback": "phone_call"},
            ),
            NotificationRule(
                id="rule_delivery_summary",
                organization_id=org.id,
                name="Delivery digest",
                match={"event_types": ["delivery_detected"], "min_risk_score": 0.2},
                channels=[{"type": "push", "destination": "owner-phone"}],
                escalation={"after_minutes": 30, "fallback": "email_digest"},
            ),
            NotificationDelivery(
                rule_id="rule_critical_security",
                event_id="evt_risk_002",
                channel="push",
                destination="owner-phone",
                status="delivered",
                attempts=1,
                provider_response={"provider": "demo-push", "message_id": "msg_001"},
            ),
            WebhookEndpoint(
                organization_id=org.id,
                name="Internal security event relay",
                url="https://hooks.example.invalid/sentinel/security",
                secret_ref="secret://webhooks/security-relay",
                subscribed_events=["event.created", "incident.updated", "model.promoted"],
            ),
        ]
    )
    db.add_all(
        [
            ModelVersion(
                id="model_detector_001",
                name="doorbell-detector",
                version="2026.07.01-demo",
                stage="staging",
                artifact_uri="s3://sentinel-models/doorbell-detector/2026-07-01/model.onnx",
                metrics={
                    "map50": 0.71,
                    "person_precision": 0.93,
                    "package_precision": 0.86,
                    "latency_ms_p50": 38,
                },
                safety_review={"privacy_reviewed": True, "rollback_plan": True},
                promoted_by="ml@sentinel.local",
            ),
            ModelVersion(
                id="model_risk_001",
                name="package-theft-risk",
                version="0.3.0-candidate",
                stage="candidate",
                artifact_uri="registry://sentinel/package-theft-risk:0.3.0",
                metrics={
                    "precision_package_theft": 0.79,
                    "recall_package_theft": 0.88,
                    "false_unlock_rate": 0.001,
                    "calibration_error": 0.06,
                },
                safety_review={"privacy_reviewed": True, "rollback_plan": False},
            ),
            LabelingTask(
                id="lbl_evt_risk_002",
                event_id="evt_risk_002",
                queue="security-review",
                priority="high",
                status="open",
                suggested_label="package_theft_risk",
                instructions="Confirm whether the person removed, touched, or only approached the package.",
            ),
            LabelingTask(
                id="lbl_evt_unlock_003",
                event_id="evt_unlock_003",
                queue="known-visitor-consent",
                priority="medium",
                status="blocked",
                suggested_label="known_visitor",
                instructions="Do not use for training until explicit familiar-visitor consent exists.",
            ),
        ]
    )
    db.add_all(
        [
            DataRetentionPolicy(
                organization_id=org.id,
                name="Local-first residential privacy baseline",
                media_days=30,
                event_days=365,
                audit_days=2555,
                legal_hold=False,
                deletion_mode="secure-delete",
            ),
            DeadLetterMessage(
                queue_name="notification-webhooks",
                payload={"event_id": "evt_risk_002", "endpoint": "security-relay"},
                failure_reason="Demo endpoint is intentionally invalid.",
                retry_count=2,
                next_retry_at=now + timedelta(minutes=15),
            ),
            JobRun(
                name="nightly-media-retention",
                status="succeeded",
                started_at=now - timedelta(hours=2),
                finished_at=now - timedelta(hours=2, minutes=-4),
                heartbeat_at=now - timedelta(hours=2, minutes=-4),
                params={"dry_run": True},
                result={"clips_scanned": 128, "clips_deleted": 0, "mode": "demo"},
            ),
            DeviceCertificate(
                device_id="front_door_01",
                serial_number="CERT-DEMO-FRONT-001",
                public_key_fingerprint="SHA256:7a:demo:fingerprint:front-door",
                expires_at=now + timedelta(days=365),
            ),
            EdgeCommand(
                device_id="front_door_01",
                command_type="pull_diagnostics",
                payload={"include": ["logs", "thermal", "camera-reconnects"]},
                status="queued",
                issued_by="ops@sentinel.local",
            ),
            SloMetric(
                service="event-ingest",
                window="30d",
                target=0.995,
                actual=0.998,
                burn_rate=0.41,
            ),
            SloMetric(
                service="edge-inference",
                window="24h",
                target=0.99,
                actual=0.986,
                burn_rate=1.31,
            ),
        ]
    )
    db.add_all(
        [
            AuditLog(
                organization_id=org.id,
                actor_id=operator.id,
                action="lock.command.dry_run",
                resource_type="august_lock",
                resource_id="front-door-lock",
                after={"action": "kept_locked", "reason": "package_theft_risk"},
            ),
            AuditLog(
                organization_id=org.id,
                actor_id=ml_engineer.id,
                action="labeling.task.created",
                resource_type="labeling_task",
                resource_id="lbl_evt_risk_002",
                after={"queue": "security-review", "priority": "high"},
            ),
            AuditLog(
                organization_id=org.id,
                actor_id="system",
                action="feature_flag.updated",
                resource_type="feature_flag",
                resource_id="august_unlock_safety_gate_v2",
                after={"enabled": True, "rollout_percent": 35},
            ),
        ]
    )
    db.commit()
