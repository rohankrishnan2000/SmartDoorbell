export type Detection = {
  label: string;
  confidence: number;
  bbox: number[];
  track_id?: string | null;
};

export type EventRecord = {
  id: string;
  device_id: string;
  event_type: string;
  severity: "info" | "warning" | "critical" | string;
  timestamp: string;
  confidence: number;
  risk_score: number;
  summary: string;
  snapshot_path?: string | null;
  clip_path?: string | null;
  notification_sent: boolean;
  lock_action?: string | null;
  detections: Detection[];
  metadata: Record<string, unknown>;
};

export type Device = {
  id: string;
  name: string;
  location: string;
  camera_source: string;
  status: string;
  firmware_version: string;
  battery_percent: number;
  temperature_c: number;
  config: Record<string, unknown>;
  last_seen_at: string;
};

export type Occupancy = {
  probability_home: number;
  confidence: number;
  horizon_minutes: number;
  narrative: string;
  features: Record<string, unknown>;
};

export type InternalOverview = {
  organization: {
    id: string;
    name: string;
    plan: string;
    users: number;
    api_keys: number;
  };
  fleet: {
    devices: number;
    queued_commands: number;
    feature_flags: number;
  };
  security: {
    open_incidents: number;
    audit_events: number;
    dead_letters: number;
    notification_rules: number;
  };
  mlops: {
    registered_models: number;
    open_labeling_tasks: number;
  };
  operations: {
    job_runs: number;
    latest_slo: {
      service: string;
      target: number;
      actual: number;
      burn_rate: number;
    };
  };
};

const fallbackEvents: EventRecord[] = [
  {
    id: "evt_risk_002",
    device_id: "front_door_01",
    event_type: "package_theft_risk",
    severity: "warning",
    timestamp: new Date(Date.now() - 7 * 60_000).toISOString(),
    confidence: 0.84,
    risk_score: 0.71,
    summary: "Person lingered near an unattended package after dark.",
    snapshot_path: null,
    clip_path: null,
    notification_sent: true,
    lock_action: "kept_locked",
    detections: [
      { label: "person", confidence: 0.84, bbox: [250, 70, 512, 712], track_id: "trk_23" },
      { label: "package", confidence: 0.79, bbox: [518, 548, 692, 690], track_id: "trk_18" },
    ],
    metadata: { dwell_seconds: 31, package_waiting: true },
  },
  {
    id: "evt_unlock_003",
    device_id: "front_door_01",
    event_type: "known_visitor",
    severity: "info",
    timestamp: new Date(Date.now() - 3 * 60_000).toISOString(),
    confidence: 0.88,
    risk_score: 0.18,
    summary: "Trusted visitor matched policy; unlock requires dashboard approval.",
    snapshot_path: null,
    clip_path: null,
    notification_sent: false,
    lock_action: "unlock_ready",
    detections: [{ label: "person", confidence: 0.88, bbox: [192, 92, 448, 704], track_id: "trk_28" }],
    metadata: { policy: "manual_approval" },
  },
  {
    id: "evt_delivery_001",
    device_id: "front_door_01",
    event_type: "delivery_detected",
    severity: "info",
    timestamp: new Date(Date.now() - 18 * 60_000).toISOString(),
    confidence: 0.91,
    risk_score: 0.33,
    summary: "Courier detected with package near porch ROI.",
    snapshot_path: null,
    clip_path: null,
    notification_sent: true,
    lock_action: null,
    detections: [
      { label: "person", confidence: 0.91, bbox: [130, 80, 390, 680], track_id: "trk_17" },
      { label: "package", confidence: 0.86, bbox: [430, 508, 620, 676], track_id: "trk_18" },
    ],
    metadata: { weather: "clear" },
  },
];

const fallbackDevice: Device = {
  id: "front_door_01",
  name: "Front Door Sentinel",
  location: "Front porch",
  camera_source: "demo://front-door",
  status: "online",
  firmware_version: "edge-0.1.0",
  battery_percent: 87,
  temperature_c: 39.4,
  config: { min_confidence: 0.65, cooldown_seconds: 45 },
  last_seen_at: new Date().toISOString(),
};

const fallbackOccupancy: Occupancy = {
  probability_home: 0.78,
  confidence: 0.72,
  horizon_minutes: 60,
  narrative: "Likely occupied",
  features: { hour: 20.4, recent_events: 9, calendar_prior: "weekday-evening" },
};

const fallbackInternalOverview: InternalOverview = {
  organization: {
    id: "org_demo",
    name: "Sentinel Home Security Labs",
    plan: "internal-platform-demo",
    users: 3,
    api_keys: 1,
  },
  fleet: {
    devices: 1,
    queued_commands: 1,
    feature_flags: 3,
  },
  security: {
    open_incidents: 1,
    audit_events: 3,
    dead_letters: 1,
    notification_rules: 2,
  },
  mlops: {
    registered_models: 2,
    open_labeling_tasks: 1,
  },
  operations: {
    job_runs: 1,
    latest_slo: {
      service: "event-ingest",
      target: 0.995,
      actual: 0.998,
      burn_rate: 0.41,
    },
  },
};

async function getJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`/api${path}`);
    if (!response.ok) throw new Error(response.statusText);
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export const api = {
  events: () => getJson<EventRecord[]>("/events", fallbackEvents),
  devices: () => getJson<Device[]>("/devices", [fallbackDevice]),
  occupancy: () => getJson<Occupancy>("/predictions/occupancy", fallbackOccupancy),
  internalOverview: () => getJson<InternalOverview>("/internal/overview", fallbackInternalOverview),
  commandLock: async (action: "lock" | "unlock") => {
    const response = await fetch("/api/locks/front-door/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, reason: "dashboard operator command" }),
    });
    if (!response.ok) {
      return { accepted: true, state: action === "lock" ? "locked" : "unlocked", safety_summary: "Demo dry-run accepted." };
    }
    return response.json();
  },
};
