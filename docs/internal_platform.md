# Internal Platform Features

This layer is intentionally the kind of operational machinery a real device/security company would build around the visible smart doorbell product.

## Tenancy And Access

- Organizations with plan, region, residency, and privacy settings.
- Users, memberships, roles, and explicit scopes.
- API keys for edge devices and service-to-service ingestion.
- RBAC decisions through `PolicyEngine`, including emergency break-glass audit paths.

## Security Operations

- Immutable-style audit logs for lock commands, model promotions, label creation, and feature flag changes.
- Incident cases with assignee, status, severity, SLA due date, notes, tags, and resolution fields.
- Notification rules that map high-risk events to push, SMS, webhooks, and escalation policies.
- Dead-letter queue records for failed webhooks or background jobs.

## Device Fleet Management

- Device certificates for edge identity and rotation planning.
- Edge command queue for reboot, diagnostics, ROI updates, model updates, certificate rotation, and cache clearing.
- Feature flags for staged rollouts such as safer August unlock flows and agentic incident review.
- SLO records for ingest and edge inference reliability.

## Business And Support Operations

- Usage metering and quota decisions for event ingest, media minutes, inference, lock commands, webhooks, and agent reviews.
- Invoice preview calculations for plan overages.
- Compliance export manifests for data-subject requests.
- Privacy review checklists for consent-sensitive features.
- Limited support sessions with explicit redaction policies.
- Troubleshooting bundles for device-health support work.
- Release gates for migrations, model updates, rollback artifacts, and canary rollouts.
- Worker scheduling for heartbeat sweeps, webhook retries, retention, label export, certificate scans, and model drift reports.

## MLOps And Data Governance

- Model registry records with artifact URIs, stage, metrics, safety review, promoter, and rollback requirements.
- Promotion guard that blocks production deployment when privacy, rollback, precision, or false-unlock checks fail.
- Labeling tasks for human review of high-risk or uncertain events.
- Retention policies for media, event metadata, audit logs, legal holds, and deletion modes.

## Internal API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/internal/overview` | Company platform summary |
| `GET` | `/internal/audit` | Recent audit activity |
| `GET` | `/internal/feature-flags` | Rollout and safety toggles |
| `GET` | `/internal/incidents` | Incident queue |
| `POST` | `/internal/incidents` | Create an incident case |
| `GET` | `/internal/notifications/plan/{event_id}` | Show escalation plan for an event |
| `GET` | `/internal/model-registry` | Registered model versions |
| `POST` | `/internal/model-registry/promote` | Attempt model promotion through governance gate |
| `GET` | `/internal/labeling/tasks` | Human labeling queue |
| `POST` | `/internal/fleet/devices/{device_id}/commands` | Queue edge command |
| `GET` | `/internal/retention/plan` | Current deletion/archive plan |
| `GET` | `/internal/access/decision` | Explain an RBAC decision |

## Why This Helps The Project

These pieces turn the repo from a smart doorbell demo into a credible product platform. Backend roles can discuss multi-tenant control planes, ML roles can discuss model governance and labeling, devops roles can discuss SLOs and job operations, and security roles can discuss auditability, least privilege, incident response, and device certificates.

See also `docs/runbooks.md` for production-style operating procedures.
