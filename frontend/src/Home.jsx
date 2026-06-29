import React from "react";
import { STUDY_CASES } from "./studyCases.js";
import { Logo } from "./ui.jsx";

const LINKS = {
  github: "https://github.com/dannyredel",
  linkedin: "https://www.linkedin.com/in/daniel-redel-14b052b6/",
  email: "mailto:dannyredel@gmail.com",
  portfolio: "https://dannyredel.github.io/",
  guide: "https://lyra-docs-chi.vercel.app/",
};

export default function Home({ experiments, onOpenCase, onNew }) {
  const certified = (experiments || []).filter((e) => e.truth?.certified).length;
  const withTruth = (experiments || []).filter((e) => e.truth).length;
  return (
    <>
      <div className="hero">
        <span className="hero-badge">✓ Lyra Verified</span>
        <h1>Experimentation you can <em>trust</em>.</h1>
        <p>Every experiment runs on a simulator with a <b>known ground truth</b> — so Lyra doesn't just
          report a result, it <b>certifies</b> the result is correct. Something no real platform can do.</p>
        <div className="hero-cta">
          <button className="btn primary" onClick={onNew}>+ New experiment</button>
          <a className="btn" href={LINKS.guide} target="_blank" rel="noreferrer"
            style={{ background: "rgba(255,255,255,.10)", color: "#fff", borderColor: "rgba(255,255,255,.22)" }}>
            Read the guide →</a>
          <span className="hero-stat">{(experiments || []).length} experiments · <b style={{ color: "#6EE7A8", fontWeight: 600 }}>{certified}/{withTruth} certified</b></span>
        </div>
      </div>

      <div className="how-strip">
        {[
          ["1", "Author the world", "Set the true effect in a data-generating process — you own the ground truth."],
          ["2", "Run the experiment", "Assignment · governed metrics · the right estimator for the design — the real chassis."],
          ["3", "Certify against truth", "A Monte-Carlo harness checks the estimate recovers the known effect at the right coverage."],
        ].map(([n, t, d]) => (
          <div key={n} className="how-step"><span className="hn">{n}</span><div><div className="ht">{t}</div><div className="hp">{d}</div></div></div>
        ))}
      </div>

      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", margin: "30px 0 14px" }}>
        <h3 className="section-t" style={{ margin: 0 }}>Study cases — Lyra across industries</h3>
        <span className="note" style={{ marginTop: 0 }}>click a case to read the brief</span>
      </div>
      <div className="case-grid">
        {STUDY_CASES.map((sc) => (
          <button key={sc.id} className="case-card" style={{ "--accent": sc.accent }} onClick={() => onOpenCase(sc.id)}>
            <span className="case-tag" style={{ "--accent": sc.accent }}>{sc.industry}</span>
            <div className="case-title">{sc.title}</div>
            <div className="case-q">{sc.question}</div>
            <div className="case-methods">{sc.methods.map((m) => <span key={m} className="tag">{m}</span>)}</div>
            <div className="case-foot">{sc.deepDive ? "Deep-dive analysis" : "Live demo"} · Explore →</div>
          </button>
        ))}
      </div>

      <footer className="site-foot">
        <div className="foot-cols">
          <div>
            <div className="foot-brand"><Logo size={24} /> Lyra</div>
            <p>A thin-but-real experimentation platform with a deep inference engine. Because every
              experiment runs on a simulator with a <b>known ground truth</b>, every estimator is
              <b> validated against that truth</b> via a Monte-Carlo recovery harness — a guarantee no
              live platform can offer.</p>
          </div>
          <div>
            <div className="foot-h">Under the hood</div>
            <ul>
              <li>12-notebook inference curriculum — DR/DML · CUPED · cluster-robust SEs · switchback ·
                always-valid sequences · CATE · policy/OPE · observational · incrementality</li>
              <li>FastAPI chassis — assignment · governed metrics · lifecycle · ship-rule decisions</li>
              <li>Every method certified vs ground truth; incrementality validated on the real Criteo
                Uplift RCT (13.9M rows)</li>
            </ul>
            <div className="foot-links" style={{ marginTop: 12 }}>
              <a href={LINKS.guide} target="_blank" rel="noreferrer">📖 Read the user guide →</a>
            </div>
          </div>
          <div>
            <div className="foot-h">Built by</div>
            <p>Daniel Redel — data science, causal inference &amp; experimentation.</p>
            <div className="foot-links">
              <a href={LINKS.portfolio} target="_blank" rel="noreferrer">Portfolio ↗</a>
              <a href={LINKS.github} target="_blank" rel="noreferrer">GitHub ↗</a>
              <a href={LINKS.linkedin} target="_blank" rel="noreferrer">LinkedIn ↗</a>
              <a href={LINKS.email}>Email</a>
            </div>
          </div>
        </div>
        <div className="foot-base">
          <span>Lyra — a portfolio demo. Read-only snapshot; the full create→run→decide loop runs on the local backend.</span>
          <span>Built with Python · PyMC/econml · FastAPI · React</span>
        </div>
      </footer>
    </>
  );
}
