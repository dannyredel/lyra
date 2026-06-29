import React from "react";
import { StateChip } from "./ui.jsx";

export default function Decisions({ experiments, onSelect }) {
  const rows = experiments.filter((e) => e.decision_rec || (e.decision && e.decision.ship != null));
  const shippable = rows.filter((e) => e.decision_rec?.ship).length;
  const blocked = rows.filter((e) => e.decision_rec && !e.decision_rec.ship).length;

  return (
    <>
      <div className="page-head">
        <div><h1>Decisions</h1><p>The ship rule across the portfolio — <b>OEC superiority ∧ guardrails
          non-inferior ∧ certified</b>. A recommendation for every experiment; the recorded call once decided.</p></div>
      </div>
      <div className="grid stat-cards" style={{ gridTemplateColumns: "repeat(3,1fr)" }}>
        <div className="card stat"><div className="lbl">Recommendations</div><div className="val">{rows.length}</div></div>
        <div className="card stat"><div className="lbl">Ship</div><div className="val" style={{ color: "var(--green)" }}>{shippable}</div></div>
        <div className="card stat"><div className="lbl">Hold</div><div className="val" style={{ color: "var(--amber)" }}>{blocked}</div></div>
      </div>
      <div className="card" style={{ padding: "14px 8px" }}>
        <table className="reg-table">
          <thead><tr><th>Experiment</th><th>State</th><th>Recommendation</th><th>Rationale</th><th>Recorded</th></tr></thead>
          <tbody>
            {rows.map((e) => {
              const rec = e.decision_rec, dec = e.decision;
              return (
                <tr key={e.id} className="row" onClick={() => onSelect(e.id)}>
                  <td><div className="name">{e.name}</div></td>
                  <td><StateChip state={e.state} /></td>
                  <td>{rec ? <span className={"badge " + (rec.ship ? "ok" : "no")}>{rec.ship ? "✓ Ship" : "✗ Hold"}</span> : "—"}</td>
                  <td style={{ color: "var(--muted)", maxWidth: 320 }}>{rec?.reason}</td>
                  <td>{dec && dec.ship != null
                    ? <span className={"badge " + (dec.ship ? "ok" : "no")}>{dec.ship ? "shipped" : "held"}</span>
                    : <span style={{ color: "var(--muted)" }}>—</span>}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}
