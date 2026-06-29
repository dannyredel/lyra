import React, { useState, useEffect } from "react";
import { api } from "./api.js";

// static fallback (mirrors chassis/catalog.py) so the catalog renders without the backend
const STATIC = [
  { key: "proportion", name: "Conversion rate", type: "proportion", estimand: "risk difference  (p_t − p_c)", variance: "p(1−p)  (Bernoulli)", estimator: "Two-proportion z", when: "Binary outcome — did the user convert?", owner: "Growth DS", version: "1.2", status: "governed" },
  { key: "mean", name: "Value per user", type: "continuous", estimand: "mean difference", variance: "σ²  (sample)", estimator: "Welch t / OLS", when: "Continuous outcome — revenue, time-on-app.", owner: "Core DS", version: "1.0", status: "governed" },
  { key: "ratio", name: "Per-session ratio", type: "ratio", estimand: "ratio of means", variance: "delta method at the randomization unit", estimator: "Delta-method ratio", when: "Randomize by user, measure by session.", owner: "Core DS", version: "1.1", status: "governed" },
  { key: "cuped", name: "CUPED-adjusted", type: "variance-reduction", estimand: "same ATE, tighter CI", variance: "× (1 − ρ²)", estimator: "CUPED + base estimator", when: "Any metric with a predictive pre-period covariate.", owner: "Core DS", version: "0.9", status: "beta" },
  { key: "cluster", name: "Cluster effect", type: "cluster", estimand: "ATE (cluster-robust)", variance: "CR1 / CR3 sandwich", estimator: "ClusterOLS", when: "Cluster-randomized or clustered data (geo, markets).", owner: "Causal DS", version: "1.0", status: "governed" },
  { key: "switchback", name: "Switchback ATE", type: "temporal", estimand: "time-averaged ATE", variance: "cluster-robust on the cell", estimator: "SwitchbackCUPED", when: "Temporal interference — randomize on/off over time.", owner: "Causal DS", version: "0.8", status: "beta" },
];

export default function Metrics() {
  const [metrics, setMetrics] = useState(null);
  useEffect(() => { api.metrics().then((d) => setMetrics(d.metrics)).catch(() => setMetrics(STATIC)); }, []);
  const list = metrics || STATIC;

  return (
    <>
      <div className="page-head">
        <div><h1>Metrics</h1><p>The <b>governed</b> metric catalog — versioned definitions with an estimand,
          a variance model, and the estimator that computes them. Each maps to a typed estimator in <code>lyra</code>.</p></div>
      </div>
      <div className="card" style={{ padding: "14px 8px" }}>
        <table className="reg-table">
          <thead><tr>
            <th>Metric</th><th>Estimand</th><th>Variance</th><th>Estimator</th><th>When to use</th><th>Owner</th><th>Status</th>
          </tr></thead>
          <tbody>
            {list.map((m) => (
              <tr key={m.key}>
                <td><div className="name">{m.name}</div><div className="sub">{m.type} · v{m.version}</div></td>
                <td className="num">{m.estimand}</td>
                <td style={{ color: "var(--ink-2)" }}>{m.variance}</td>
                <td><span className="tag">{m.estimator}</span></td>
                <td style={{ color: "var(--muted)", maxWidth: 220 }}>{m.when}</td>
                <td>{m.owner}</td>
                <td><span className={"badge " + (m.status === "governed" ? "ok" : "no")}>{m.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
