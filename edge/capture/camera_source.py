from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class Frame:
    image: np.ndarray
    timestamp: datetime
    source: str
    sequence: int


class CameraSource(Protocol):
    def read_frame(self) -> Frame:
        """Return the latest normalized frame."""


class DemoCamera:
    def __init__(self, source: str = "demo://front-door", width: int = 1280, height: int = 720) -> None:
        self.source = source
        self.width = width
        self.height = height
        self.sequence = 0

    def read_frame(self) -> Frame:
        self.sequence += 1
        image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        return Frame(image=image, timestamp=datetime.now(UTC), source=self.source, sequence=self.sequence)

