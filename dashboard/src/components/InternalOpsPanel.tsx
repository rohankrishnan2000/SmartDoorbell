import { DatabaseZap, Flag, KeyRound, ListChecks, Network, ShieldAlert, Siren, Waypoints } from "lucide-react";
import type { InternalOverview } from "../api/client";
import { pct } from "../lib/format";

type Props = {
  overview?: InternalOverview;
};

export function InternalOpsPanel({ overview }: Props) {
  const latestSlo = overview?.operations.latest_slo;
  const rows = [
    {
      label: "Users / API keys",
      value: `${overview?.organization.users ?? 3}/${overview?.organization.api_keys ?? 1}`,
      icon: KeyRound,
    },
    {
      label: "Feature flags",
      value: String(overview?.fleet.feature_flags ?? 3),
      icon: Flag,
    },
    {
      label: "Queued edge commands",
      value: String(overview?.fleet.queued_commands ?? 1),
      icon: Network,
    },
    {
      label: "Open incidents",
      value: String(overview?.security.open_incidents ?? 1),
      icon: Siren,
    },
    {
      label: "Audit events",
      value: String(overview?.security.audit_events ?? 3),
      icon: ListChecks,
    },
    {
      label: "Dead letters",
      value: String(overview?.security.dead_letters ?? 1),
      icon: ShieldAlert,
    },
    {
      label: "Models / labels",
      value: `${overview?.mlops.registered_models ?? 2}/${overview?.mlops.open_labeling_tasks ?? 1}`,
      icon: DatabaseZap,
    },
    {
      label: latestSlo?.service ?? "event-ingest",
      value: pct(latestSlo?.actual ?? 0.998),
      icon: Waypoints,
    },
  ];

  return (
    <section className="panel internal-panel">
      <div className="panel-heading">
        <span className="eyebrow">Internal control plane</span>
        <strong>{overview?.organization.plan ?? "internal-platform-demo"}</strong>
      </div>
      <div className="internal-grid">
        {rows.map(({ label, value, icon: Icon }) => (
          <div className="internal-cell" key={label}>
            <Icon size={16} />
            <span>{label}</span>
            <b>{value}</b>
          </div>
        ))}
      </div>
    </section>
  );
}

