import { AlertTriangle, Bell, PackageCheck, UserRoundCheck } from "lucide-react";
import type { EventRecord } from "../api/client";
import { eventLabel, pct, relativeTime } from "../lib/format";

const icons = {
  package_theft_risk: AlertTriangle,
  delivery_detected: PackageCheck,
  known_visitor: UserRoundCheck,
  visitor_detected: Bell,
};

type Props = {
  events: EventRecord[];
  selectedId: string;
  onSelect: (event: EventRecord) => void;
};

export function EventTimeline({ events, selectedId, onSelect }: Props) {
  return (
    <section className="panel timeline-panel">
      <div className="panel-heading">
        <span className="eyebrow">Event queue</span>
        <strong>{events.length} incidents</strong>
      </div>
      <div className="timeline-list">
        {events.map((event) => {
          const Icon = icons[event.event_type as keyof typeof icons] ?? Bell;
          return (
            <button
              key={event.id}
              className={`timeline-item ${selectedId === event.id ? "selected" : ""}`}
              onClick={() => onSelect(event)}
              type="button"
            >
              <span className={`event-icon ${event.severity}`}>
                <Icon size={18} />
              </span>
              <span className="timeline-copy">
                <span className="timeline-title">{eventLabel(event.event_type)}</span>
                <span>{event.summary}</span>
              </span>
              <span className="timeline-meta">
                <b>{pct(event.risk_score)}</b>
                <span>{relativeTime(event.timestamp)}</span>
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

