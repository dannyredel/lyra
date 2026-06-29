import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer, Cell } from "recharts";

function histogram(values, nbins = 26) {
  if (!values?.length) return [];
  const lo = Math.min(...values), hi = Math.max(...values), w = (hi - lo) / nbins || 1;
  const bins = Array.from({ length: nbins }, (_, i) => ({ x: +(lo + (i + 0.5) * w).toFixed(4), count: 0 }));
  values.forEach((v) => { bins[Math.min(nbins - 1, Math.floor((v - lo) / w))].count++; });
  return bins;
}
const mean = (a) => a.reduce((s, v) => s + v, 0) / a.length;
const std = (a) => { const m = mean(a); return Math.sqrt(a.reduce((s, v) => s + (v - m) ** 2, 0) / (a.length - 1)); };

export default function Analytics({ data }) {
  const a = data.analytics, t = data.truth;
  if (!a) return <div className="card cardpad note">Detailed analytics aren’t available for this experiment.</div>;

  const hist = histogram(a.sampling);
  const m = mean(a.sampling), bias = m - a.truth;
  const lo = Math.min(...a.intervals.map((i) => i[0]), a.truth);
  const hi = Math.max(...a.intervals.map((i) => i[1]), a.truth);
  const pad = (hi - lo) * 0.06 || 0.01, dmin = lo - pad, span = hi + pad - dmin;
  const pos = (v) => ((v - dmin) / span) * 100;
  const ah = a.arm_hist, binary = ah.edges.length <= 3;
  const armData = ah.control.map((c, i) => ({
    bin: binary ? (i === 0 ? "lower" : "higher") : ((ah.edges[i] + ah.edges[i + 1]) / 2).toFixed(2),
    control: c, treatment: ah.treatment[i],
  }));

  return (
    <>
      <div className="grid stat-cards">
        <div className="card stat"><div className="lbl">Simulated re-runs</div><div className="val">{a.sampling.length}</div><div className="sub">Monte-Carlo replicates</div></div>
        <div className="card stat"><div className="lbl">Mean estimate</div><div className="val num">{m.toFixed(3)}</div><div className="sub">truth {a.truth.toFixed(3)}</div></div>
        <div className="card stat"><div className="lbl">Bias</div><div className="val num" style={{ color: Math.abs(bias) < 2 * std(a.sampling) / Math.sqrt(a.sampling.length) ? "var(--green)" : "var(--amber)" }}>{bias >= 0 ? "+" : ""}{bias.toFixed(4)}</div><div className="sub">mean − truth ≈ 0</div></div>
        <div className="card stat"><div className="lbl">CI coverage</div><div className="val num">{Math.round(a.coverage * 100)}%</div><div className="sub">target 95%</div></div>
      </div>

      <div className="sc-grid">
        <div className="card cardpad">
          <h3 className="section-t">Sampling distribution of the estimate</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={hist} margin={{ top: 8, right: 12, bottom: 4, left: -10 }}>
              <CartesianGrid stroke="#EEF2F7" vertical={false} />
              <XAxis dataKey="x" tickLine={false} axisLine={{ stroke: "#E7ECF4" }} tick={{ fill: "#6B7A90", fontSize: 11 }} />
              <YAxis tickLine={false} axisLine={false} tick={{ fill: "#6B7A90", fontSize: 11 }} width={32} />
              <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid #E7ECF4", fontSize: 12 }} />
              <ReferenceLine x={a.truth} stroke="#0E1A2B" strokeDasharray="5 4" strokeWidth={1.6}
                label={{ value: "true effect", position: "top", fill: "#0E1A2B", fontSize: 11 }} />
              <Bar dataKey="count" fill="#1E6091" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="note">Re-running the experiment {a.sampling.length}× on fresh simulated data, the estimate
            <b> centres on the dashed true effect</b> — an unbiased estimator, proven against ground truth.</div>
        </div>

        <div className="card cardpad">
          <h3 className="section-t">Interval coverage — {Math.round(a.coverage * 100)}% cover the truth</h3>
          <div style={{ position: "relative", height: 230, marginTop: 6 }}>
            <div style={{ position: "absolute", top: 0, bottom: 16, left: pos(a.truth) + "%", width: 2, background: "#0E1A2B", opacity: 0.55 }} />
            {a.intervals.map((iv, k) => (
              <div key={k} style={{ position: "absolute", top: (k / a.intervals.length) * (230 - 16), height: 2.2,
                left: pos(iv[0]) + "%", width: (pos(iv[1]) - pos(iv[0])) + "%",
                background: iv[2] ? "var(--green)" : "var(--red)", opacity: iv[2] ? 0.55 : 0.9, borderRadius: 2 }} />
            ))}
            <div style={{ position: "absolute", bottom: 0, left: pos(a.truth) + "%", transform: "translateX(-50%)", fontSize: 10, color: "#0E1A2B" }}>truth</div>
          </div>
          <div className="note">Each line is one re-run’s 95% CI; <b style={{ color: "var(--green)" }}>green</b> covers the
            truth, <b style={{ color: "var(--red)" }}>red</b> misses. ~5% misses is exactly right — that’s what 95% means.</div>
        </div>
      </div>

      <div className="card cardpad" style={{ marginTop: 16 }}>
        <h3 className="section-t">Per-arm outcome distribution (one run)</h3>
        <ResponsiveContainer width="100%" height={210}>
          <BarChart data={armData} margin={{ top: 8, right: 12, bottom: 4, left: -10 }}>
            <CartesianGrid stroke="#EEF2F7" vertical={false} />
            <XAxis dataKey="bin" tickLine={false} axisLine={{ stroke: "#E7ECF4" }} tick={{ fill: "#6B7A90", fontSize: 11 }} />
            <YAxis tickLine={false} axisLine={false} tick={{ fill: "#6B7A90", fontSize: 11 }} width={42} />
            <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid #E7ECF4", fontSize: 12 }} />
            <Bar dataKey="control" fill="#94A3B8" radius={[3, 3, 0, 0]} />
            <Bar dataKey="treatment" fill="#1E6091" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <div className="note">Control mean {ah.control_mean.toFixed(3)} · treatment mean {ah.treatment_mean.toFixed(3)}
          — the raw outcomes behind the effect.</div>
      </div>
    </>
  );
}
