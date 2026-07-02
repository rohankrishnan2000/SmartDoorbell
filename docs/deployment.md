# Deployment Notes

## Local

```bash
uvicorn backend.app.main:app --reload --port 8000
cd dashboard && npm run dev
```

## Docker Compose

```bash
docker compose -f deploy/docker/docker-compose.yml up --build
```

## Edge Device

Use the systemd units in `deploy/systemd` for a Raspberry Pi, Jetson, or mini PC deployment. The edge service can run CPU fallback detections until a real ONNX model is placed at `models/yolo-doorbell.onnx`.

## Cloud

The Terraform sketch provisions a container registry, PostgreSQL, object storage for event media, and a Kubernetes cluster. It is intentionally not provider-complete yet; the file is meant to communicate the intended production topology.

