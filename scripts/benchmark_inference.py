from pathlib import Path
from time import perf_counter

import numpy as np

from edge.inference.yolo_model import DoorbellYoloModel


def main() -> None:
    model = DoorbellYoloModel(Path("models/yolo-doorbell.onnx"))
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    start = perf_counter()
    runs = 100
    for _ in range(runs):
        model.detect(frame)
    elapsed = perf_counter() - start
    print({"runs": runs, "avg_ms": round(elapsed / runs * 1000, 3), "mode": "fallback" if not model.loaded else "onnx"})


if __name__ == "__main__":
    main()

