CREATE TABLE IF NOT EXISTS devices (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  location TEXT NOT NULL,
  camera_source TEXT NOT NULL,
  status TEXT NOT NULL,
  firmware_version TEXT NOT NULL,
  battery_percent INTEGER NOT NULL,
  temperature_c REAL NOT NULL,
  config JSON NOT NULL,
  last_seen_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY,
  device_id TEXT NOT NULL REFERENCES devices(id),
  event_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  confidence REAL NOT NULL,
  risk_score REAL NOT NULL,
  summary TEXT NOT NULL,
  snapshot_path TEXT,
  clip_path TEXT,
  notification_sent BOOLEAN NOT NULL,
  lock_action TEXT,
  metadata_json JSON NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS detections (
  id INTEGER PRIMARY KEY,
  event_id TEXT NOT NULL REFERENCES events(id),
  label TEXT NOT NULL,
  confidence REAL NOT NULL,
  x1 INTEGER NOT NULL,
  y1 INTEGER NOT NULL,
  x2 INTEGER NOT NULL,
  y2 INTEGER NOT NULL,
  track_id TEXT
);

CREATE TABLE IF NOT EXISTS occupancy_predictions (
  id TEXT PRIMARY KEY,
  device_id TEXT NOT NULL REFERENCES devices(id),
  prediction_time TIMESTAMP NOT NULL,
  horizon_minutes INTEGER NOT NULL,
  probability_home REAL NOT NULL,
  confidence REAL NOT NULL,
  features JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_runs (
  id TEXT PRIMARY KEY,
  event_id TEXT REFERENCES events(id),
  agent_name TEXT NOT NULL,
  status TEXT NOT NULL,
  recommendation TEXT NOT NULL,
  critique TEXT NOT NULL,
  next_action TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  metadata_json JSON NOT NULL
);

