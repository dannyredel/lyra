import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer,
} from "recharts";
import { DecisionBanner, SrmBadge, fmt, pct } from "./bits.jsx";

export default function ExperimentDetail({ detail, onBack }) {
  if (!detail) {
    return (
      <>
        <span className="crumb" onClick={onBack}>← Portfolio</span>
        <p className="sub">Loading experiment…</p>
      </>
    );
  }

  const ts = (detail.timeseries || []).map((d) => ({ ...d, range: [d.ci_low, d.ci_high] }));
  const gtRate = detail.ground_truth_rate;

  return (
    <>
      <span className="crumb" onClick={onBack}>← Portfolio</span>
      <h1 className="page">{detail.id}</h1>
      <p className="sub">
        {detail.advertiser} · {detail.type} · {detail.randomization}-randomized · primary metric{" "}
        <code>{detail.primary_metric}</code>
      </p>

      <DecisionBanner decision={detail.decision} />

      <p style={{ color: "var(--ink)", maxWidth: 720, marginTop: -8 }}>
        <strong>Hypothesis.</strong> <span style={{ color: "var(--muted)" }}>{detail.hypothesis}</span>
      </p>

      <div className="grid cols-2" style={{ marginTop: 18 }}>
        {/* effect-over-time chart */}
        <div className="card">
          <h3>Effect over the simulated clock (margin / user / day)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={ts} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
              <CartesianGrid stroke="#222734" vertical={false} />
              <XAxis dataKey="day" stroke="#6b7280" tick={{ fill: "#9aa3b2", fontSize: 12 }}
                label={{ value: "simulated day", position: "insideBottom", offset: -2, fill: "#9aa3b2", fontSize: 12 }} />
              <YAxis stroke="#6b7280" tick={{ fill: "#9aa3b2", fontSize: 12 }} width={64}
                tickFormatter={(v) => v.toFixed(3)} />
              <Tooltip
                contentStyle={{ background: "#161922", border: "1px solid #262b36", borderRadius: 8, color: "#e7e9ee" }}
                formatter={(v, name) => {
                  if (name === "range") return [`[${v[0].toFixed(4)}, ${v[1].toFixed(4)}]`, "95% CI"];
                  return [Number(v).toFixed(4), "effect"];
                }}
                labelFormatter={(d) => `day ${d}`} />
              <Area dataKey="range" stroke="none" fill="#e9548a" fillOpacity={0.16} isAnimationActive={false} />
              <Line dataKey="point" stroke="#e9548a" strokeWidth={2.4} dot={false} isAnimationActive={false} />
              {gtRate !== undefined && (
                <ReferenceLine y={gtRate} stroke="#3fb68b" strokeDasharray="5 4" strokeWidth={2}
                  label={{ value: `ground truth ${fmt(gtRate)}`, position: "insideTopRight", fill: "#3fb68b", fontSize: 11 }} />
              )}
              <ReferenceLine y={0} stroke="#46506a" strokeWidth={1} />
            </ComposedChart>
          </ResponsiveContainer>
          <div className="legend">
            <span><i style={{ background: "#e9548a" }} />naive effect (point + 95% CI band)</span>
            <span><i className="dash" style={{ borderColor: "#3fb68b" }} />ground-truth rate (shadow runs)</span>
          </div>
          <p className="hint">
            The band <strong>narrows</strong> as the experiment accrues days (more precision). The
            naive estimate converges <em>short of</em> the green ground-truth line — that visible gap
            is the interference bias the corrected estimator removes.
          </p>
        </div>

        {/* headline numbers */}
        <div className="card">
          <h3>Full-horizon effect (margin / user)</h3>
          <div className="stat" style={{ color: "#e9548a" }}>{fmt(detail.naive?.point)}</div>
          <div className="hint" style={{ marginTop: 0 }}>naive difference-in-means</div>

          <div style={{ marginTop: 16 }}>
            <div className="kv"><span className="k">Corrected (interference-aware)</span>
              <span className="v" style={{ color: "#6ea8fe" }}>{detail.corrected ? fmt(detail.corrected.point) : "—"}</span></div>
            <div className="kv"><span className="k">Ground truth (shadow runs)</span>
              <span className="v" style={{ color: "#3fb68b" }}>{fmt(detail.ground_truth)}</span></div>
            <div className="kv"><span className="k">Naive bias vs truth</span>
              <span className="v">{fmt((detail.naive?.point ?? 0) - (detail.ground_truth ?? 0))}</span></div>
            <div className="kv"><span className="k">p-value (naive)</span>
              <span className="v">{detail.naive?.p_value?.toExponential?.(1) ?? "—"}</span></div>
            <div className="kv"><span className="k">n (treatment / control)</span>
              <span className="v">{detail.naive?.n_treatment?.toLocaleString()} / {detail.naive?.n_control?.toLocaleString()}</span></div>
            <div className="kv"><span className="k">Randomization SRM</span>
              <span className="v"><SrmBadge srm={detail.srm} /></span></div>
          </div>
        </div>
      </div>

      {/* guardrails */}
      <div className="card" style={{ marginTop: 16 }}>
        <h3>Guardrails</h3>
        {detail.guardrails?.map((g) => (
          <div className="kv" key={g.name}>
            <span className="k">{g.name}</span>
            <span className="v">
              {g.computed === false ? (
                <span style={{ color: "var(--muted)" }}>{g.note}</span>
              ) : (
                <>
                  {fmt(g.rel_change * 100, 1)}% vs control{"  "}
                  <span className={`badge ${g.breached ? "warn" : "ok"}`} style={{ marginLeft: 8 }}>
                    {g.breached ? `⚠ breached (cap ${pct(g.threshold_rel, 0)})` : "✓ within cap"}
                  </span>
                </>
              )}
            </span>
          </div>
        ))}
        <p className="hint">
          A breach triggers the kill-switch in the decision logic (ramp auto-rollback). ROAS and D7
          retention are wired in the incrementality / long-term legs (M4).
        </p>
      </div>
    </>
  );
}
