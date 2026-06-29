# frontend/ — the Lyra chassis UI (Ocean palette)

The React scorecard for the experimentation platform. Bright off-white background, white cards, navy ink +
one blue accent, soft pastel status chips (the **Ocean** palette, LYRA §13). Built with Vite + React +
Recharts. It reads a **static snapshot** (`public/data/chassis.json`, produced by `python -m chassis.export`)
so it deploys without a server; the live FastAPI app (`chassis/app.py`) serves the same shape at `/api`.

## Screens
- **Experiments registry** (`Registry.jsx`) — portfolio stat cards + a table: name · metric · owner ·
  state chip · effect (CI-coloured) · the **certified** badge · power bar.
- **Scorecard** (`Scorecard.jsx`) — the state-gated readout: the effect headline + **CI-colour-bar**
  (green/red/grey by sign, with a faint mark at the *true* effect), stat cards (effect · CI · power ·
  **validation**), the **accrual chart** (the CI band narrowing onto the dashed *true-effect* line — the
  superpower no real platform can show), the **SRM / A·A diagnostics**, and the recorded **decision** (for
  DECIDED) or the **power-gate** (for DRAFT).

## Run
```bash
python -m chassis.export                  # (re)write public/data/chassis.json
cd frontend && npm install && npm run dev # → http://localhost:5173
# or, live backend:  uvicorn chassis.app:app --reload   (point fetch at /api)
```

`src/ocean.css` is the design system (tokens + components); `src/ui.jsx` the shared bits (chips, badges,
CI-bar). The pre-pivot marketplace replay components (`App.jsx`, `Portfolio.jsx`, …) are retained in `src/`
but no longer wired (the chassis app is the entry via `main.jsx`).
