import React from "react";
import { StateChip } from "./ui.jsx";

// Portfolio trust diagnostics — the checks every experiment must pass before its readout is believed.
// Reads the static snapshot (each experiment carries `diagnostics` + `truth`), so it works with no backend.
export default function Health({ experiments = [] }) {
  const diag = experiments.filter((e) => e.diagnostics);
  const srmClean = diag.filter((e) => e.diagnostics.srm_ok).length;
  const aa = diag.filter((e) => e.diagnostics.is_aa);
  const aaClean = aa.filter((e) => e.diagnostics.aa_ok).length;
  const truthful = experiments.filter((e) => e.truth);
  const certified = truthful.filter((e) => e.truth.certified).length;

  const Stat = ({ label, value, sub, good }) => (
    <div className="card stat">
      <div className="lbl">{label}</div>
      <div className={"val " + (good === true ? "green" : good === false ? "amber" : "")}>{value}</div>
      <div className="sub">{sub}</div>
    </div>
  );

  return (
    <>
      <div className="page-head">
        <div><h1>Health</h1><p>The trust diagnostics every experiment must clear before its readout is believed —
          a balanced split (<b>SRM</b>), null <b>A/A</b> controls, and recovery <b>certified against ground
          truth</b> — monitored across the whole portfolio.</p></div>
      </div>

      <div className="grid stat-cards">
        <Stat label="Experiments" value={experiments.length} sub="in the portfolio" />
        <Stat label="SRM balanced" value={`${srmClean}/${diag.length}`} sub="split matches the target allocation"
          good={srmClean === diag.length} />
        <Stat label="A/A nulls clean" value={aa.length ? `${aaClean}/${aa.length}` : "—"}
          sub="no false effect on a null test" good={aa.length ? aaClean === aa.length : undefined} />
        <Stat label="Certified vs truth" value={`${certified}/${truthful.length}`}
          sub="estimator recovers the planted effect" good={certified === truthful.length} />
      </div>

      <div className="card" style={{ padding: "14px 8px" }}>
        <table className="reg-table">
          <thead><tr>
            <th>Experiment</th><th>State</th><th>SRM (split balance)</th><th>A/A null</th>
            <th>Control / treatment</th><th>Certified vs truth</th>
          </tr></thead>
          <tbody>
            {experiments.map((e) => {
              const d = e.diagnostics || {};
              const nC = d.n_control, nT = d.n_treatment;
              return (
                <tr key={e.id}>
                  <td><div className="name">{e.name}</div><div className="sub">{e.design} · {e.metric?.type}</div></td>
                  <td><StateChip state={e.state} /></td>
                  <td>{d.srm_p != null
                    ? <span className={"badge " + (d.srm_ok ? "ok" : "no")}>{d.srm_ok ? "✓ balanced" : "✗ mismatch"} · p={d.srm_p}</span>
                    : <span style={{ color: "var(--muted)" }}>—</span>}</td>
                  <td>{d.is_aa
                    ? <span className={"badge " + (d.aa_ok ? "ok" : "no")}>{d.aa_ok ? "✓ no effect" : "✗ flagged"}</span>
                    : <span className="tag">not an A/A</span>}</td>
                  <td className="num">{nC != null ? `${nC.toLocaleString()} / ${nT.toLocaleString()}` : "—"}</td>
                  <td>{e.truth
                    ? <span className={"badge " + (e.truth.certified ? "ok" : "no")}>
                        {e.truth.certified ? `✓ certified · ${e.truth.coverage_pct}%` : "uncertified"}</span>
                    : <span style={{ color: "var(--muted)" }}>—</span>}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="note" style={{ marginTop: 12 }}>This is the "trustworthy experimentation" layer: a result is
        only shipped if the split is balanced, the A/A controls are null, and — uniquely here — the estimator is
        <b> certified to recover the known ground truth</b>. The detailed per-experiment diagnostics live on each
        scorecard.</p>
    </>
  );
}
