from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class DetectionResult:
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]
    track_id: str | None = None


class DoorbellYoloModel:
    """ONNX/TensorRT boundary with a deterministic fallback for demos."""

    def __init__(self, model_path: Path | str, providers: list[str] | None = None) -> None:
        self.model_path = Path(model_path)
        self.providers = providers or ["CPUExecutionProvider"]
        self.loaded = self.model_path.exists()

    def detect(self, frame: np.ndarray) -> list[DetectionResult]:
        height, width = frame.shape[:2]
        if not self.loaded:
            return [
                DetectionResult("person", 0.88, (int(width * 0.34), int(height * 0.13), int(width * 0.58), int(height * 0.88)), "trk_demo_person"),
                DetectionResult("package", 0.81, (int(width * 0.62), int(height * 0.68), int(width * 0.79), int(height * 0.87)), "trk_demo_pkg"),
            ]
        # Real ONNX Runtime inference can be wired here without changing callers.
        return []

