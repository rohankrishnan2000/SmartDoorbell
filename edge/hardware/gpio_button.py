from collections.abc import Callable


class DoorbellButton:
    """GPIO abstraction that can be replaced with gpiozero on Raspberry Pi."""

    def __init__(self, pin: int, on_press: Callable[[], None]) -> None:
        self.pin = pin
        self.on_press = on_press

    def simulate_press(self) -> None:
        self.on_press()

