import React, { useState, useMemo } from "react";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar, AreaChart, Area, ScatterChart, Scatter,
  ComposedChart, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, ReferenceLine,
} from "recharts";
import { requiredN, powerAtN, mdeAtN } from "./power.js";
import { abPreview, switchbackPreview, clusterPreview, marketplacePreview } from "./dgpViz.js";
import { Info } from "./ui.jsx";
import SampleSize from "./SampleSize.jsx";
import { METRIC_CATALOG } from "./Metrics.jsx";

// The dependent-variable choices, sourced from the governed Metric library (not free-text).
const DV_METRICS = METRIC_CATALOG.filter((m) => ["proportion", "mean", "ratio"].includes(m.key));
const KEY_TO_TYPE = { proportion: "proportion", mean: "continuous", ratio: "ratio" };

const DESIGNS = {
  ab: { label: "A/B test", blurb: "Two arms with a planted effect — the workhorse.", estimator: "Two-proportion z / OLS" },
  cluster: { label: "Cluster-randomized", blurb: "Whole clusters (geos, markets) assigned to an arm.", estimator: "ClusterOLS (cluster-robust)" },
  switchback: { label: "Switchback", blurb: "One market, treatment toggled on/off over time.", estimator: "CUPED + cluster-robust" },
  interference: { label: "Marketplace (interference)", blurb: "Shared-budget cannibalization — a naive A/B is biased.", estimator: "DiffInMeans / ClusterOLS" },
};
const STEPS = ["Design", "Sample size", "Simulate", "Review"];

const DEFAULTS = {
  name: "", hypothesis: "", owner: "Daniel R.", design: "ab", metricKey: "proportion", metricType: "proportion",
  mu: 0.2, sigma2: 1.0, trueEffect: 0.02, relMde: 5, qc: 50, alpha: 0.05, power: 0.8, twoSided: true,
  S: 1, C: 1, Gnim: 0, GnoNim: 0, rho: 0, days: 21, nPerDay: 1500,
  G: 60, n_g: 25, J: 50, H: 20, n_bar: 18, boost: 0.6, interferenceDesign: "cluster",
};

function seedForm(t) {
  if (!t) return { ...DEFAULTS };
  return {
    ...DEFAULTS, design: t.design ?? DEFAULTS.design, metricType: t.metric_type ?? DEFAULTS.metricType,
    metricKey: t.metric_key ?? (t.metric_type === "continuous" ? "mean" : t.metric_type === "ratio" ? "ratio" : DEFAULTS.metricKey),
    mu: t.mu ?? DEFAULTS.mu, sigma2: t.sigma2 ?? DEFAULTS.sigma2, trueEffect: t.true_effect ?? DEFAULTS.trueEffect,
    relMde: t.rel_mde != null ? t.rel_mde * 100 : DEFAULTS.relMde, qc: t.q_control != null ? t.q_control * 100 : DEFAULTS.qc,
    G: t.G ?? DEFAULTS.G, n_g: t.n_g ?? DEFAULTS.n_g, J: t.J ?? DEFAULTS.J, H: t.H ?? DEFAULTS.H,
    n_bar: t.n_bar ?? DEFAULTS.n_bar, boost: t.boost ?? DEFAULTS.boost, interferenceDesign: t.interference_design ?? DEFAULTS.interferenceDesign,
  };
}

function Field({ label, hint, info, children }) {
  return (
    <div className={"field" + (label === "" ? " full" : "")}>
      {label !== "" && <label>{label}{info && <Info>{info}</Info>}</label>}
      {children}{hint && <span className="hint">{hint}</span>}
    </div>
  );
}

export default function NewExperiment({ onBack, onCreate, mode, template }) {
  const [f, setF] = useState(() => seedForm(template));
  const [step, setStep] = useState(1);
  const num = (k) => (e) => setF({ ...f, [k]: e.target.value === "" ? "" : parseFloat(e.target.value) });
  const txt = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const isAB = f.design === "ab", isInterf = f.design === "interference";

  const p = {
    binary: f.metricType === "proportion", mu: +f.mu || 0, sigma2: +f.sigma2 || 0, relMde: (+f.relMde || 0) / 100,
    qc: Math.min(0.95, Math.max(0.05, (+f.qc || 50) / 100)), alpha: +f.alpha || 0.05, power: +f.power || 0.8,
    twoSided: f.twoSided !== false, S: +f.S || 1, C: +f.C || 1, Gnim: +f.Gnim || 0, rho: +f.rho || 0,
  };
  const availableN = Math.round((+f.days || 0) * (+f.nPerDay || 0));
  const req = useMemo(() => (isAB ? requiredN(p) : null), [isAB, JSON.stringify(p)]);
  const powered = isAB && availableN >= req.nTotal && req.nTotal > 0;
  const curve = useMemo(() => {
    if (!isAB) return [];
    const hi = Math.max(req.nTotal * 1.6, availableN * 1.2, 1000);
    return Array.from({ length: 24 }, (_, i) => { const N = Math.round(hi * (i + 1) / 24); return { N, power: +(powerAtN(N, p) * 100).toFixed(1) }; });
  }, [isAB, JSON.stringify(p), req?.nTotal, availableN]);

  const dvMetric = DV_METRICS.find((m) => m.key === f.metricKey) || DV_METRICS[0];
  const create = () => {
    const spec = {
      name: f.name || "Untitled experiment", hypothesis: f.hypothesis, owner: f.owner, design: f.design,
      metric_type: f.metricType, metric_key: f.metricKey, mu: +f.mu || 0, sigma2: p.sigma2, true_effect: +f.trueEffect || 0,
      rel_mde: p.relMde, q_control: p.qc, alpha: p.alpha, power: p.power, two_sided: p.twoSided,
      n_success: p.S, n_comparisons: p.C, n_guardrail_nim: p.Gnim, rho: p.rho,
      days: +f.days || 0, n_per_day: +f.nPerDay || 0, G: +f.G || 0, n_g: +f.n_g || 0, J: +f.J || 0, H: +f.H || 0,
      n_bar: +f.n_bar || 0, boost: +f.boost || 0, interference_design: f.interferenceDesign,
    };
    spec.__row = {
      id: "exp_new_" + Date.now(), name: spec.name, hypothesis: f.hypothesis, owner: f.owner, state: "DRAFT",
      design: f.design === "ab" ? "user" : f.design, guardrails: [],
      metric: { name: dvMetric.name, type: f.metricType, key: f.metricKey, class: "primary", direction: "up" },
      power: { required_n: isAB ? req.nTotal : 0, current_n: availableN, powered, pct_powered: isAB && req.nTotal ? +Math.min(100, 100 * availableN / req.nTotal).toFixed(1) : 100 },
    };
    onCreate(spec);
  };

  return (
    <>
      <button className="btn ghost" onClick={onBack} style={{ marginBottom: 14 }}>← Experiments</button>
      <div className="page-head">
        <div><h1>New experiment</h1><p>Design it, choose metrics, then <b>author the world</b> and watch the data react.</p></div>
      </div>

      <div className="steps">
        {STEPS.map((s, i) => (
          <div key={s} className={"stepi" + (step === i + 1 ? " active" : step > i + 1 ? " done" : "")}>
            <span className="num">{step > i + 1 ? "✓" : i + 1}</span><span className="slabel">{s}</span>
          </div>
        ))}
      </div>

      {step === 1 && (
        <div className="card cardpad">
          <h3 className="section-t">Design & hypothesis</h3>
          <div className="form-grid">
            <Field label="Design" info={<>Fixes the DGP world + estimator. <b>A/B</b> simple two-arm; <b>cluster</b> geo/market; <b>switchback</b> temporal; <b>marketplace</b> shared-budget cannibalization.</>}>
              <select value={f.design} onChange={txt("design")}>{Object.entries(DESIGNS).map(([k, d]) => <option key={k} value={k}>{d.label}</option>)}</select>
            </Field>
            <Field label="Primary metric (dependent variable)" info={<>The outcome you measure — picked from the governed <b>Metric library</b>, so its definition and estimator are fixed platform-wide (no ad-hoc "conversion rate").</>}>
              <select value={f.metricKey} onChange={(e) => { const k = e.target.value; setF({ ...f, metricKey: k, metricType: KEY_TO_TYPE[k] }); }}>
                {DV_METRICS.map((m) => <option key={m.key} value={m.key}>{m.name} · {m.type}</option>)}
              </select>
            </Field>
            <Field label="Owner"><input value={f.owner} onChange={txt("owner")} /></Field>
            <Field label=""><input placeholder="Name (e.g. Reward sizing — Game C)" value={f.name} onChange={txt("name")} /></Field>
            <Field label=""><input placeholder="Hypothesis (what do you expect, and why?)" value={f.hypothesis} onChange={txt("hypothesis")} /></Field>
          </div>
          <div className="note" style={{ marginTop: 12 }}>{DESIGNS[f.design].blurb} Estimator: <b>{DESIGNS[f.design].estimator}</b>.</div>
        </div>
      )}

      {step === 2 && <SampleSize f={f} setF={setF} />}

      {step === 3 && (
        <div className="sc-grid">
          <div className="card cardpad">
            <h3 className="section-t">Author the world (the DGP)</h3>
            <p className="note" style={{ marginTop: 0 }}>This is a simulator — you set the <b>true effect</b>. On launch, Lyra certifies the estimate recovers exactly this.</p>
            <div className="form-grid">
              {isAB && <>
                <Field label="Baseline μ (from history)" hint={p.binary ? "control rate today" : "control mean today"} info={<>A planning estimate of the control average, from history — not the result.</>}><input type="number" step="0.01" value={f.mu} onChange={num("mu")} /></Field>
                <Field label={"True effect (" + (p.binary ? "risk diff" : "mean shift") + ")"} info={<>The real effect you plant; Lyra certifies the estimate recovers it.</>}><input type="number" step="0.005" value={f.trueEffect} onChange={num("trueEffect")} /></Field>
                {!p.binary && <Field label="Variance σ²"><input type="number" step="0.01" value={f.sigma2} onChange={num("sigma2")} /></Field>}
              </>}
              {f.design === "cluster" && <>
                <Field label="True cluster effect"><input type="number" step="0.05" value={f.trueEffect} onChange={num("trueEffect")} /></Field>
                <Field label="Clusters (G)"><input type="number" step="5" value={f.G} onChange={num("G")} /></Field>
                <Field label="Units / cluster"><input type="number" step="5" value={f.n_g} onChange={num("n_g")} /></Field>
              </>}
              {f.design === "switchback" && <>
                <Field label="Baseline μ (GMV/period)"><input type="number" step="50" value={f.mu} onChange={num("mu")} /></Field>
                <Field label="True effect (τ)"><input type="number" step="5" value={f.trueEffect} onChange={num("trueEffect")} /></Field>
                <Field label="Markets (J)"><input type="number" step="5" value={f.J} onChange={num("J")} /></Field>
                <Field label="Periods (H)"><input type="number" step="2" value={f.H} onChange={num("H")} /></Field>
              </>}
              {isInterf && <>
                <Field label="Randomization" info={<><b>naive user-level</b> A/B is biased under cannibalization; <b>cluster-safe</b> recovers the global effect.</>}>
                  <select value={f.interferenceDesign} onChange={txt("interferenceDesign")}><option value="cluster">cluster-safe</option><option value="user">naive user-level</option></select></Field>
                <Field label="Cannibalization (boost)"><input type="number" step="0.1" value={f.boost} onChange={num("boost")} /></Field>
                <Field label="Markets (G)"><input type="number" step="5" value={f.G} onChange={num("G")} /></Field>
              </>}
              <Field label="Days"><input type="number" step="1" value={f.days} onChange={num("days")} /></Field>
              {isAB && <Field label="Users / day"><input type="number" step="100" value={f.nPerDay} onChange={num("nPerDay")} /></Field>}
            </div>
          </div>
          <DgpPlot design={f.design} f={f} p={p} />
        </div>
      )}

      {step === 4 && (
        <div className="sc-grid">
          <div className="card cardpad">
            <h3 className="section-t">Review</h3>
            <div className="kv"><span className="k">Design</span><span className="v">{DESIGNS[f.design].label}</span></div>
            <div className="kv"><span className="k">Metric (dependent variable)</span><span className="v">{dvMetric.name} · {f.metricType}</span></div>
            <div className="kv"><span className="k">True effect (planted)</span><span className="v num">{isInterf ? "computed" : f.trueEffect}</span></div>
            <div className="kv"><span className="k">Allocation</span><span className="v">control {f.qc}% · treatment {100 - f.qc}%</span></div>
            <div className="kv"><span className="k">Run</span><span className="v">{f.days} days{isAB ? ` × ${(+f.nPerDay || 0).toLocaleString()}/day` : ""}</span></div>
          </div>
          {isAB ? <AbReadout f={f} p={p} req={req} availableN={availableN} powered={powered} curve={curve} /> : <DesignSummary f={f} isInterf={isInterf} />}
        </div>
      )}

      <div className="wizard-nav">
        <button className="btn" onClick={() => setStep(step - 1)} disabled={step === 1}>← Back</button>
        {step < 4
          ? <button className="btn primary" onClick={() => setStep(step + 1)}>Next →</button>
          : <button className="btn primary" onClick={create}>Create draft</button>}
      </div>
    </>
  );
}

function DgpPlot({ design, f, p }) {
  const wrap = (note, chart) => (
    <div style={{ display: "grid", gap: 16 }}>
      <div className="card cardpad">
        <h3 className="section-t">Preview — how the data looks</h3>
        <ResponsiveContainer width="100%" height={250}>{chart}</ResponsiveContainer>
        <div className="note">{note} <i>Illustrative — the real, validated numbers come from running it.</i></div>
      </div>
    </div>
  );
  const axis = { tickLine: false, axisLine: { stroke: "#E7ECF4" }, tick: { fill: "#6B7A90", fontSize: 11 } };
  const tip = { contentStyle: { borderRadius: 10, border: "1px solid #E7ECF4", fontSize: 12 } };

  if (design === "ab") {
    const pv = abPreview({ binary: p.binary, mu: p.mu, effect: +f.trueEffect || 0, sigma: Math.sqrt(p.sigma2) });
    const eff = +f.trueEffect || 0;
    return wrap(p.binary
      ? "Conversion rate, control (grey) vs treatment (blue) — the gap is the risk difference you planted."
      : "Outcome density, control (grey) vs treatment (blue) — the dashed lines mark each group's mean; the gap is the effect.",
      pv.kind === "bars" ? (
        <BarChart data={pv.data} margin={{ top: 8, right: 10, bottom: 4, left: -12 }}>
          <CartesianGrid stroke="#EEF2F7" vertical={false} /><XAxis dataKey="outcome" {...axis} /><YAxis {...axis} width={36} tickFormatter={(v) => Math.round(v * 100) + "%"} /><Tooltip {...tip} formatter={(v) => (v * 100).toFixed(1) + "%"} />
          <Bar dataKey="control" fill="#94A3B8" radius={[3, 3, 0, 0]} /><Bar dataKey="treatment" fill="#1E6091" radius={[3, 3, 0, 0]} />
        </BarChart>
      ) : (
        <AreaChart data={pv.data} margin={{ top: 8, right: 10, bottom: 4, left: -12 }}>
          <CartesianGrid stroke="#EEF2F7" vertical={false} /><XAxis dataKey="x" {...axis} /><YAxis {...axis} width={28} /><Tooltip {...tip} />
          <Area dataKey="control" stroke="#94A3B8" strokeWidth={1.6} fill="#94A3B8" fillOpacity={0.18} isAnimationActive={false} />
          <Area dataKey="treatment" stroke="#1E6091" strokeWidth={1.8} fill="#1E6091" fillOpacity={0.18} isAnimationActive={false} />
          <ReferenceLine x={+p.mu.toFixed(2)} stroke="#94A3B8" strokeDasharray="3 3" strokeOpacity={0.85} />
          <ReferenceLine x={+(p.mu + eff).toFixed(2)} stroke="#1E6091" strokeDasharray="3 3"
            label={{ value: "+effect", fill: "#1E6091", fontSize: 10, position: "top" }} />
        </AreaChart>
      ));
  }
  if (design === "switchback") {
    const d = switchbackPreview({ mu: +f.mu || 0, tau: +f.trueEffect || 0, H: +f.H || 20 });
    return wrap("Treatment toggles on/off each period — filled dot = on, hollow = off — and the outcome tracks it.",
      <LineChart data={d} margin={{ top: 8, right: 10, bottom: 4, left: -4 }}>
        <CartesianGrid stroke="#EEF2F7" vertical={false} /><XAxis dataKey="period" {...axis} /><YAxis domain={["auto", "auto"]} {...axis} width={46} /><Tooltip {...tip} />
        <Line dataKey="y" stroke="#1E6091" strokeWidth={2} dot={(pr) => <circle key={pr.key} cx={pr.cx} cy={pr.cy} r={4} fill={pr.payload.treat ? "#1E6091" : "#fff"} stroke="#1E6091" strokeWidth={1.6} />} />
      </LineChart>);
  }
  if (design === "cluster") {
    const d = clusterPreview({ G: +f.G || 40, effect: +f.trueEffect || 0 });
    return wrap("Each dot is a cluster's mean — control (grey) vs treated (blue). The spread between clusters is what inflates the CI.",
      <ScatterChart margin={{ top: 8, right: 10, bottom: 4, left: -4 }}>
        <CartesianGrid stroke="#EEF2F7" /><XAxis dataKey="g" name="cluster" {...axis} /><YAxis dataKey="mean" name="mean" {...axis} width={42} /><ZAxis range={[40, 40]} /><Tooltip {...tip} />
        <Scatter data={d.filter((x) => !x.treated)} fill="#94A3B8" /><Scatter data={d.filter((x) => x.treated)} fill="#1E6091" />
      </ScatterChart>);
  }
  const d = marketplacePreview({ boost: +f.boost || 0 });
  return wrap("The naive A/B uplift (red) decays as you treat more — and sits far above the true global effect (green). That gap is cannibalization.",
    <LineChart data={d} margin={{ top: 8, right: 10, bottom: 4, left: -8 }}>
      <CartesianGrid stroke="#EEF2F7" vertical={false} /><XAxis dataKey="phi" unit="%" {...axis} /><YAxis {...axis} width={40} /><Tooltip {...tip} />
      <Line dataKey="naive" stroke="#DC2626" strokeWidth={2.2} dot={false} name="naive A/B" />
      <Line dataKey="truth" stroke="#16A34A" strokeWidth={2} strokeDasharray="5 4" dot={false} name="true global" />
    </LineChart>);
}

function AbReadout({ f, p, req, availableN, powered, curve }) {
  const mdeNow = mdeAtN(availableN, p);
  return (
    <div style={{ display: "grid", gap: 16 }}>
      <div className="card cardpad">
        <h3 className="section-t">Required sample size</h3>
        <div className="bignum">{req.nTotal.toLocaleString()}</div>
        <div className="note">total ({req.nPerArm.toLocaleString()}/arm) to detect a {f.relMde}% lift at 80% power.</div>
        <div className={"gate " + (powered ? "ok" : "no")}>
          <div className="ic">{powered ? "✓" : "⚠"}</div>
          <div><div className="t">{powered ? "Adequately powered" : "Underpowered"}</div>
            <div className="s" style={{ fontSize: 12, color: "var(--ink-2)" }}>{availableN.toLocaleString()} available = {req.nTotal ? Math.round(100 * availableN / req.nTotal) : 0}% of required.{!powered && ` Detectable: ≥ ${(mdeNow.relMde * 100).toFixed(1)}%.`}</div></div>
        </div>
      </div>
      <div className="card cardpad">
        <h3 className="section-t">Power vs sample size</h3>
        <ResponsiveContainer width="100%" height={190}>
          <LineChart data={curve} margin={{ top: 8, right: 14, bottom: 4, left: -8 }}>
            <CartesianGrid stroke="#EEF2F7" vertical={false} />
            <XAxis dataKey="N" tickFormatter={(n) => (n >= 1000 ? (n / 1000).toFixed(0) + "k" : n)} tickLine={false} axisLine={{ stroke: "#E7ECF4" }} tick={{ fill: "#6B7A90", fontSize: 11 }} />
            <YAxis domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fill: "#6B7A90", fontSize: 11 }} width={32} />
            <Tooltip formatter={(v) => v + "% power"} contentStyle={{ borderRadius: 10, border: "1px solid #E7ECF4", fontSize: 12 }} />
            <ReferenceLine y={80} stroke="#94A3B8" strokeDasharray="4 4" /><ReferenceLine x={req.nTotal} stroke="#16A34A" strokeDasharray="5 4" label={{ value: "required", fill: "#16A34A", fontSize: 10, position: "top" }} />
            <ReferenceLine x={availableN} stroke="#1E6091" label={{ value: "available", fill: "#1E6091", fontSize: 10, position: "top" }} />
            <Line dataKey="power" stroke="#1E6091" strokeWidth={2.4} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function DesignSummary({ f, isInterf }) {
  const d = DESIGNS[f.design];
  const naive = isInterf && f.interferenceDesign === "user";
  const struct = f.design === "cluster" ? `${f.G} clusters × ${f.n_g} units`
    : f.design === "switchback" ? `${f.J} markets × ${f.H} periods × ${f.n_bar} units` : `${f.G} markets`;
  return (
    <div style={{ display: "grid", gap: 16 }}>
      <div className="card cardpad">
        <h3 className="section-t">{d.label}</h3>
        <div className="kv"><span className="k">Structure</span><span className="v">{struct}</span></div>
        <div className="kv"><span className="k">Estimator</span><span className="v">{naive ? "DiffInMeans (naive)" : d.estimator}</span></div>
      </div>
      <div className="card cardpad">
        <div className={"gate " + (naive ? "no" : "ok")}>
          <div className="ic">{naive ? "⚠" : "✓"}</div>
          <div><div className="t">{naive ? "Expected: uncertified" : "Validated by simulation"}</div>
            <div className="s" style={{ fontSize: 12, color: "var(--ink-2)" }}>{naive ? "A naive A/B in a shared market is biased — the certified badge will flag it on launch." : "On launch, the harness certifies the estimator covers the planted truth — watch the certified badge."}</div></div>
        </div>
      </div>
    </div>
  );
}
