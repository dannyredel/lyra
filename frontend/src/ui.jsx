import React from "react";

export const STATE_LABEL = { DRAFT: "Draft", RUNNING: "Running", STOPPED: "Stopped",
  ANALYZED: "Analyzed", DECIDED: "Decided" };
const COLOR_VAR = { green: "var(--green)", red: "var(--red)", grey: "#94A3B8" };

export function StateChip({ state }) {
  return <span className={"chip " + state.toLowerCase()}><span className="d" />{STATE_LABEL[state] || state}</span>;
}

export function MetricChip({ metric }) {
  return <span className="tag">{metric.name} · {metric.type}</span>;
}

export function CertifiedBadge({ truth }) {
  if (!truth) return <span className="badge no">—</span>;
  return truth.certified
    ? <span className="badge ok">✓ certified · {truth.coverage_pct}%</span>
    : <span className="badge no">uncertified</span>;
}

export function EffectCell({ readout }) {
  if (!readout) return <span style={{ color: "var(--muted)" }}>—</span>;
  return <span className={"effect-cell " + readout.ci_color}><span className="d" />{readout.headline}</span>;
}

export function PowerBar({ power }) {
  if (!power) return <span style={{ color: "var(--muted)" }}>—</span>;
  const pct = power.pct_powered ?? 0;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div className={"pbar" + (power.powered ? " full" : "")}><span style={{ width: Math.min(100, pct) + "%" }} /></div>
      <span className="num" style={{ fontSize: 12, color: "var(--muted)", minWidth: 34 }}>{pct}%</span>
    </div>
  );
}

/** The CI-as-colored-bar — green if entirely >0, red if entirely <0, grey if it spans 0.
 *  The band is scaled to a prominent, consistent width (centered on the interval); the 0 line and the
 *  faint *true-effect* mark (Lyra's superpower) sit at their real positions, or clamp to the edge when
 *  they fall outside the framed range. */
export function CIBar({ readout, truth }) {
  const { ci_low: lo, ci_high: hi, point, ci_color } = readout;
  const t = truth?.value;
  const w = (hi - lo) || 0.002;
  const center = (lo + hi) / 2;
  const half = w * 1.15;                       // CI fills ~43% of the bar → always clearly visible
  const min = center - half, span = 2 * half;
  const inFrame = (v) => v >= min && v <= center + half;
  const pos = (v) => Math.max(0.5, Math.min(99.5, ((v - min) / span) * 100));
  return (
    <div>
      <div className="cibar">
        <div className="axis" />
        <div className="zero" style={{ left: pos(0) + "%", opacity: inFrame(0) ? 1 : 0.35 }} />
        <div className={"band " + ci_color} style={{ left: pos(lo) + "%", width: (pos(hi) - pos(lo)) + "%" }} />
        <div className="pt" style={{ left: pos(point) + "%", background: COLOR_VAR[ci_color] }} />
        {t != null && (
          <div title={`true effect = ${t.toFixed(3)}`}
            style={{ position: "absolute", top: 1, bottom: 1, left: pos(t) + "%", width: 2,
                     background: "#0E1A2B", opacity: inFrame(t) ? 0.45 : 0.18 }} />
        )}
      </div>
      <div className="cibar-cap"><span className="num">{lo.toFixed(3)}</span><span className="num">{hi.toFixed(3)}</span></div>
    </div>
  );
}

export function Info({ children }) {
  return <span className="info" tabIndex={0}>i<span className="tip">{children}</span></span>;
}

// the Lyra constellation — Vega (the bright star) anchors the lyre. A nod to the project's two names.
export function Logo({ size = 30 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 30 30" fill="none" aria-label="Lyra">
      <defs>
        <linearGradient id="lyraG" x1="0" y1="0" x2="30" y2="30">
          <stop stopColor="#122140" /><stop offset="1" stopColor="#1E6091" />
        </linearGradient>
      </defs>
      <rect width="30" height="30" rx="8" fill="url(#lyraG)" />
      <g stroke="#9FC2DE" strokeWidth="1" opacity="0.7" strokeLinejoin="round" fill="none">
        <path d="M9 8 L17 12 L21 19 L13 22 L9 15 Z M17 12 L9 15" />
      </g>
      <circle cx="9" cy="8" r="2.4" fill="#fff" />
      <circle cx="17" cy="12" r="1.4" fill="#EAF3FA" />
      <circle cx="21" cy="19" r="1.2" fill="#EAF3FA" />
      <circle cx="13" cy="22" r="1.2" fill="#EAF3FA" />
      <circle cx="9" cy="15" r="1.2" fill="#EAF3FA" />
    </svg>
  );
}

// Static-deploy banner — tells a first-time visitor what's interactive vs what needs the backend.
export function DemoBanner({ onClose }) {
  return (
    <div className="demo-banner">
      <span className="d" />
      <div><b>Demo mode</b> — you're exploring a precomputed snapshot. The registry, every scorecard, the
        metrics catalog, decisions, and the live <b>sample-size calculator</b> are fully interactive.
        <em> Launching</em> a created experiment runs Python, so it needs the live backend.</div>
      <button className="x" onClick={onClose} aria-label="Dismiss">×</button>
    </div>
  );
}

// The visual language, made explicit — the Lyra superpower (a known ground truth) needs one read.
export function Legend() {
  return (
    <div className="legend">
      <span className="li"><span className="sw" style={{ background: "var(--green)" }} /> certified vs truth</span>
      <span className="li"><span className="sw dash" /> ground truth (planted)</span>
      <span className="li"><span className="sw line" style={{ background: "var(--green)" }} /> CI excludes 0</span>
      <span className="li"><span className="sw line" style={{ background: "#94A3B8" }} /> CI spans 0</span>
    </div>
  );
}

export function AdvisoryChip({ sequential }) {
  if (!sequential) return null;
  const s = sequential.state;
  const label = s === "stop" ? "✓ safe to stop" : s === "keep" ? "keep collecting" : "collecting";
  return (
    <span className={"badge " + (s === "stop" ? "ok" : "no")} title={sequential.text}>
      {label}{sequential.magnitude_inflated ? " ⚠" : ""}
    </span>
  );
}

export function Stat({ label, value, sub, icon }) {
  return (
    <div className="card stat row">
      {icon && <div className="ic">{icon}</div>}
      <div>
        <div className="lbl">{label}</div>
        <div className="val">{value}</div>
        {sub && <div className="sub">{sub}</div>}
      </div>
    </div>
  );
}

export function Sidebar({ section, onNav, mode }) {
  const item = (key, label) => (
    <button className={section === key ? "active" : ""} onClick={() => onNav(key)}>
      <span className="dot" />{label}</button>
  );
  return (
    <aside className="sidebar">
      <div className="brand">
        <Logo size={30} />
        <div>
          <div className="name">Lyra</div>
          <div className="sub">experimentation</div>
        </div>
      </div>
      <nav className="nav">
        {item("home", "Home")}
        {item("experiments", "Experiments")}
        {item("metrics", "Metrics")}
        {item("decisions", "Decisions")}
        {item("assignment", "Assignment")}
      </nav>
      <div className="foot">
        {mode && <div style={{ marginBottom: 8 }}>
          <span className={"chip " + (mode === "live" ? "decided" : "draft")}><span className="d" />
            {mode === "live" ? "live · FastAPI" : "demo · static"}</span></div>}
        Thin-but-real chassis.<br />Every readout <b>validated</b> against a known ground truth.
      </div>
    </aside>
  );
}
