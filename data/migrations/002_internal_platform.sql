CREATE TABLE IF NOT EXISTS organizations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  plan TEXT NOT NULL,
  region TEXT NOT NULL,
  data_residency TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  settings JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS user_accounts (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  email TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  status TEXT NOT NULL,
  mfa_enabled BOOLEAN NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS memberships (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  user_id TEXT NOT NULL REFERENCES user_accounts(id),
  role TEXT NOT NULL,
  scopes JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS api_keys (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  name TEXT NOT NULL,
  key_prefix TEXT NOT NULL,
  hashed_secret TEXT NOT NULL,
  scopes JSON NOT NULL,
  expires_at TIMESTAMP,
  last_used_at TIMESTAMP,
  disabled BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  actor_id TEXT,
  action TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  resource_id TEXT NOT NULL,
  ip_address TEXT NOT NULL,
  user_agent TEXT NOT NULL,
  before JSON NOT NULL,
  after JSON NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS feature_flags (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  key TEXT NOT NULL,
  enabled BOOLEAN NOT NULL,
  rollout_percent INTEGER NOT NULL,
  rules JSON NOT NULL,
  owner TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS incident_cases (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  event_id TEXT REFERENCES events(id),
  title TEXT NOT NULL,
  severity TEXT NOT NULL,
  status TEXT NOT NULL,
  assigned_to TEXT,
  sla_due_at TIMESTAMP,
  resolution TEXT,
  tags JSON NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS case_notes (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES incident_cases(id),
  author_id TEXT NOT NULL,
  body TEXT NOT NULL,
  visibility TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS notification_rules (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  name TEXT NOT NULL,
  enabled BOOLEAN NOT NULL,
  match JSON NOT NULL,
  channels JSON NOT NULL,
  escalation JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS model_versions (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  stage TEXT NOT NULL,
  artifact_uri TEXT NOT NULL,
  metrics JSON NOT NULL,
  safety_review JSON NOT NULL,
  promoted_by TEXT,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS labeling_tasks (
  id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL REFERENCES events(id),
  queue TEXT NOT NULL,
  priority TEXT NOT NULL,
  status TEXT NOT NULL,
  suggested_label TEXT NOT NULL,
  human_label TEXT,
  reviewer_id TEXT,
  instructions TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS data_retention_policies (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  name TEXT NOT NULL,
  media_days INTEGER NOT NULL,
  event_days INTEGER NOT NULL,
  audit_days INTEGER NOT NULL,
  legal_hold BOOLEAN NOT NULL,
  deletion_mode TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notification_deliveries (
  id TEXT PRIMARY KEY,
  rule_id TEXT NOT NULL REFERENCES notification_rules(id),
  event_id TEXT REFERENCES events(id),
  channel TEXT NOT NULL,
  destination TEXT NOT NULL,
  status TEXT NOT NULL,
  attempts INTEGER NOT NULL,
  provider_response JSON NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS webhook_endpoints (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  name TEXT NOT NULL,
  url TEXT NOT NULL,
  secret_ref TEXT NOT NULL,
  subscribed_events JSON NOT NULL,
  enabled BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dead_letter_messages (
  id TEXT PRIMARY KEY,
  queue_name TEXT NOT NULL,
  payload JSON NOT NULL,
  failure_reason TEXT NOT NULL,
  retry_count INTEGER NOT NULL,
  next_retry_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS job_runs (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TIMESTAMP,
  finished_at TIMESTAMP,
  heartbeat_at TIMESTAMP,
  params JSON NOT NULL,
  result JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS device_certificates (
  id TEXT PRIMARY KEY,
  device_id TEXT NOT NULL REFERENCES devices(id),
  serial_number TEXT NOT NULL,
  public_key_fingerprint TEXT NOT NULL,
  issued_at TIMESTAMP NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  revoked_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS edge_commands (
  id TEXT PRIMARY KEY,
  device_id TEXT NOT NULL REFERENCES devices(id),
  command_type TEXT NOT NULL,
  payload JSON NOT NULL,
  status TEXT NOT NULL,
  issued_by TEXT NOT NULL,
  issued_at TIMESTAMP NOT NULL,
  acknowledged_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS slo_metrics (
  id TEXT PRIMARY KEY,
  service TEXT NOT NULL,
  window TEXT NOT NULL,
  target REAL NOT NULL,
  actual REAL NOT NULL,
  burn_rate REAL NOT NULL,
  created_at TIMESTAMP NOT NULL
);
