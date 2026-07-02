# Internal Runbooks

These runbooks are deliberately included to make the project read like an operated product, not just a prototype.

## High-Risk Event Escalation

Trigger: an event is classified as `robbery_risk`, `package_theft_risk`, or a warning/critical incident with risk above policy threshold.

1. Confirm event exists in `/events/{event_id}`.
2. Check `/internal/notifications/plan/{event_id}` to verify the intended escalation path.
3. Create or update an incident case in `/internal/incidents`.
4. Confirm the August lock adapter state is locked or blocked by safety gate.
5. Queue `pull_diagnostics` for the device if the clip or detection metadata looks inconsistent.
6. Create a labeling task when the agent critique says the model may have over-weighted lighting, dwell time, or package state.

## Model Promotion

Trigger: a detector or risk model is ready to move from candidate to staging or production.

1. Register the model artifact URI in `/internal/model-registry`.
2. Confirm metrics include package-theft precision, false-unlock rate, calibration error, latency, and rollback artifact.
3. Run promotion through `/internal/model-registry/promote`.
4. If blocked, complete required follow-ups before retrying.
5. Roll out behind a feature flag and watch edge-inference SLO burn rate.

## Device Certificate Rotation

Trigger: device certificate expires within 30 days or a device is suspected compromised.

1. Queue `rotate_certificate` command in `/internal/fleet/devices/{device_id}/commands`.
2. Verify the edge device acknowledges the command.
3. Confirm the old certificate is revoked only after the new fingerprint is observed.
4. Add an audit log entry with actor, reason, old fingerprint, and new fingerprint.

## Media Retention

Trigger: nightly retention job or user data deletion request.

1. Inspect `/internal/retention/plan`.
2. Confirm legal hold is false before deleting media.
3. Export required audit and event metadata before deletion if compliance requires it.
4. Delete or archive media according to policy.
5. Record job result in `job_runs`.

## Webhook Failure

Trigger: dead-letter queue has failed notification webhooks.

1. Inspect dead-letter payload and retry count.
2. Verify webhook endpoint is enabled and secret reference exists.
3. Replay only idempotent event types.
4. Escalate to email digest if push/webhook delivery remains unhealthy.

