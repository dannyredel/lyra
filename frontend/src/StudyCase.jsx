import React from "react";
import { STUDY_CASES, BRIEF_SECTIONS } from "./studyCases.js";

export default function StudyCase({ id, onBack, onViewLive, onCreate }) {
  const sc = STUDY_CASES.find((s) => s.id === id);
  if (!sc) return null;
  return (
    <>
      <button className="btn ghost" onClick={onBack} style={{ marginBottom: 14 }}>← Home</button>
      <div className="page-head">
        <div>
          <span className="case-tag" style={{ "--accent": sc.accent }}>{sc.industry}</span>
          <h1 style={{ marginTop: 10 }}>{sc.title}</h1>
          <p>{sc.question}</p>
        </div>
      </div>

      <div className="sc-grid">
        <div className="card cardpad brief">
          {BRIEF_SECTIONS.map(([k, label]) => (
            <div key={k} className="brief-sec">
              <h3 className="section-t" style={{ color: "var(--accent)" }}>{label}</h3>
              <p>{sc.brief[k]}</p>
            </div>
          ))}
        </div>

        <div style={{ display: "grid", gap: 16 }}>
          <div className="card cardpad">
            <h3 className="section-t">Methods showcased</h3>
            <div className="case-methods">{sc.methods.map((m) => <span key={m} className="tag">{m}</span>)}</div>
            <div className="result-box">{sc.result}</div>
          </div>
          <div className="card cardpad">
            <h3 className="section-t">Run it</h3>
            {sc.liveId && (
              <button className="btn primary" style={{ width: "100%", marginBottom: sc.template ? 8 : 0 }}
                onClick={() => onViewLive(sc.liveId)}>View live experiment →</button>
            )}
            {sc.template && (
              <button className="btn" style={{ width: "100%" }} onClick={() => onCreate(sc.template)}>
                Create this experiment</button>
            )}
            {sc.deepDive && (
              <div className="note" style={{ marginTop: 0 }}>This method runs as a <b>validated notebook</b>
                (CATE / incrementality) — the result above is graded against the authored ground truth.
                One-click chassis creation for this design is on the roadmap.</div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
