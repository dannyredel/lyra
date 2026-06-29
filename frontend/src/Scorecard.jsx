import React, { useState } from "react";
import {
  ResponsiveContainer, ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine,
} from "recharts";
import { StateChip, MetricChip, CertifiedBadge, CIBar, AdvisoryChip, Legend } from "./ui.jsx";
import Analytics from "./Analytics.jsx";

const LINE = { green: "#16A34A", red: "#DC2626", grey: "#1E6091" };

export default function Scorecard({ data, onBack, onTransition, mode }) {
  const isDraft = data.state === "DRAFT" || !data.readout;
  const [tab, setTab] = useState("summary");
  return (
    <>
      <button className="btn ghost" onClick={onBack} style={{ marginBottom: 14 }}>← Experiments</button>
      <div className="page-head">
        <div>
          <h1>{data.name}</h1>
          <p>{data.hypothesis} &nbsp;·&nbsp; <span style={{ color: "var(--ink-2)" }}>{data.owner}</span></p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <StateChip state={data.state} />
          {mode === "live" && <Lifecycle state={data.state} rec={data.decision_rec} onTransition={onTransition} />}
        </div>
      </div>
      {!isDraft && (
        <div className="tabs">
          <button className={tab === "summary" ? "active" : ""} onClick={() => setTab("summary")}>Summary</button>
          <button className={tab === "analytics" ? "active" : ""} onClick={() => setTab("analytics")}>Detailed analytics</button>
        </div>
      )}
      {isDraft ? <Draft data={data} /> : tab === "analytics" ? <Analytics data={data} /> : <Running data={data} />}
    </>
  );
}

function Lifecycle({ state, rec, onTransition }) {
  const T = (to, extra) => () => onTransition(to, extra);
  if (state === "DRAFT") return <button className="btn primary" onClick={T("RUNNING")}>Launch ▶</button>;
  if (state === "RUNNING") return <button className="btn" onClick={T("STOPPED")}>Stop ■</button>;
  if (state === "STOPPED") return (<>
    <button className="btn" onClick={T("RUNNING")}>Resume</button>
    <button className="btn primary" onClick={T("ANALYZED")}>Analyze</button></>);
  if (state === "ANALYZED") return (<>
    <button className="btn" onClick={T("RUNNING")}>Resume</button>
    <button className="btn" onClick={T("DECIDED", { ship: "false", rationale: "manual hold" })}>Hold ✗</button>
    <button className="btn primary" onClick={T("DECIDED", { ship: "true", rationale: rec?.reason || "ship" })}>Ship ✓</button></>);
  return null;
}

function Draft({ data }) {
  const p = data.power || {};
  return (
    <div className="sc-grid">
      <div className="card cardpad">
        <div className={"certbox " + (p.powered ? "" : "no")}>
          <div className="ic">{p.powered ? "✓" : "⚠"}</div>
          <div>
            <div className="t" style={{ color: p.powered ? "var(--green)" : "var(--amber)" }}>
              {p.powered ? "Adequately powered" : "Underpowered design"}
            </div>
            <div className="s">{p.current_n?.toLocaleString()} of {p.required_n?.toLocaleString()} required units
              ({p.pct_powered}%). The DRAFT gate {p.powered ? "passes" : "blocks launch"}.</div>
          </div>
        </div>
        <div style={{ marginTop: 16 }} className="pbar"><span style={{ width: Math.min(100, p.pct_powered) + "%" }} /></div>
      </div>
      <Meta data={data} />
    </div>
  );
}

function Running({ data }) {
  const r = data.readout, t = data.truth, color = r.ci_color;
  const chart = (data.timeseries || []).map((d) => ({ day: d.day, point: d.point,
    range: [d.ci_low, d.ci_high], cs: [d.cs_low ?? d.ci_low, d.cs_high ?? d.ci_high] }));

  return (
    <>
      <div className="grid stat-cards">
        <div className="card stat">
          <div className="lbl">Effect{r.is_pct ? " (vs control)" : " (absolute)"}</div>
          <div className={"headline " + color}><span className="big">{r.headline}</span></div>
          <CIBar readout={r} truth={t} />
        </div>
        <Mini label="95% CI" value={`[${r.ci_low.toFixed(3)}, ${r.ci_high.toFixed(3)}]`} sub={`SE ${r.se.toFixed(4)}`}
          color={r.ci_color === "grey" ? "" : r.ci_color} />
        <Mini label="Power" value={`${data.power.pct_powered}%`} color={data.power.powered ? "green" : "amber"}
          sub={`${data.power.current_n.toLocaleString()} / ${data.power.required_n.toLocaleString()} units`} />
        <div className="card stat">
          <div className="lbl">Validation</div>
          <div className={"certbox " + (t.certified ? "" : "no")} style={{ marginTop: 8 }}>
            <div className="ic">{t.certified ? "✓" : "·"}</div>
            <div>
              <div className="t">{t.certified ? "Certified" : "Uncertified"}</div>
              <div className="s">CI {t.covered ? "covers" : "misses"} the {t.label} · {t.coverage_pct}% coverage</div>
            </div>
          </div>
        </div>
      </div>

      <div className="sc-grid">
        <div className="card cardpad">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
            <h3 className="section-t" style={{ margin: 0 }}>Effect over time — with the always-valid sequence</h3>
            <AdvisoryChip sequential={data.sequential} />
          </div>
          <ResponsiveContainer width="100%" height={252}>
            <ComposedChart data={chart} margin={{ top: 8, right: 14, bottom: 4, left: -6 }}>
              <CartesianGrid stroke="#EEF2F7" vertical={false} />
              <XAxis dataKey="day" tickLine={false} axisLine={{ stroke: "#E7ECF4" }}
                tick={{ fill: "#6B7A90", fontSize: 11 }} />
              <YAxis tickLine={false} axisLine={false} tick={{ fill: "#6B7A90", fontSize: 11 }} width={50} />
              <Tooltip formatter={(v) => (Array.isArray(v) ? `[${v[0].toFixed(3)}, ${v[1].toFixed(3)}]` : v.toFixed(3))}
                contentStyle={{ borderRadius: 10, border: "1px solid #E7ECF4", fontSize: 12 }}
                labelFormatter={(d) => `Day ${d}`} />
              <ReferenceLine y={0} stroke="#CBD5E1" />
              {t && <ReferenceLine y={t.value} stroke="#0E1A2B" strokeDasharray="5 4" strokeOpacity={0.55}
                label={{ value: "true effect", position: "insideTopRight", fill: "#0E1A2B", fontSize: 11, opacity: 0.7 }} />}
              <Area dataKey="cs" stroke="none" fill={LINE[color]} fillOpacity={0.06} />
              <Area dataKey="range" stroke="none" fill={LINE[color]} fillOpacity={0.16} />
              <Line dataKey="point" stroke={LINE[color]} strokeWidth={2.4} dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
          <div style={{ margin: "10px 0 2px" }}><Legend /></div>
          <div className="note">Dark band = fixed-n 95% CI; faint band = the <b>always-valid confidence
            sequence</b> (peek-safe, NB 07). Both narrow around the dashed <b>true effect</b> — proof the
            estimator is right (a real platform can't show this line).</div>
        </div>

        <div style={{ display: "grid", gap: 16 }}>
          <div className="card cardpad">
            <h3 className="section-t">Diagnostics</h3>
            <Diag label="Sample-ratio mismatch (SRM)"
              ok={data.diagnostics.srm_ok} text={`p = ${data.diagnostics.srm_p}`} />
            {data.diagnostics.is_aa && <Diag label="A/A null control"
              ok={data.diagnostics.aa_ok} text={data.diagnostics.aa_ok ? "no false effect" : "FLAGGED"} />}
            <div className="diag-row"><span className="k" style={{ color: "var(--muted)" }}>Arm sizes</span>
              <span className="num" style={{ fontWeight: 600 }}>
                {data.diagnostics.n_control.toLocaleString()} / {data.diagnostics.n_treatment.toLocaleString()}</span></div>
          </div>
          {data.decision_rec && <ShipRec rec={data.decision_rec} />}
          {data.decision && data.decision.ship != null
            ? <Decision decision={data.decision} />
            : <Meta data={data} card />}
        </div>
      </div>
    </>
  );
}

function ShipRec({ rec }) {
  return (
    <div className="card cardpad">
      <h3 className="section-t">Ship recommendation</h3>
      <span className={"badge " + (rec.ship ? "ok" : "no")} style={{ fontSize: 13, padding: "5px 12px" }}>
        {rec.ship ? "✓ Ship" : "✗ Hold"}</span>
      <div className="note" style={{ marginTop: 9, color: "var(--ink-2)", fontSize: 13 }}>{rec.reason}</div>
      <div style={{ marginTop: 8 }}>
        <div className="diag-row"><span className="k" style={{ color: "var(--muted)" }}>Primary — superiority</span>
          <span className={"badge " + (rec.primary_superior ? "ok" : "no")}>{rec.primary_superior ? "✓ met" : "✗ not yet"}</span></div>
        {(rec.guardrails || []).map((g, i) => (
          <div className="diag-row" key={i}><span className="k" style={{ color: "var(--muted)" }}>{g.name} — non-inferior</span>
            <span className={"badge " + (g.non_inferior ? "ok" : "no")}>{g.non_inferior ? "✓ within margin" : "✗ regressed"}</span></div>
        ))}
        {rec.blocked_by_certification &&
          <div className="note" style={{ marginTop: 7, color: "var(--amber)" }}>⚠ also blocked: design not certified vs ground truth</div>}
      </div>
    </div>
  );
}

function Mini({ label, value, sub, color }) {
  return (
    <div className="card stat">
      <div className="lbl">{label}</div>
      <div className={"val num " + (color || "")} style={{ fontSize: 20 }}>{value}</div>
      {sub && <div className="sub num">{sub}</div>}
    </div>
  );
}

function Diag({ label, ok, text }) {
  return (
    <div className="diag-row">
      <span className="k" style={{ color: "var(--muted)" }}>{label}</span>
      <span className={"badge " + (ok ? "ok" : "no")}>{ok ? "✓ " : "✗ "}{text}</span>
    </div>
  );
}

function Decision({ decision }) {
  return (
    <div className="card cardpad">
      <h3 className="section-t">Decision</h3>
      <span className={"badge " + (decision.ship ? "ok" : "no")} style={{ fontSize: 13, padding: "5px 12px" }}>
        {decision.ship ? "✓ Ship" : "✗ Do not ship"}</span>
      <div className="note" style={{ marginTop: 10, color: "var(--ink-2)", fontSize: 13 }}>{decision.rationale}</div>
      {decision.checklist && <ul className="checklist">{decision.checklist.map((c, i) => <li key={i}>{c}</li>)}</ul>}
    </div>
  );
}

function Meta({ data, card }) {
  const body = (
    <>
      <h3 className="section-t">Details</h3>
      <div className="kv"><span className="k">Metric</span><span className="v"><MetricChip metric={data.metric} /></span></div>
      <div className="kv"><span className="k">Design</span><span className="v">{data.design}</span></div>
      <div className="kv"><span className="k">Allocation</span><span className="v">
        {data.allocations ? Object.entries(data.allocations).map(([k, v]) => `${k} ${Math.round(v * 100)}%`).join(" · ") : "—"}</span></div>
      {data.guardrails?.length > 0 &&
        <div className="kv"><span className="k">Guardrails</span><span className="v" style={{ fontWeight: 500 }}>{data.guardrails.join(", ")}</span></div>}
      {data.truth && <div className="kv"><span className="k">Certified vs truth</span>
        <span className="v"><CertifiedBadge truth={data.truth} /></span></div>}
    </>
  );
  return card === undefined ? <div className="card cardpad">{body}</div> : <div className="card cardpad">{body}</div>;
}
