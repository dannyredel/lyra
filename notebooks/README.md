# notebooks/ — the Lyra curriculum (build raw, then promote)

These notebooks are the **operating model** ([[notebooks-first-promotion]], LYRA §10): each one builds
a method **raw by hand** from the libraries (learn the mechanics), *then* **promotes** the core into
`.py` modules certified by the harness. The full plan is **[ROADMAP.md](ROADMAP.md)** (10 notebooks
across the four pillars: DGP · experiment · metric · method). `_old/` holds the earlier notebooks —
recycle freely.

> **Build raw first, productionize second.** The notebook is where you *understand* every line; the
> promotion to `lyra/` is what makes "in production" mean something (it must pass the harness vs a known truth).

## Contents

| Notebook | What it builds | Promotes to |
|---|---|---|
| `01_spine.py` | DGP ladder (L0/L1) · Core ATE (diff/OLS/**AIPW**) · the **Monte-Carlo harness** · the **robustness grid** (OLS biases / AIPW survives) | `lyra/{protocols,dgp,estimators,harness}.py` |
| *(02–10 — see `ROADMAP.md`)* | metrics · interference money-shot · switchback/VR · sequential · power · CATE · uplift/policy · observational · incrementality | `lyra/…`, `inference/…` |
| `_old/` | archived first-pass notebooks (world · money-shot · estimators/trust · switchback · spine-v0) | — |
| `nbtools.py` | thin shared helpers — matplotlib style + palette + (Vega) config builders. No estimation logic. | — |

## Jupytext pairing (why there are `.py` *and* `.ipynb`)

Each notebook is stored as a **paired `.py` (percent format) + `.ipynb`** via
[jupytext](https://jupytext.readthedocs.io). The `.py` is the source of truth — diffable,
code-reviewable, and CI-runnable; the `.ipynb` carries the rendered outputs/figures for reading in the
IDE. Editing either one and saving keeps them in sync (jupytext handles it).

Install the tooling:

```bash
pip install -e ".[notebooks]"        # jupytext, matplotlib, nbconvert, ipykernel
```

### Run / regenerate a notebook from its `.py`

```bash
# execute and write the paired .ipynb (uses the current Python as the kernel)
python -m jupytext --to ipynb --execute --set-kernel - notebooks/02_money_shot.py
```

`--set-kernel -` pins execution to the Python running the command (so it sees the project's deps).
On Windows/Anaconda this resolves to the `base` kernel.

### Notes
- The notebooks `chdir` to the repo root (via `nbtools.use_repo_root()`) so `config.yaml` and
  `events/` resolve, and add the repo to `sys.path`.
- Analysis runs pass `compute_tau=False` (truth comes from the shadow-run oracle, not per-conversion
  `ground_truth_tau`) — it just makes them faster.
- Notebooks write scratch event logs to throwaway dirs and clean them up in the last cell; they do
  **not** touch the canonical `events/` log produced by `make run`.
