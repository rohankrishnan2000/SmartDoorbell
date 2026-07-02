# Doorbell Model Card

## Current State

`yolo-doorbell.onnx` is intentionally not committed. The code falls back to deterministic demo detections when no model file exists.

## Intended Models

- Detector: YOLOv8n/YOLOv8s exported to ONNX for person/package detection.
- Accelerator: ONNX Runtime on CPU and TensorRT on NVIDIA Jetson.
- Risk head: temporal classifier trained from event clips, dwell time, lighting, package state, and motion vectors.
- Occupancy head: tabular/time-series model using device events, lock operations, time of day, and optional calendar signals.

## Responsible Use

Face recognition and known-visitor matching should remain opt-in, consent-gated, and disabled by default.

