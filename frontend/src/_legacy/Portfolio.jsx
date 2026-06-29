import { DecisionBadge, SrmBadge, EffectCell, fmt } from "./bits.jsx";

export default function Portfolio({ portfolio, onOpen }) {
  const exps = portfolio.experiments;
  return (
    <>
      <h1 className="page">Portfolio</h1>
      <p className="sub">
        All running experiments — the data-science team's home page. Click a row for the detail view.
      </p>

      <table className="exp">
        <thead>
          <tr>
            <th>Experiment</th>
            <th>Alloc</th>
            <th>Naive effect</th>
            <th>Corrected</th>
            <th>Ground truth</th>
            <th>Health</th>
            <th>Decision</th>
          </tr>
        </thead>
        <tbody>
          {exps.map((e) => (
            <tr className="row" key={e.id} onClick={() => onOpen(e.id)}>
              <td>
                <div className="expname"><span className="id">{e.id}</span></div>
                <div className="expsub">
                  {e.advertiser} · {e.type} · {e.randomization}-randomized
                </div>
              </td>
              <td className="num">{Math.round(e.allocation * 100)}%</td>
              <td><EffectCell eff={e.naive} /></td>
              <td>{e.corrected ? <EffectCell eff={e.corrected} /> : <span style={{ color: "var(--muted)" }}>—</span>}</td>
              <td className="eff">{fmt(e.ground_truth)}</td>
              <td><SrmBadge srm={e.srm} /></td>
              <td><DecisionBadge decision={e.decision} /></td>
            </tr>
          ))}
        </tbody>
      </table>

      <p className="hint">
        “Naive” is the user-level difference-in-means a typical team would read; “Corrected” is the
        interference-aware estimator (budget-split for reward sizing; cluster-robust for
        cluster-randomized). The gap between them — and to ground truth — is the bias this platform
        exposes. Ramped experiments are analyzed at fixed allocation to avoid cohort-selection
        (see notebook 03 / DECISIONS D-13).
      </p>
    </>
  );
}
