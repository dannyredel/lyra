import { useEffect, useState } from "react";
import Portfolio from "./Portfolio.jsx";
import ExperimentDetail from "./ExperimentDetail.jsx";
import RampDiagnostic from "./RampDiagnostic.jsx";
import WorldView from "./WorldView.jsx";

const DATA = import.meta.env.BASE_URL + "data/";

export default function App() {
  const [portfolio, setPortfolio] = useState(null);
  const [view, setView] = useState("portfolio"); // "portfolio" | "ramp"
  const [selected, setSelected] = useState(null); // experiment id or null
  const [detail, setDetail] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(DATA + "portfolio.json")
      .then((r) => r.json())
      .then(setPortfolio)
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    if (!selected) { setDetail(null); return; }
    setDetail(null);
    fetch(DATA + `experiment_${selected}.json`)
      .then((r) => r.json())
      .then(setDetail)
      .catch((e) => setError(String(e)));
  }, [selected]);

  const meta = portfolio?.meta;

  return (
    <>
      <header className="top">
        <div className="inner">
          <span className="brand">Vega<span className="dot">·</span> Experiment Platform</span>
          <nav className="tabs">
            <button className={view === "portfolio" && !selected ? "tab on" : "tab"}
              onClick={() => { setView("portfolio"); setSelected(null); }}>Portfolio</button>
            <button className={view === "ramp" && !selected ? "tab on" : "tab"}
              onClick={() => { setView("ramp"); setSelected(null); }}>Interference diagnostic</button>
            <button className={view === "world" && !selected ? "tab on" : "tab"}
              onClick={() => { setView("world"); setSelected(null); }}>World</button>
          </nav>
          {meta && (
            <span className="meta">
              <b>{meta.n_users.toLocaleString()}</b> users · <b>{meta.horizon_days}</b>d · α=<b>{meta.alpha}</b>
            </span>
          )}
        </div>
      </header>

      <div className="wrap">
        {error && <p style={{ color: "var(--red)" }}>Failed to load data: {error}</p>}
        {!portfolio && !error && <p className="sub" style={{ marginTop: 40 }}>Loading…</p>}

        {portfolio && selected && (
          <ExperimentDetail detail={detail} onBack={() => setSelected(null)} />
        )}
        {portfolio && !selected && view === "portfolio" && (
          <Portfolio portfolio={portfolio} onOpen={setSelected} />
        )}
        {portfolio && !selected && view === "ramp" && <RampDiagnostic />}
        {portfolio && !selected && view === "world" && <WorldView />}

        <footer className="foot">
          Read-only replay of a recorded event log on a simulated clock (no live streaming). Figures
          are the inference library's estimates over the log; ground truth is from counterfactual
          shadow runs. Built with React + Recharts.
        </footer>
      </div>
    </>
  );
}
