// Small shared presentational helpers.

export const fmt = (x, d = 4) =>
  x === null || x === undefined || Number.isNaN(x) ? "—" : (x >= 0 ? "+" : "") + x.toFixed(d);

export const pct = (x, d = 1) => (x * 100).toFixed(d) + "%";

const DECISION_LABEL = {
  ship: "Ship", no_ship: "Do not ship", rolled_back: "Rolled back", inconclusive: "Inconclusive",
};
const DECISION_ICON = { ship: "✓", no_ship: "✕", rolled_back: "⛔", inconclusive: "•" };

export function DecisionBadge({ decision }) {
  const s = decision?.status || "inconclusive";
  return <span className={`badge ${s}`}>{DECISION_ICON[s]} {DECISION_LABEL[s] || s}</span>;
}

export function DecisionBanner({ decision }) {
  const s = decision?.status || "inconclusive";
  return (
    <div className={`banner ${s}`}>
      <div className="icon">{DECISION_ICON[s]}</div>
      <div>
        <div className="title">{decision?.label || DECISION_LABEL[s]}</div>
        <div className="reason">{decision?.reason}</div>
      </div>
    </div>
  );
}

export function SrmBadge({ srm }) {
  if (!srm) return <span className="badge inconclusive">—</span>;
  const ok = srm.ok !== false;
  return (
    <span className={`badge ${ok ? "ok" : "warn"}`} title={`realized ${pct(srm.realized_share || 0)}`}>
      {ok ? "✓ SRM ok" : "⚠ SRM"}
    </span>
  );
}

// effect ± CI as text with a tiny inline bar
export function EffectCell({ eff }) {
  if (!eff) return <span className="muted">—</span>;
  return (
    <div className="eff">
      <div>{fmt(eff.point)}</div>
      <div className="ci">[{fmt(eff.ci_low)}, {fmt(eff.ci_high)}]</div>
    </div>
  );
}
