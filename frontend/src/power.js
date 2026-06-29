// Client-side power / sample-size — the SSC formula, kept in lock-step with lyra/power.py so the
// "New experiment" calculator runs live on the static snapshot (no backend needed). Two-sided z_{1-α/2}.

function erf(x) {
  const t = 1 / (1 + 0.3275911 * Math.abs(x));
  const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592)
    * t * Math.exp(-x * x);
  return x >= 0 ? y : -y;
}
export const normCdf = (x) => 0.5 * (1 + erf(x / Math.SQRT2));

// Acklam's inverse normal CDF
export function normPpf(p) {
  const a = [-3.969683028665376e1, 2.209460984245205e2, -2.759285104469687e2, 1.383577518672690e2, -3.066479806614716e1, 2.506628277459239e0];
  const b = [-5.447609879822406e1, 1.615858368580409e2, -1.556989798598866e2, 6.680131188771972e1, -1.328068155288572e1];
  const c = [-7.784894002430293e-3, -3.223964580411365e-1, -2.400758277161838e0, -2.549732539343734e0, 4.374664141464968e0, 2.938163982698783e0];
  const d = [7.784695709041462e-3, 3.224671290700398e-1, 2.445134137142996e0, 3.754408661907416e0];
  const pl = 0.02425, ph = 1 - pl; let q, r;
  if (p < pl) { q = Math.sqrt(-2 * Math.log(p)); return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1); }
  if (p <= ph) { q = p - 0.5; r = q * q; return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1); }
  q = Math.sqrt(-2 * Math.log(1 - p)); return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
}

const adj = ({ alpha = 0.05, power = 0.8, C = 1, S = 1, Gnim = 0 }) => ({
  aAdj: alpha / (C * Math.max(S, 1)),
  pAdj: 1 - (1 - power) / (Gnim + Math.max(Math.min(S, 1), 1)),
});

export function requiredN(p) {
  const sigma2 = p.binary ? p.mu * (1 - p.mu) : p.sigma2;
  const { aAdj, pAdj } = adj(p);
  const z = normPpf(1 - (p.twoSided === false ? aAdj : aAdj / 2)) + normPpf(pAdj);
  const delta = p.mu * p.relMde;
  const alloc = 1 / p.qc + 1 / (1 - p.qc);
  const n = alloc * z * z * sigma2 * (1 - (p.rho || 0)) / (delta * delta);
  return { nTotal: Math.round(n), nPerArm: Math.round(n * p.qc), aAdj, pAdj, absMde: delta, z, sigma2 };
}

// closed-form power at a given total N (the curve)
export function powerAtN(N, p) {
  const sigma2 = p.binary ? p.mu * (1 - p.mu) : p.sigma2;
  const { aAdj } = adj(p);
  const delta = p.mu * p.relMde;
  const alloc = 1 / p.qc + 1 / (1 - p.qc);
  const se = Math.sqrt(alloc * sigma2 * (1 - (p.rho || 0)) / Math.max(N, 1));
  return normCdf(delta / se - normPpf(1 - (p.twoSided === false ? aAdj : aAdj / 2)));
}

// minimum detectable effect (relative) at a given N — the inverse
export function mdeAtN(N, p) {
  const sigma2 = p.binary ? p.mu * (1 - p.mu) : p.sigma2;
  const { aAdj, pAdj } = adj(p);
  const z = normPpf(1 - (p.twoSided === false ? aAdj : aAdj / 2)) + normPpf(pAdj);
  const alloc = 1 / p.qc + 1 / (1 - p.qc);
  const absMde = Math.sqrt(alloc * z * z * sigma2 * (1 - (p.rho || 0)) / Math.max(N, 1));
  return { absMde, relMde: p.mu ? absMde / p.mu : NaN };
}
