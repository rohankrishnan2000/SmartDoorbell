import { Bot, GitBranch, RotateCcw, ShieldCheck } from "lucide-react";
import type { EventRecord, Occupancy } from "../api/client";
import { pct } from "../lib/format";

type Props = {
  event: EventRecord;
  occupancy?: Occupancy;
};

export function AgentPanel({ event, occupancy }: Props) {
  const needsTraining = event.risk_score > 0.6;
  return (
    <section className="panel agent-panel">
      <div className="panel-heading">
        <span className="eyebrow">Agentic safety loop</span>
        <strong>Incident reviewer</strong>
      </div>
      <div className="agent-card">
        <Bot size={24} />
        <div>
          <b>{needsTraining ? "Self-correction queued" : "Monitoring baseline"}</b>
          <p>
            {needsTraining
              ? "Clip marked for human label, threshold audit, and theft-risk fine-tuning proposal."
              : "Current event does not require retraining. Policy remains in observe mode."}
          </p>
        </div>
      </div>
      <div className="agent-steps">
        <span>
          <ShieldCheck size={16} /> Safety gate {pct(occupancy?.probability_home ?? 0.78)}
        </span>
        <span>
          <GitBranch size={16} /> Label drift watch
        </span>
        <span>
          <RotateCcw size={16} /> Night model calibration
        </span>
      </div>
    </section>
  );
}

