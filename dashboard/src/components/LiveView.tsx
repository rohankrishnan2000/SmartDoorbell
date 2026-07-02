import { Camera, Crosshair, Radar, ScanLine } from "lucide-react";
import type { EventRecord } from "../api/client";
import { pct } from "../lib/format";

type Props = {
  event: EventRecord;
};

export function LiveView({ event }: Props) {
  const person = event.detections.find((detection) => detection.label === "person");
  const pkg = event.detections.find((detection) => detection.label === "package");

  return (
    <section className="live-shell" aria-label="Live camera analysis">
      <div className="live-header">
        <div>
          <span className="eyebrow">Front porch / synthetic WebRTC</span>
          <h1>Sentinel Doorbell AI</h1>
        </div>
        <div className="live-pill">
          <Radar size={16} />
          <span>Edge inference active</span>
        </div>
      </div>

      <div className="camera-frame">
        <div className="scene">
          <div className="door-panel" />
          <div className="floor-grid" />
          <div className="visitor-shape" />
          {pkg ? <div className="package-shape" /> : null}
          <div className="roi-line roi-top" />
          <div className="roi-line roi-bottom" />
          <div className="bbox person">
            <span>person {pct(person?.confidence ?? 0.84)}</span>
          </div>
          {pkg ? (
            <div className="bbox package">
              <span>package {pct(pkg.confidence)}</span>
            </div>
          ) : null}
          <div className="scan" />
        </div>
        <div className="camera-overlay">
          <span>
            <Camera size={16} /> RTSP-01
          </span>
          <span>
            <Crosshair size={16} /> ROI locked
          </span>
          <span>
            <ScanLine size={16} /> YOLO/ONNX dry-run
          </span>
        </div>
      </div>
    </section>
  );
}
