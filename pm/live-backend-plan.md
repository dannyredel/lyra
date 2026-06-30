# Plan — live backend (FastAPI → Render) for the interactive create→run→decide loop

> Goal: the deployed app currently runs **read-only** (static snapshot). Deploy the chassis API so a visitor
> can **author a world → Launch → the server runs the DGP + harness → certify vs truth → decide** — live.
> Status: **planned, not executed.** Read tonight; execute tomorrow. ~60–90 min.

## What we already know (de-risked)
- The chassis (`chassis/app.py`, `chassis/worlds.py`, `chassis/scorecard.py`) imports **only light `lyra`
  modules** — `dgp · estimators · estimators_vr · se · metrics · harness · power · decisions · diagnostics ·
  sequential`. **No econml / pymc / pyarrow / duckdb** at runtime. `lyra/__init__.py` is lazy (no transitive
  heavy imports). → fits Render's free tier (512 MB) comfortably.
- ⚠️ `fastapi`, `uvicorn`, and probably `statsmodels` + `scikit-learn` are **not** in `pyproject`
  `dependencies` (they live in the dev env / the `hte` extra). The backend needs its **own requirements
  file** — do **not** `pip install -e .` (that drags in pyarrow/duckdb and still misses fastapi).
- The registry is **in-memory** → re-seeds the 10 demo experiments on every restart/cold-start. Fine for a
  demo; just don't expect created experiments to persist across a sleep.

## Step 0 — pin the exact runtime deps (do this first, locally)
Create a clean throwaway venv and confirm `import chassis.app` succeeds with a **minimal** set, adding only
what the ImportError demands:
```bash
python -m venv /tmp/lyra-api && /tmp/lyra-api/Scripts/python -m pip install \
  fastapi "uvicorn[standard]" numpy pandas scipy statsmodels scikit-learn pyyaml
/tmp/lyra-api/Scripts/python -c "import chassis.app; print('OK')"   # run from the repo root
```
Whatever set makes that print `OK` becomes **`requirements-backend.txt`** (committed at repo root). Likely:
`fastapi · uvicorn[standard] · numpy · pandas · scipy · statsmodels · scikit-learn · pyyaml`.

## Step 1 — backend config in the repo
1. **`requirements-backend.txt`** — the pinned set from Step 0.
2. **`render.yaml`** (infra-as-code, repo root) so Render builds from git on push:
   ```yaml
   services:
     - type: web
       name: lyra-api
       runtime: python
       plan: free
       buildCommand: "pip install -r requirements-backend.txt"
       startCommand: "uvicorn chassis.app:app --host 0.0.0.0 --port $PORT"
       healthCheckPath: /api/experiments
   ```
   (chassis + lyra are top-level packages in the repo, so they import when uvicorn runs from the repo root —
   no install of the package itself needed.)
3. **CORS** — confirm `chassis/app.py`'s `CORSMiddleware` allows the Vercel origin. Set
   `allow_origins=["https://lyra-five-sable.vercel.app", "http://localhost:5173"]` (or `["*"]` for a demo).

## Step 2 — deploy on Render
- New → **Web Service** → connect `github.com/dannyredel/lyra` → it reads `render.yaml` → **Create**.
- Wait for the first build (~3–5 min). Note the URL, e.g. `https://lyra-api.onrender.com`.
- Smoke test: open `https://lyra-api.onrender.com/api/experiments` → should return JSON.

## Step 3 — wire the frontend to the backend
1. **`frontend/src/api.js`** — make the base URL configurable:
   ```js
   const BASE = import.meta.env.VITE_API_URL || "";   // "" → Vite proxy locally
   // then BASE + "/api/experiments", etc.
   ```
2. **Vercel** (app project) → Settings → Environment Variables → `VITE_API_URL = https://lyra-api.onrender.com`
   → redeploy (a `git push` does it now).
3. Keep the **static snapshot as the instant first paint + fallback** (don't regress the read-only demo).

## Step 4 — cold-start UX (the one piece of real frontend work)
Render free tier **sleeps after ~15 min idle** → first request has a **~30–50 s cold start**. The current
`loadList` times out at 15 s and silently drops to static — so a cold backend would *look* permanently static.
Better pattern (in `ChassisApp`):
1. On load, **show the static snapshot immediately** (instant content, `mode = "static"`).
2. **In the background**, ping the backend (`/api/experiments`) with a long, patient timeout (~60 s) +
   a small "● waking the live backend (free-tier cold start)…" pill.
3. When it responds → **upgrade to `mode = "live"`** (sidebar flips to "live · FastAPI", create→run→decide
   enabled). If it never responds → stay static, pill → "live backend asleep — read-only demo".
4. The **Launch** button, if pressed while still cold, shows a "waking the backend…" spinner rather than failing.

## Step 5 — verify the full loop live
Create an A/B experiment in the wizard → **Launch** → confirm the server runs the DGP + harness and the
scorecard shows the **certified-vs-truth** badge + the accrual chart → Stop → Analyze → Ship. Check it on a
cold start too (wait out the spin-up once).

## Risks / notes to keep in mind
- **Cold start** is the main UX wart — Step 4 makes it graceful, not invisible. (A `cron-job.org` ping every
  ~10 min could keep it warm, but that's optional and a bit hacky.)
- **Compute per create**: the harness runs R replications server-side; on a shared free CPU an A/B create may
  take a few seconds. Acceptable; if sluggish, lower the chassis's harness `R` for the live path.
- **No persistence**: created experiments vanish on the next cold-start (in-memory). Fine for a demo; note it
  in the UI copy if needed.
- **`requirements-backend.txt` drift**: it's separate from `pyproject` on purpose (the chassis runtime is a
  strict subset). If the chassis ever imports a new module, add it here too.

## Definition of done
A visitor at lyra-five-sable.vercel.app can create → launch → certify → decide an experiment online, with a
graceful "waking up" state on cold starts, and the read-only demo still works instantly when the backend is
asleep.
