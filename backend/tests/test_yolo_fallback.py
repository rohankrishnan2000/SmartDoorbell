from pathlib import Path

import numpy as np

from edge.inference.yolo_model import DoorbellYoloModel


def test_yolo_model_returns_scaled_demo_detections_when_weights_missing(tmp_path):
    model = DoorbellYoloModel(tmp_path / "missing.onnx")

    detections = model.detect(np.zeros((720, 1280, 3), dtype=np.uint8))

    assert model.loaded is False
    assert [d.label for d in detections] == ["person", "package"]
    assert detections[0].bbox == (435, 93, 742, 633)
    assert detections[1].bbox == (793, 489, 1011, 626)


def test_yolo_model_boundary_returns_empty_when_weights_exist(tmp_path):
    weights = tmp_path / "model.onnx"
    Path(weights).touch()
    model = DoorbellYoloModel(weights)

    assert model.loaded is True
    assert model.detect(np.zeros((32, 32, 3), dtype=np.uint8)) == []
