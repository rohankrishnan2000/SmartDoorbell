class PIRSensor:
    """PIR motion sensor boundary for GPIO-backed deployments."""

    def __init__(self, pin: int) -> None:
        self.pin = pin
        self._motion = False

    def has_motion(self) -> bool:
        return self._motion

    def simulate_motion(self, value: bool = True) -> None:
        self._motion = value

