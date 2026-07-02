import { useEffect, useMemo, useState } from "react";
import { BellRing, Lock, Unlock, Wifi } from "lucide-react";
import { api, type Device, type EventRecord, type InternalOverview, type Occupancy } from "../api/client";
import { AgentPanel } from "../components/AgentPanel";
import { EventTimeline } from "../components/EventTimeline";
import { InternalOpsPanel } from "../components/InternalOpsPanel";
import { LiveView } from "../components/LiveView";
import { Metrics } from "../components/Metrics";
import { eventLabel, pct } from "../lib/format";

export function App() {
  const [events, setEvents] = useState<EventRecord[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [occupancy, setOccupancy] = useState<Occupancy>();
  const [internalOverview, setInternalOverview] = useState<InternalOverview>();
  const [selected, setSelected] = useState<EventRecord>();
  const [lockState, setLockState] = useState("locked");
  const [toast, setToast] = useState("Demo console loaded");

  useEffect(() => {
    Promise.all([api.events(), api.devices(), api.occupancy(), api.internalOverview()]).then(([eventData, deviceData, occupancyData, internalData]) => {
      setEvents(eventData);
      setDevices(deviceData);
      setOccupancy(occupancyData);
      setInternalOverview(internalData);
      setSelected(eventData[0]);
    });
  }, []);

  const activeEvent = useMemo(() => selected ?? events[0], [events, selected]);

  async function commandLock(action: "lock" | "unlock") {
    const result = await api.commandLock(action);
    setLockState(result.state ?? action);
    setToast(result.safety_summary ?? `Dry-run ${action} accepted`);
  }

  if (!activeEvent) {
    return <main className="app loading">Loading Sentinel Doorbell AI...</main>;
  }

  return (
    <main className="app">
      <nav className="topbar">
        <div className="brand">
          <span className="brand-mark">
            <BellRing size={20} />
          </span>
          <span>
            <b>Sentinel</b>
            <small>Doorbell AI ops console</small>
          </span>
        </div>
        <div className="status-strip">
          <span>
            <Wifi size={16} /> API + edge mesh
          </span>
          <span>PostgreSQL ready</span>
          <span>Agent mode: mock</span>
        </div>
      </nav>

      <div className="command-grid">
        <LiveView event={activeEvent} />
        <aside className="side-rail">
          <section className={`threat-card ${activeEvent.severity}`}>
            <span className="eyebrow">Selected incident</span>
            <h2>{eventLabel(activeEvent.event_type)}</h2>
            <p>{activeEvent.summary}</p>
            <div className="threat-score">
              <span>Risk score</span>
              <strong>{pct(activeEvent.risk_score)}</strong>
            </div>
          </section>

          <section className="panel controls-panel">
            <div className="panel-heading">
              <span className="eyebrow">August lock dry-run</span>
              <strong>{lockState}</strong>
            </div>
            <div className="lock-actions">
              <button type="button" onClick={() => commandLock("lock")}>
                <Lock size={18} /> Lock
              </button>
              <button type="button" onClick={() => commandLock("unlock")}>
                <Unlock size={18} /> Unlock
              </button>
            </div>
            <p>{toast}</p>
          </section>
        </aside>
      </div>

      <Metrics device={devices[0]} occupancy={occupancy} lockState={lockState} />

      <div className="lower-grid">
        <EventTimeline events={events} selectedId={activeEvent.id} onSelect={setSelected} />
        <AgentPanel event={activeEvent} occupancy={occupancy} />
        <section className="panel model-panel">
          <div className="panel-heading">
            <span className="eyebrow">Model cockpit</span>
            <strong>Doorbell risk ensemble</strong>
          </div>
          <div className="model-bars">
            <label>
              Person detector
              <span style={{ "--bar": "91%" } as React.CSSProperties} />
            </label>
            <label>
              Package detector
              <span style={{ "--bar": "86%" } as React.CSSProperties} />
            </label>
            <label>
              Theft classifier
              <span style={{ "--bar": `${Math.round(activeEvent.risk_score * 100)}%` } as React.CSSProperties} />
            </label>
            <label>
              Occupancy predictor
              <span style={{ "--bar": `${Math.round((occupancy?.probability_home ?? 0.78) * 100)}%` } as React.CSSProperties} />
            </label>
          </div>
        </section>
        <InternalOpsPanel overview={internalOverview} />
      </div>
    </main>
  );
}
