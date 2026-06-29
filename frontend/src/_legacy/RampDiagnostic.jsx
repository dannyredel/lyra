import { useEffect, useState } from "react";
import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer,
} from "recharts";
import { fmt } from "./bits.jsx";

const DATA = import.meta.env.BASE_URL + "data/";

export default function RampDiagnostic() {
  const [rd, setRd] = useState(null);
  useEffect(() => {
    fetch(DATA + "ramp_diagnostic.json").then((r) => r.json()).then(setRd).catch(() => {});
  }, []);

  if (!rd) return <p className="sub" style={{ marginTop: 30 }}>Loading diagnostic…</p>;

  const data = rd.points.map((p) => ({
    alloc: Math.round(p.allocation * 100),
    naive: p.naive.point, naive_range: [p.naive.ci_low, p.naive.ci_high],
    corrected: p.corrected.point, corrected_range: [p.corrected.ci_low, p.corrected.ci_high],
  }));
  const naiveBias = rd.points[rd.points.length - 1].naive.point - rd.ground_truth;
  const corrBias = rd.points[rd.points.length - 1].corrected.point - rd.ground_truth;

  return (
    <>
      <h1 className="page">Interference / ramp diagnostic</h1>
      <p className="sub">
        The differentiator off-the-shelf tools can't show: the <strong>same experiment</strong> run at
        several treatment allocations. Because we authored the simulator, we know the true effect — so
        we can watch the naive A/B <strong>drift away from it</strong> as treatment share grows, while
        the interference-aware estimator stays close.
      </p>

      <div className="card">
        <h3>{rd.experiment} — estimated effect vs treatment allocation</h3>
        <ResponsiveContainer width="100%" height={380}>
          <ComposedChart data={data} margin={{ top: 10, right: 18, bottom: 18, left: 6 }}>
            <CartesianGrid stroke="#222734" vertical={false} />
            <XAxis dataKey="alloc" stroke="#6b7280" tick={{ fill: "#9aa3b2", fontSize: 12 }}
              tickFormatter={(v) => v + "%"}
              label={{ value: "treatment allocation", position: "insideBottom", offset: -6, fill: "#9aa3b2", fontSize: 12 }} />
            <YAxis stroke="#6b7280" tick={{ fill: "#9aa3b2", fontSize: 12 }} width={70}
              tickFormatter={(v) => v.toFixed(2)}
              label={{ value: "effect (margin / user)", angle: -90, position: "insideLeft", fill: "#9aa3b2", fontSize: 12 }} />
            <Tooltip
              contentStyle={{ background: "#161922", border: "1px solid #262b36", borderRadius: 8, color: "#e7e9ee" }}
              labelFormatter={(v) => `allocation ${v}%`}
              formatter={(val, name) => {
                if (Array.isArray(val)) return [`[${val[0].toFixed(3)}, ${val[1].toFixed(3)}]`, "95% CI"];
                return [Number(val).toFixed(4), name];
              }} />
            <ReferenceLine y={rd.ground_truth} stroke="#3fb68b" strokeDasharray="6 4" strokeWidth={2}
              label={{ value: `true ATE ${fmt(rd.ground_truth)}`, position: "insideBottomRight", fill: "#3fb68b", fontSize: 12 }} />
            <Area dataKey="naive_range" stroke="none" fill="#e9548a" fillOpacity={0.13} isAnimationActive={false} />
            <Area dataKey="corrected_range" stroke="none" fill="#6ea8fe" fillOpacity={0.13} isAnimationActive={false} />
            <Line dataKey="naive" name="naive" stroke="#e9548a" strokeWidth={2.6}
              dot={{ r: 4, fill: "#e9548a" }} isAnimationActive={false} />
            <Line dataKey="corrected" name="budget-split" stroke="#6ea8fe" strokeWidth={2.6}
              dot={{ r: 4, fill: "#6ea8fe" }} isAnimationActive={false} />
          </ComposedChart>
        </ResponsiveContainer>
        <div className="legend">
          <span><i style={{ background: "#e9548a" }} />naive (shared budget)</span>
          <span><i style={{ background: "#6ea8fe" }} />budget-split (corrected)</span>
          <span><i className="dash" style={{ borderColor: "#3fb68b" }} />true global ATE (shadow runs)</span>
        </div>
      </div>

      <div className="grid cols-3" style={{ marginTop: 16 }}>
        <div className="card">
          <h3>True effect</h3>
          <div className="stat" style={{ color: "#3fb68b" }}>{fmt(rd.ground_truth)}</div>
          <div className="hint" style={{ marginTop: 2 }}>global ATE from counterfactual shadow runs</div>
        </div>
        <div className="card">
          <h3>Naive bias @ 50%</h3>
          <div className="stat" style={{ color: "#e9548a" }}>{fmt(naiveBias)}</div>
          <div className="hint" style={{ marginTop: 2 }}>grows with allocation — interference</div>
        </div>
        <div className="card">
          <h3>Budget-split bias @ 50%</h3>
          <div className="stat" style={{ color: "#6ea8fe" }}>{fmt(corrBias)}</div>
          <div className="hint" style={{ marginTop: 2 }}>
            {Math.round((1 - Math.abs(corrBias) / Math.abs(naiveBias || 1)) * 100)}% of the naive bias removed
          </div>
        </div>
      </div>

      <p className="hint">
        Mechanism: treated users (richer reward) deplete the shared daily budget faster, starving the
        control arm — so the naive contrast is "treated vs a progressively-starved control," and the
        gap to truth widens with allocation. Budget-split gives each arm its own pool, restoring the
        scarcity each arm would face on its own. (Multi-advertiser world ⇒ a residual remains from a
        second channel, effort substitution.) Each point is a separate fixed-allocation run.
      </p>
    </>
  );
}
