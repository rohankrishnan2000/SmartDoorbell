import { BatteryCharging, BrainCircuit, Home, LockKeyhole, ThermometerSun } from "lucide-react";
import type { Device, Occupancy } from "../api/client";
import { pct } from "../lib/format";

type Props = {
  device?: Device;
  occupancy?: Occupancy;
  lockState: string;
};

export function Metrics({ device, occupancy, lockState }: Props) {
  const items = [
    { label: "Home probability", value: pct(occupancy?.probability_home ?? 0.78), icon: Home },
    { label: "Lock state", value: lockState, icon: LockKeyhole },
    { label: "Edge battery", value: `${device?.battery_percent ?? 87}%`, icon: BatteryCharging },
    { label: "Thermal", value: `${device?.temperature_c ?? 39.4}C`, icon: ThermometerSun },
    { label: "Agent confidence", value: pct(occupancy?.confidence ?? 0.72), icon: BrainCircuit },
  ];

  return (
    <section className="metrics-grid">
      {items.map(({ label, value, icon: Icon }) => (
        <div className="metric" key={label}>
          <Icon size={18} />
          <span>{label}</span>
          <strong>{value}</strong>
        </div>
      ))}
    </section>
  );
}

