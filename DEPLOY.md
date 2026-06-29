# DEPLOY.md — shipping the Lyra chassis

Two ways to run it. The **static demo** is the zero-cost portfolio deploy; the **live app** is for the
full interactive create→run→decide loop (local, or a paid backend host).

## A. Static demo (recommended for a portfolio) — zero cost, no backend

The React app falls back to a **precomputed snapshot** (`frontend/public/data/chassis.json`) whenever the
`/api` backend isn't reachable, so the built site is fully self-contained.

```bash
python -m chassis.export          # (re)generate the snapshot from the seeded experiments
cd frontend && npm run build      # → frontend/dist/  (self-contained static site)
npm run preview                   # optional: verify dist/ locally (no backend) → http://localhost:4173
```

Deploy `frontend/dist/` to any static host:
- **Vercel / Netlify** — drag-and-drop `dist/`, or connect the repo with build `cd frontend && npm run build` and output `frontend/dist`.
- **GitHub Pages** — push `dist/` to a `gh-pages` branch (or use an Action). `vite.config.js` sets `base: "./"` so it works under any subpath.

**What the static demo shows (read-only + one live tool):**
- ✅ Experiments registry + every **scorecard** (certified-vs-truth badge, accrual chart with the
  always-valid CS, SRM, decision) · **Metrics** catalog · **Decisions** table
- ✅ The **power calculator** in "+ New experiment" (runs entirely client-side)
- ⚠️ Needs the live backend: **launching/running** a created experiment, the **Assignment** lookup
  (both degrade gracefully — Assignment shows a "start the backend" note; the sidebar shows a `demo · static` badge)

## B. Live app — the full loop (create → run the DGP → certify → decide)

The backend runs the Python DGPs + the Monte-Carlo harness server-side, so it needs a real Python host.

```bash
# terminal 1 — the API
uvicorn chassis.app:app --port 8000
# terminal 2 — the UI (Vite proxies /api → :8000)
cd frontend && npm run dev         # → http://localhost:5173  (sidebar shows "live · FastAPI")
```

To host it live: deploy the FastAPI app as an always-on container (**Render / Fly.io / Railway**, or a VPS)
and point the frontend's `/api` at it. State is **in-memory** (re-seeds 10 demos on restart). If you later
want created experiments to persist, add SQLAlchemy + a `DATABASE_URL` (SQLite file locally → managed
Postgres such as Neon/Supabase in prod) — note plain SQLite is wiped on hosts with an ephemeral filesystem.
