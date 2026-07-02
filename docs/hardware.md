# Hardware Plan

## Supported Modes

- Camera upgrade mode: RTSP camera, USB webcam, old phone stream, or existing CCTV feed.
- Dedicated doorbell mode: Raspberry Pi 5 or NVIDIA Jetson Orin Nano, CSI camera, PIR sensor, GPIO button, speaker, and optional display.

## Pins

| Component | Suggested Pin | Notes |
| --- | --- | --- |
| Doorbell button | GPIO17 | Pull-up input |
| PIR sensor | GPIO27 | Motion trigger |
| Speaker amp | GPIO18/PWM | Chime and talkback |
| Status LED | GPIO22 | Device health |

## Privacy Defaults

- Local inference by default.
- Store clips locally unless cloud relay is explicitly enabled.
- Known visitor recognition remains consent-gated and disabled by default.

