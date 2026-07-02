# API Surface

Base URL: `http://localhost:8000`

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service status and capability list |
| `GET` | `/devices` | Device inventory and edge health |
| `PATCH` | `/devices/{device_id}/config` | Update threshold/ROI/cooldown config |
| `GET` | `/events` | Latest security events |
| `GET` | `/events/{event_id}` | Event details and detections |
| `POST` | `/events` | Edge event ingestion |
| `POST` | `/events/{event_id}/agent-review` | Run incident-review agent |
| `GET` | `/predictions/occupancy` | Home-presence probability |
| `POST` | `/locks/front-door/command` | Dry-run August lock command |
| `WS` | `/events/ws` | Event stream placeholder |
| `GET` | `/internal/overview` | Internal platform summary |
| `GET` | `/internal/audit` | Audit trail |
| `GET` | `/internal/incidents` | Incident case queue |
| `GET` | `/internal/model-registry` | Model governance state |
| `GET` | `/internal/labeling/tasks` | Human labeling work queue |
| `POST` | `/internal/fleet/devices/{device_id}/commands` | Queue edge fleet command |
| `GET` | `/internal/retention/plan` | Data retention plan |

## Example Event Ingest

```json
{
  "device_id": "front_door_01",
  "event_type": "motion",
  "confidence": 0.86,
  "detections": [
    { "label": "person", "confidence": 0.86, "bbox": [120, 80, 420, 700], "track_id": "trk_9" },
    { "label": "package", "confidence": 0.78, "bbox": [500, 520, 680, 690], "track_id": "trk_10" }
  ],
  "metadata": {
    "package_waiting": true,
    "lighting": "low",
    "camera": "front_door_01"
  }
}
```
