from backend.app.models.domain import Detection, Device, Event
from backend.app.schemas.domain import DetectionRead, DeviceRead, EventRead


def detection_to_read(detection: Detection) -> DetectionRead:
    return DetectionRead(
        label=detection.label,
        confidence=detection.confidence,
        bbox=[detection.x1, detection.y1, detection.x2, detection.y2],
        track_id=detection.track_id,
    )


def event_to_read(event: Event) -> EventRead:
    return EventRead(
        id=event.id,
        device_id=event.device_id,
        event_type=event.event_type,
        severity=event.severity,
        timestamp=event.timestamp,
        confidence=event.confidence,
        risk_score=event.risk_score,
        summary=event.summary,
        snapshot_path=event.snapshot_path,
        clip_path=event.clip_path,
        notification_sent=event.notification_sent,
        lock_action=event.lock_action,
        detections=[detection_to_read(detection) for detection in event.detections],
        metadata=event.metadata_json,
    )


def device_to_read(device: Device) -> DeviceRead:
    return DeviceRead(
        id=device.id,
        name=device.name,
        location=device.location,
        camera_source=device.camera_source,
        status=device.status,
        firmware_version=device.firmware_version,
        battery_percent=device.battery_percent,
        temperature_c=device.temperature_c,
        config=device.config,
        last_seen_at=device.last_seen_at,
    )

