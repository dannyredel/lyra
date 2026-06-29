import { useEffect, useState } from "react";
import {
  ComposedChart, Area, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";

const DATA = import.meta.env.BASE_URL + "data/";
const CAT_COLOR = {
  puzzle: "#6ea8fe", casino: "#e9548a", rpg: "#9d7bff", survey: "#3fb68b", shopping: "#e08c4f",
};

export default function WorldView() {
  const [w, setW] = useState(null);
  useEffect(() => {
    fetch(DATA + "world.json").then((r) => r.json()).then(setW).catch(() => {});
  }, []);
  if (!w) return <p className="sub" style={{ marginTop: 30 }}>Loading world…</p>;

  const peakActive = Math.max(...w.timeseries.map((d) => d.active));
  const totalConv = w.timeseries.reduce((s, d) => s + d.conversions, 0);
  const totalChurn = w.timeseries[w.timeseries.length - 1].churned_cumulative;
  const byAdv = {};
  w.offers.forEach((o) => { (byAdv[o.advertiser] ||= []).push(o); });

  return (
    <>
      <h1 className="page">Market / world view</h1>
      <p className="sub">
        The living simulated marketplace the experiments run inside — the reward-seeking user
        population and the advertiser offer wall, replayed over {w.timeseries.length} simulated days.
      </p>

      <div className="grid cols-3">
        <div className="card"><h3>Peak active users</h3><div className="stat">{peakActive.toLocaleString()}</div></div>
        <div className="card"><h3>Conversions</h3><div className="stat">{totalConv.toLocaleString()}</div></div>
        <div className="card"><h3>Churned (cumulative)</h3><div className="stat" style={{ color: "var(--red)" }}>{totalChurn.toLocaleString()}</div></div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3>Population &amp; conversions over the replayed clock</h3>
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={w.timeseries} margin={{ top: 8, right: 16, bottom: 18, left: 6 }}>
            <CartesianGrid stroke="#222734" vertical={false} />
            <XAxis dataKey="day" stroke="#6b7280" tick={{ fill: "#9aa3b2", fontSize: 12 }}
              label={{ value: "simulated day", position: "insideBottom", offset: -6, fill: "#9aa3b2", fontSize: 12 }} />
            <YAxis yAxisId="l" stroke="#6b7280" tick={{ fill: "#9aa3b2", fontSize: 12 }} width={56} />
            <YAxis yAxisId="r" orientation="right" stroke="#6b7280" tick={{ fill: "#9aa3b2", fontSize: 12 }} width={56} />
            <Tooltip contentStyle={{ background: "#161922", border: "1px solid #262b36", borderRadius: 8, color: "#e7e9ee" }} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Area yAxisId="l" dataKey="active" name="active users" stroke="#6ea8fe" fill="#6ea8fe" fillOpacity={0.15} isAnimationActive={false} />
            <Bar yAxisId="r" dataKey="conversions" name="conversions/day" fill="#3fb68b" opacity={0.7} isAnimationActive={false} />
            <Line yAxisId="r" dataKey="churn" name="churn/day" stroke="#e08c4f" dot={false} strokeWidth={2} isAnimationActive={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3>The offer wall — {w.meta.n_offers} offers across {w.meta.n_advertisers} advertisers</h3>
        <div className="legend" style={{ marginBottom: 12 }}>
          {w.meta.categories.map((c) => (
            <span key={c}><i style={{ background: CAT_COLOR[c] || "#888", height: 10, width: 10, borderRadius: 3 }} />{c}</span>
          ))}
        </div>
        {Object.entries(byAdv).map(([adv, offers]) => (
          <div key={adv} className="advrow">
            <span className="advname">{adv}</span>
            <div className="wall">
              {offers.map((o) => (
                <div key={o.offer_id} className="offer" title={`${o.offer_id} · ${o.category}\npayout ${o.payout} · reward ${o.reward} · budget ${o.budget_cap}/day`}
                  style={{ borderColor: CAT_COLOR[o.category] || "#888" }}>
                  <span className="opay">{o.payout.toFixed(1)}</span>
                  <span className="orew" style={{ color: CAT_COLOR[o.category] }}>▸{o.reward.toFixed(1)}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
        <p className="hint">Each tile is an offer (advertiser campaign): payout the advertiser pays, ▸ the reward the user
          sees (payout × pass-through). The platform keeps the difference — the OEC margin. Border = category.</p>
      </div>
    </>
  );
}
