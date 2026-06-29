// Live chassis API (FastAPI via the Vite /api proxy). The UI tries this first and falls back to the
// static snapshot when the backend isn't running.
const J = (r) => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); };

export const api = {
  list: () => fetch("/api/experiments").then(J),
  get: (id) => fetch("/api/experiments/" + id).then(J),
  create: (spec) => fetch("/api/experiments", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(spec),
  }).then(J),
  transition: (id, to_state, extra = {}) =>
    fetch(`/api/experiments/${id}/transition?` + new URLSearchParams({ to_state, ...extra }),
      { method: "POST" }).then(J),
  assign: (unit, experiment) =>
    fetch(`/api/assign?unit=${encodeURIComponent(unit)}&experiment=${experiment}`).then(J),
  assignCheck: (experiment, n = 4000) =>
    fetch(`/api/assign/check?experiment=${experiment}&n=${n}`).then(J),
  metrics: () => fetch("/api/metrics").then(J),
};

