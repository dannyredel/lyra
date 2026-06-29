import React from "react";
import { StateChip, MetricChip, CertifiedBadge, EffectCell, PowerBar, Stat, AdvisoryChip } from "./ui.jsx";

export default function Registry({ experiments, meta, onSelect, onNew }) {
  const running = experiments.filter((e) => e.state === "RUNNING").length;
  const decided = experiments.filter((e) => e.state === "DECIDED").length;
  const withTruth = experiments.filter((e) => e.truth);
  const certified = withTruth.filter((e) => e.truth.certified).length;
  const fdr = meta?.fdr;

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Experiments</h1>
          <p>Every experiment runs on a ground-truth simulator — so the platform can <b>certify</b> each estimate is correct.</p>
        </div>
        <button className="btn primary" onClick={onNew}>+ New experiment</button>
      </div>

      <div className="grid stat-cards">
        <Stat icon="⬡" label="Experiments" value={experiments.length} sub={`${running} running · ${decided} decided`} />
        <Stat icon="◴" label="Running" value={running} sub="live readouts" />
        <Stat icon="✓" label="Certified" value={`${certified}/${withTruth.length}`} sub="cover truth at nominal rate" />
        <Stat icon="⚖" label="Significant (FDR)" value={fdr ? `${fdr.n_significant}/${fdr.n_tested}` : "—"}
          sub={`BH-controlled · ${decided} shipped`} />
      </div>

      <div className="card" style={{ padding: "14px 8px" }}>
        <table className="reg-table">
          <thead>
            <tr>
              <th>Experiment</th><th>Metric</th><th>Owner</th><th>State</th>
              <th>Effect</th><th>Certified</th><th>Power</th>
            </tr>
          </thead>
          <tbody>
            {experiments.map((e) => (
              <tr key={e.id} className="row" onClick={() => onSelect(e.id)}>
                <td><div className="name">{e.name}</div><div className="sub">{e.hypothesis}</div></td>
                <td><MetricChip metric={e.metric} /></td>
                <td>{e.owner}</td>
                <td>
                  <StateChip state={e.state} />
                  {e.sequential && e.state === "RUNNING" &&
                    <div style={{ marginTop: 5 }}><AdvisoryChip sequential={e.sequential} /></div>}
                </td>
                <td><EffectCell readout={e.readout} /></td>
                <td><CertifiedBadge truth={e.truth} /></td>
                <td><PowerBar power={e.power} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
