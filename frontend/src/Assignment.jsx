import React, { useState } from "react";
import { api } from "./api.js";

export default function Assignment({ experiments }) {
  const [exp, setExp] = useState(experiments[0]?.id || "");
  const [unit, setUnit] = useState("daniel@example.com");
  const [res, setRes] = useState(null);
  const [chk, setChk] = useState(null);
  const [err, setErr] = useState(false);

  const lookup = async () => { try { setErr(false); setRes(await api.assign(unit, exp)); } catch { setErr(true); } };
  const balance = async () => { try { setErr(false); setChk(await api.assignCheck(exp, 5000)); } catch { setErr(true); } };

  return (
    <>
      <div className="page-head">
        <div><h1>Assignment</h1><p>Deterministic, <b>source-agnostic</b> bucketing — a salted hash of the
          unit id. The same function the live SDK's <code>get_variant()</code> would call; a unit always
          lands in the same arm.</p></div>
      </div>

      {err && <div className="card cardpad" style={{ marginBottom: 16, color: "var(--amber)" }}>
        ⚠ Assignment needs the live backend. Start it: <code>uvicorn chassis.app:app --port 8000</code>, then reload.</div>}

      <div className="sc-grid">
        <div className="card cardpad">
          <h3 className="section-t">Look up a unit</h3>
          <div className="form-grid">
            <Field label="Experiment">
              <select value={exp} onChange={(e) => setExp(e.target.value)}>
                {experiments.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
            </Field>
            <Field label="Unit id"><input value={unit} onChange={(e) => setUnit(e.target.value)} /></Field>
          </div>
          <button className="btn primary" style={{ marginTop: 12 }} onClick={lookup}>Assign →</button>
          {res && !res.error && (
            <div style={{ marginTop: 16 }}>
              <div className="note">unit lands in</div>
              <span className={"chip " + (res.variant === "control" ? "draft" : "running")}
                style={{ fontSize: 15, padding: "5px 14px", marginTop: 4 }}><span className="d" />{res.variant}</span>
              <div className="kv" style={{ marginTop: 12 }}><span className="k">salt</span><span className="v num">{res.salt}</span></div>
              <div className="note" style={{ marginTop: 4 }}>Deterministic — re-running with the same id always returns <b>{res.variant}</b>.</div>
            </div>
          )}
        </div>

        <div className="card cardpad">
          <h3 className="section-t">Balance check (SRM)</h3>
          <p className="note" style={{ marginTop: 0 }}>Hash 5,000 synthetic units and test the split against
            the target allocation — the sample-ratio-mismatch gate every experiment must pass.</p>
          <button className="btn" onClick={balance}>Run balance check</button>
          {chk && !chk.error && (
            <div style={{ marginTop: 16 }}>
              <div style={{ display: "flex", height: 26, borderRadius: 7, overflow: "hidden", border: "1px solid var(--line)" }}>
                {Object.entries(chk.counts).map(([k, v], i) => (
                  <div key={k} style={{ width: (100 * v / chk.n) + "%",
                    background: i === 0 ? "var(--slate-soft)" : "var(--blue-soft)",
                    color: i === 0 ? "var(--slate)" : "var(--blue-700)", fontSize: 11, fontWeight: 600,
                    display: "grid", placeItems: "center" }}>{k} {v.toLocaleString()}</div>
                ))}
              </div>
              <div className="kv" style={{ marginTop: 12 }}><span className="k">SRM χ² p-value</span>
                <span className="v num">{chk.srm_p}</span></div>
              <div className="diag-row"><span className="k" style={{ color: "var(--muted)" }}>verdict</span>
                <span className={"badge " + (chk.srm_ok ? "ok" : "no")}>{chk.srm_ok ? "✓ balanced" : "✗ mismatch"}</span></div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

function Field({ label, children }) {
  return <div className="field"><label>{label}</label>{children}</div>;
}
