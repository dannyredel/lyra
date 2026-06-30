import React, { useState } from "react";
import katex from "katex";
import { AreaChart, Area, XAxis, YAxis, ReferenceLine, ResponsiveContainer } from "recharts";
import { requiredN } from "./power.js";
import { Info } from "./ui.jsx";

function Tex({ children, block }) {
  return <span dangerouslySetInnerHTML={{ __html: katex.renderToString(children, { throwOnError: false, displayMode: !!block }) }} />;
}

const GREY = "#94A3B8", BLUE = "#1E6091";
const _grid = (lo, hi, n = 90) => Array.from({ length: n }, (_, i) => lo + ((hi - lo) * i) / (n - 1));
const _npdf = (x, m, s) => Math.exp(-0.5 * ((x - m) / s) ** 2) / (s * Math.sqrt(2 * Math.PI));

// Two reactive views of the same design: the per-unit population (control vs treatment, heavy overlap)
// and the sampling distribution of each group MEAN at the required N (now separated — that's what N buys).
function DistPanel({ mu, delta, sigma2, rho, nC, nT, binary }) {
  const sd = Math.sqrt(Math.max(sigma2, 1e-12));
  const seC = Math.sqrt((sigma2 * (1 - rho)) / Math.max(nC, 1));
  const seT = Math.sqrt((sigma2 * (1 - rho)) / Math.max(nT, 1));
  const mkt = mu + delta, w = Math.max(seC, seT, 1e-9);
  const pop = _grid(Math.min(mu, mkt) - 3.6 * sd, Math.max(mu, mkt) + 3.6 * sd)
    .map((x) => ({ x, c: _npdf(x, mu, sd), t: _npdf(x, mkt, sd) }));
  const mean = _grid(Math.min(mu, mkt) - 4.2 * w, Math.max(mu, mkt) + 4.2 * w)
    .map((x) => ({ x, c: _npdf(x, mu, seC), t: _npdf(x, mkt, seT) }));
  const fmt = (v) => (binary ? (v * 100).toFixed(0) + "%" : (+v).toFixed(2));
  const Chart = ({ data, refs }) => (
    <ResponsiveContainer width="100%" height={150}>
      <AreaChart data={data} margin={{ top: 6, right: 10, bottom: 0, left: 6 }}>
        <XAxis dataKey="x" type="number" domain={["dataMin", "dataMax"]} tickFormatter={fmt}
          tick={{ fill: "#6B7A90", fontSize: 10 }} tickLine={false} axisLine={{ stroke: "#E7ECF4" }} />
        <YAxis hide domain={[0, "dataMax"]} />
        <Area dataKey="c" stroke={GREY} strokeWidth={1.6} fill={GREY} fillOpacity={0.22} isAnimationActive={false} />
        <Area dataKey="t" stroke={BLUE} strokeWidth={1.8} fill={BLUE} fillOpacity={0.20} isAnimationActive={false} />
        {refs.map((x, i) => <ReferenceLine key={i} x={x} stroke={i ? BLUE : GREY} strokeDasharray="4 3" strokeOpacity={0.7} />)}
      </AreaChart>
    </ResponsiveContainer>
  );
  return (
    <div className="card cardpad" style={{ marginTop: 16 }}>
      <div className="card-h-row" style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h3 className="section-t" style={{ margin: 0 }}>What that sample buys you</h3>
        <div className="chart-legend" style={{ display: "flex", gap: 14, fontSize: 11, color: "var(--muted)" }}>
          <span><i style={{ display: "inline-block", width: 10, height: 10, borderRadius: 3, background: GREY, marginRight: 5 }} />control</span>
          <span><i style={{ display: "inline-block", width: 10, height: 10, borderRadius: 3, background: BLUE, marginRight: 5 }} />treatment (+δ)</span>
        </div>
      </div>
      <div className="grid" style={{ gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 10 }}>
        <div>
          <div className="note" style={{ marginBottom: 2 }}><b>Individual outcomes</b> — the population</div>
          <Chart data={pop} refs={[mu, mkt]} />
          <div className="note" style={{ marginTop: 2 }}>The effect shifts the mean by δ, but individuals overlap heavily — one user tells you almost nothing.</div>
        </div>
        <div>
          <div className="note" style={{ marginBottom: 2 }}><b>Group means at N</b> — the sampling distribution</div>
          <Chart data={mean} refs={[mu, mkt]} />
          <div className="note" style={{ marginTop: 2 }}>Averaging the required N units sharpens each group mean until the two separate — enough to detect δ at your power.</div>
        </div>
      </div>
    </div>
  );
}

function Slider({ label, info, value, min, max, step, onChange, fmt }) {
  return (
    <div className="ssc-field">
      <label>{label}{info && <Info>{info}</Info>}</label>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(parseFloat(e.target.value))} />
      <div className="ssc-val">{fmt ? fmt(value) : value}</div>
    </div>
  );
}
function NumIn({ label, info, value, step, onChange, disabled }) {
  return (
    <div className="ssc-field">
      <label>{label}{info && <Info>{info}</Info>}</label>
      <input type="number" step={step} value={value} disabled={disabled}
        onChange={(e) => onChange(e.target.value === "" ? "" : parseFloat(e.target.value))} />
    </div>
  );
}

export default function SampleSize({ f, setF }) {
  const [showF, setShowF] = useState(false);
  const set = (k, v) => setF({ ...f, [k]: v });
  const binary = f.metricType === "proportion";
  const twoSided = f.twoSided !== false;
  const sigma2 = binary ? +f.mu * (1 - +f.mu) : +f.sigma2;
  const p = {
    binary, mu: +f.mu || 0, sigma2, relMde: (+f.relMde || 0) / 100, twoSided,
    qc: Math.min(0.95, Math.max(0.05, (+f.qc || 50) / 100)), alpha: +f.alpha || 0.05, power: +f.power || 0.8,
    S: +f.S || 1, C: +f.C || 1, Gnim: +f.Gnim || 0, rho: +f.rho || 0,
  };
  const r = requiredN(p);
  const aAdj = p.alpha / (p.C * Math.max(p.S, 1));
  const pAdj = 1 - (1 - p.power) / (p.Gnim + Math.max(Math.min(p.S, 1), 1));
  const z1 = (q) => { /* one-sided z = Φ⁻¹(q) */ const a = [-39.69683, 220.9460, -275.9285, 138.3577, -30.66479, 2.506628], b = [-54.47609, 161.5858, -155.6989, 66.80131, -13.28068], c = [-0.007784894, -0.3223964, -2.400758, -2.549732, 4.374664, 2.938164], d = [0.007784695, 0.3224671, 2.445134, 3.754408]; const pl = 0.02425; let t; if (q < pl) { t = Math.sqrt(-2 * Math.log(q)); return (((((c[0] * t + c[1]) * t + c[2]) * t + c[3]) * t + c[4]) * t + c[5]) / ((((d[0] * t + d[1]) * t + d[2]) * t + d[3]) * t + 1); } if (q <= 1 - pl) { t = q - 0.5; const r2 = t * t; return (((((a[0] * r2 + a[1]) * r2 + a[2]) * r2 + a[3]) * r2 + a[4]) * r2 + a[5]) * t / (((((b[0] * r2 + b[1]) * r2 + b[2]) * r2 + b[3]) * r2 + b[4]) * r2 + 1); } t = Math.sqrt(-2 * Math.log(1 - q)); return -(((((c[0] * t + c[1]) * t + c[2]) * t + c[3]) * t + c[4]) * t + c[5]) / ((((d[0] * t + d[1]) * t + d[2]) * t + d[3]) * t + 1); };
  const zA = z1(1 - (twoSided ? aAdj / 2 : aAdj)), zP = z1(pAdj), alloc = 1 / p.qc + 1 / (1 - p.qc), delta = p.mu * p.relMde;
  const zSub = twoSided ? "1-\\alpha_{adj}/2" : "1-\\alpha_{adj}";

  return (
    <>
      <div className="ssc-grid">
        <div className="card cardpad">
          <h3 className="section-t">Metric parameters</h3>
          <NumIn label="Metric mean (μ)" info={<>The control-group average today (from history).</>} value={f.mu} step="0.01" onChange={(v) => set("mu", v)} />
          <Slider label="Relative MDE / NIM (%)" info={<>Smallest lift to detect, as % of μ. Halving it ~quadruples N.</>} value={f.relMde} min={0.5} max={20} step={0.5} onChange={(v) => set("relMde", v)} />
          <NumIn label="Metric variance (σ²)" info={<>Outcome variance. For a binary metric it's μ(1−μ), auto.</>} value={binary ? sigma2.toFixed(3) : f.sigma2} step="0.01" disabled={binary} onChange={(v) => set("sigma2", v)} />
          <label className="ssc-check"><input type="checkbox" checked={binary} onChange={(e) => set("metricType", e.target.checked ? "proportion" : "continuous")} /> This is a binary metric</label>
          <Slider label="Variance reduction factor (ρ)" info={<>CUPED: a pre-period covariate cuts variance by (1−ρ).</>} value={f.rho} min={0} max={0.9} step={0.05} onChange={(v) => set("rho", v)} />
        </div>

        <div className="card cardpad">
          <h3 className="section-t">Statistical parameters</h3>
          <Slider label="Alpha (false-positive rate)" info={<>The significance level α. Split across success metrics.</>} value={f.alpha} min={0.01} max={0.2} step={0.01} onChange={(v) => set("alpha", v)} />
          <Slider label="Power (true-positive rate)" info={<>The chance of detecting a real effect of the MDE size.</>} value={f.power} min={0.5} max={0.99} step={0.01} onChange={(v) => set("power", v)} />
          <div className="ssc-field">
            <label>Test type<Info>Two-sided (z_{"{"}1−α/2{"}"}) is correct for the two-sided CIs we analyse with. One-sided matches Spotify's calculator exactly — but under-powers a two-sided test.</Info></label>
            <div className="tabs" style={{ marginBottom: 0, marginTop: 2 }}>
              <button className={twoSided ? "active" : ""} onClick={() => set("twoSided", true)}>Two-sided</button>
              <button className={!twoSided ? "active" : ""} onClick={() => set("twoSided", false)}>One-sided</button>
            </div>
          </div>
        </div>

        <div className="card cardpad">
          <h3 className="section-t">Experiment design</h3>
          <Slider label="Number of group comparisons" info={<>Treatment arms vs control. Splits α.</>} value={f.C} min={1} max={6} step={1} onChange={(v) => set("C", v)} />
          <Slider label="Number of success metrics" info={<>Primary win metrics. α is split across them.</>} value={f.S} min={1} max={6} step={1} onChange={(v) => set("S", v)} />
          <Slider label="Guardrail metrics with NIMs" info={<>Must-not-harm metrics with a non-inferiority margin — raise required power.</>} value={f.Gnim} min={0} max={6} step={1} onChange={(v) => set("Gnim", v)} />
          <Slider label="Guardrails without NIMs (no effect on N)" info={<>Monitored but not size-driving.</>} value={f.GnoNim} min={0} max={6} step={1} onChange={(v) => set("GnoNim", v)} />
        </div>

        <div className="card cardpad">
          <h3 className="section-t">Sample allocation</h3>
          <Slider label="Proportion in control (%)" value={f.qc} min={5} max={95} step={5} onChange={(v) => set("qc", v)} />
          <Slider label="Proportion in treatment (%)" value={100 - f.qc} min={5} max={95} step={5} onChange={(v) => set("qc", 100 - v)} />
        </div>
      </div>

      <div className="card cardpad" style={{ marginTop: 16 }}>
        <div className="bignum" style={{ fontSize: 24 }}>Required sample size: {r.nTotal.toLocaleString()}</div>
        <div className="note">The relative MDE corresponds to an absolute value of {r.absMde.toFixed(4)}. With {f.qc}% in
          control, the required control group is {r.nPerArm.toLocaleString()} and treatment is {(r.nTotal - r.nPerArm).toLocaleString()}.</div>
        <label className="ssc-check" style={{ marginTop: 12 }}><input type="checkbox" checked={showF} onChange={(e) => setShowF(e.target.checked)} /> Show detailed formulas</label>
      </div>

      <DistPanel mu={p.mu} delta={delta} sigma2={sigma2} rho={p.rho}
        nC={r.nPerArm} nT={r.nTotal - r.nPerArm} binary={binary} />

      {showF && (
        <div className="card cardpad formulas" style={{ marginTop: 16 }}>
          <h3 className="section-t">Detailed formulas</h3>
          <div className="tex-block">
            <Tex block>{`N = \\left(\\tfrac{1}{q_c}+\\tfrac{1}{q_t}\\right)\\frac{(z_{${zSub}}+z_{power_{adj}})^2\\,\\sigma^2(1-\\rho)}{(\\mu\\cdot \\text{relMDE})^2} = ${alloc.toFixed(2)}\\cdot\\frac{(${zA.toFixed(3)}+${zP.toFixed(3)})^2\\cdot ${sigma2.toFixed(2)}\\cdot(1-${p.rho})}{(${p.mu}\\cdot ${p.relMde})^2} = ${r.nTotal.toLocaleString()}`}</Tex>
          </div>
          <h4 style={{ fontSize: 13, fontWeight: 700, color: "var(--ink-2)", margin: "16px 0 8px" }}>Corrections of α and power</h4>
          <div className="tex-block">
            <Tex block>{`\\alpha_{adj} = \\frac{\\alpha}{C\\cdot S} = \\frac{${p.alpha}}{${p.C}\\cdot ${p.S}} = ${aAdj.toFixed(4)} \\;\\Rightarrow\\; z_{${zSub}} = ${zA.toFixed(3)}`}</Tex>
          </div>
          <div className="tex-block">
            <Tex block>{`power_{adj} = 1-\\frac{1-power}{G_{NIM}+\\min(S,1)} = 1-\\frac{1-${p.power}}{${p.Gnim}+${Math.min(p.S, 1)}} = ${pAdj.toFixed(4)} \\;\\Rightarrow\\; z_{power_{adj}} = ${zP.toFixed(3)}`}</Tex>
          </div>
          <div className="note">{twoSided
            ? "Two-sided z (default) — correct for the two-sided CIs the platform analyses with."
            : "One-sided z — matches Spotify's calculator exactly, but under-powers a two-sided test."} The
            allocation factor is written 1/q_c + 1/q_t so unequal splits are exact.</div>
        </div>
      )}
    </>
  );
}
