import React, { useState, useEffect } from "react";
import { api } from "./api.js";

// The governed metric catalog (mirrors chassis/catalog.py). Exported so the create wizard sources its
// dependent-variable picker from the SAME library — that's what enforces one definition per metric.
export const METRIC_CATALOG = [
  { key: "proportion", name: "Conversion rate", type: "proportion", estimand: "risk difference  (p_t − p_c)", variance: "p(1−p)  (Bernoulli)", estimator: "Two-proportion z", when: "Binary outcome — did the user convert?", owner: "Growth DS", version: "1.2", status: "governed" },
  { key: "mean", name: "Value per user", type: "continuous", estimand: "mean difference", variance: "σ²  (sample)", estimator: "Welch t / OLS", when: "Continuous outcome — revenue, time-on-app.", owner: "Core DS", version: "1.0", status: "governed" },
  { key: "ratio", name: "Per-session ratio", type: "ratio", estimand: "ratio of means", variance: "delta method at the randomization unit", estimator: "Delta-method ratio", when: "Randomize by user, measure by session.", owner: "Core DS", version: "1.1", status: "governed" },
  { key: "cuped", name: "CUPED-adjusted", type: "variance-reduction", estimand: "same ATE, tighter CI", variance: "× (1 − ρ²)", estimator: "CUPED + base estimator", when: "Any metric with a predictive pre-period covariate.", owner: "Core DS", version: "0.9", status: "beta" },
  { key: "cluster", name: "Cluster effect", type: "cluster", estimand: "ATE (cluster-robust)", variance: "CR1 / CR3 sandwich", estimator: "ClusterOLS", when: "Cluster-randomized or clustered data (geo, markets).", owner: "Causal DS", version: "1.0", status: "governed" },
  { key: "switchback", name: "Switchback ATE", type: "temporal", estimand: "time-averaged ATE", variance: "cluster-robust on the cell", estimator: "SwitchbackCUPED", when: "Temporal interference — randomize on/off over time.", owner: "Causal DS", version: "0.8", status: "beta" },
];

export default function Metrics({ experiments = [] }) {
  const [metrics, setMetrics] = useState(null);
  useEffect(() => { api.metrics().then((d) => setMetrics(d.metrics)).catch(() => setMetrics(METRIC_CATALOG)); }, []);
  const list = metrics || METRIC_CATALOG;
  const usedBy = (m) => experiments.filter(
    (e) => e.metric && (e.metric.key === m.key || e.metric.type === m.type || e.metric.name === m.name)).length;

  return (
    <>
      <div className="page-head">
        <div><h1>Metric library</h1><p>The single source of truth for <b>outcomes</b>. Every experiment picks its
          dependent variable from here — so a term like "conversion rate" has <b>one</b> definition, estimand, and
          estimator across the whole platform, not a different one in each analysis.</p></div>
      </div>
      <div className="card" style={{ padding: "14px 8px" }}>
        <table className="reg-table">
          <thead><tr>
            <th>Metric (dependent variable)</th><th>Estimand</th><th>Variance</th><th>Estimator</th><th>When to use</th><th>Owner</th><th className="num">Used by</th><th>Status</th>
          </tr></thead>
          <tbody>
            {list.map((m) => {
              const n = usedBy(m);
              return (
                <tr key={m.key}>
                  <td><div className="name">{m.name}</div><div className="sub">{m.type} · v{m.version}</div></td>
                  <td className="num">{m.estimand}</td>
                  <td style={{ color: "var(--ink-2)" }}>{m.variance}</td>
                  <td><span className="tag">{m.estimator}</span></td>
                  <td style={{ color: "var(--muted)", maxWidth: 220 }}>{m.when}</td>
                  <td>{m.owner}</td>
                  <td className="num" style={{ color: n ? "var(--ink)" : "var(--muted)" }}>{n ? `${n} live` : "—"}</td>
                  <td><span className={"badge " + (m.status === "governed" ? "ok" : "no")}>{m.status}</span></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="note" style={{ marginTop: 12 }}>Governance is the point: an experiment can't invent its own
        "conversion rate" — it <b>references</b> a metric here, which fixes the estimand and the estimator. Field
        harmonization (mapping each source's raw <code>cost/value/spend</code> naming into one clean field) happens
        upstream, so here you only compose already-clean, agreed definitions.</p>
    </>
  );
}
