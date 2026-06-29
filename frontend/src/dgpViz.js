// Client-side, schematic DGP previews — parameter-responsive and instant (no backend round-trip). They
// convey the *shape* of each design's data as you drag the sliders; the real, validated numbers come from
// running the experiment. A tiny LCG keeps them deterministic per (params, seed).

const lcg = (seed) => { let s = (seed * 9301 + 49297) % 233280 || 7; return () => (s = (s * 9301 + 49297) % 233280) / 233280; };
const lin = (a, b, n) => Array.from({ length: n }, (_, i) => a + (b - a) * i / (n - 1));
const clamp01 = (x) => Math.max(0, Math.min(1, x));

// A/B: outcome distribution, control vs treatment
export function abPreview({ binary, mu, effect, sigma = 1 }) {
  if (binary) {
    const p0 = clamp01(mu), p1 = clamp01(mu + effect);
    return { kind: "bars", data: [
      { outcome: "did not convert", control: +(1 - p0).toFixed(3), treatment: +(1 - p1).toFixed(3) },
      { outcome: "converted", control: +p0.toFixed(3), treatment: +p1.toFixed(3) }] };
  }
  const s = Math.max(0.2, sigma);
  const xs = lin(mu - 3.5 * s, mu + effect + 3.5 * s, 50);
  const dn = (x, m) => Math.exp(-0.5 * ((x - m) / s) ** 2);
  return { kind: "area", data: xs.map((x) => ({ x: +x.toFixed(2), control: +dn(x, mu).toFixed(3), treatment: +dn(x, mu + effect).toFixed(3) })) };
}

// Switchback: treatment toggles on/off over periods; the cell-mean tracks it (+ a diurnal wave)
export function switchbackPreview({ mu, tau, H }) {
  const r = lcg(7);
  return Array.from({ length: Math.max(6, Math.min(H, 40)) }, (_, t) => {
    const on = r() < 0.5 ? 1 : 0;
    const wave = Math.sin(2 * Math.PI * t / 8) * Math.abs(tau) * 0.6;
    return { period: t + 1, treat: on, y: +(mu + wave + tau * on + (r() - 0.5) * Math.abs(tau)).toFixed(1) };
  });
}

// Cluster: between-cluster mean scatter (control vs treated clusters); shows between vs within variance
export function clusterPreview({ G, effect }) {
  const r = lcg(11), n = Math.max(10, Math.min(G, 80));
  return Array.from({ length: n }, (_, g) => {
    const treated = g >= n / 2 ? 1 : 0;
    return { g, treated, mean: +((r() - 0.5) * 2 + effect * treated).toFixed(3) };
  });
}

// Marketplace: the naive uplift decays with treated allocation; the true global effect stays flat & small
export function marketplacePreview({ boost }) {
  const trueGlobal = +(0.13 * boost).toFixed(3);
  return Array.from({ length: 9 }, (_, i) => {
    const phi = 0.1 + i * 0.1;
    const naive = (0.45 + boost * 0.35) / (1 + phi * boost * 1.1);
    return { phi: Math.round(phi * 100), naive: +naive.toFixed(3), truth: trueGlobal };
  });
}
