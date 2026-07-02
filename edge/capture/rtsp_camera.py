import cv2

from edge.capture.camera_source import Frame


class RTSPCamera:
    def __init__(self, uri: str) -> None:
        self.uri = uri
        self.capture = cv2.VideoCapture(uri)
        self.sequence = 0

    def read_frame(self) -> Frame:
        from datetime import UTC, datetime

        ok, image = self.capture.read()
        if not ok:
            self.capture.release()
            self.capture = cv2.VideoCapture(self.uri)
            ok, image = self.capture.read()
        if not ok:
            raise RuntimeError(f"Could not read RTSP frame from {self.uri}")
        self.sequence += 1
        return Frame(image=image, timestamp=datetime.now(UTC), source=self.uri, sequence=self.sequence)

