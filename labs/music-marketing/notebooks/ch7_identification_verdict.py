# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.3
#   kernelspec:
#     display_name: Python (vega-mml)
#     language: python
#     name: vega-mml
# ---

# %% [markdown]
# # Chapter 7 · The verdict — where does it hold, where does it break?
# ### Track R · sweep the scarcity grid → GO / RESCOPE / KILL
#
# [Chapter 6](ch6_identification_harness.ipynb) built the recovery harness and proved it on **one**
# favorable scenario. But "it works on a good day" isn't a feasibility verdict. The real question for
# *causal measurement for music marketing* is a **map**: across the regimes a real label actually lives
# in — *few* releases, *collinear* channels, *no* geo experiment, *aggressive* spend chasing — where
# does the platform still recover the truth, and where does it quietly fail?
#
# So we take the **same H1–H5 ledger** from Chapter 6 and apply it to a **grid** of scenarios, dialling
# one scarcity knob at a time off the favorable baseline. Each cell earns one of three calls:
#
# | verdict | meaning |
# |---|---|
# | **GO** | every hypothesis passes — recover magnitudes *and* decisions with calibrated intervals |
# | **RESCOPE** | the **decision** (keep/cut) is reliable, but magnitudes/intervals aren't — trust the call, caveat the number |
# | **KILL** | even the keep/cut decision is unreliable — don't ship a measurement here |
#
# ## The ledger (recap)
# | id | hypothesis | GO bar |
# |---|---|---|
# | **H1** | median \|relative bias\| of recovered mROAS | < 0.25 |
# | **H2** | 80% credible-interval coverage | 0.70–0.90 |
# | **H3** | keep/cut accuracy vs the €6 break-even bar | ≥ 0.80 |
# | **H4** | κ=0 false-positive rate (don't invent a multiplier) | ≤ 0.20 |
# | **H5** | pooling cuts per-channel mROAS RMSE vs no-pooling | ≥ 20% |
#
# > **Compute.** Each grid cell is M Monte-Carlo fits; the full grid is an **offline job**
# > (`run_grid.py` → `outputs/grid_results.json`), exactly the exploratory-vs-decision split in
# > `REPLICATE.md`. This notebook *loads and renders* that JSON, so it's instant. Re-run the job with
# > `python run_grid.py 20` for tighter (M=20) estimates; M≥100 for decision grade needs a GPU/cluster.

# %% [markdown]
# ## 1 · Load the grid

# %%
import json, pathlib
import numpy as np, pandas as pd, matplotlib.pyplot as plt
plt.rcParams.update({"figure.figsize":(11,4.5),"figure.dpi":110,"axes.grid":True,"grid.alpha":.25,
    "axes.spines.top":False,"axes.spines.right":False,"font.size":11})
BLUE,RED,GREEN,GREY,GOLD="#3b6fb0","#d1495b","#66a182","#9e9e9e","#e8a33d"
VCOL = {"GO":GREEN, "RESCOPE":GOLD, "KILL":RED}

res = json.loads((pathlib.Path.cwd().parent / "outputs" / "grid_results.json").read_text())
cells = res["cells"]; CHANNELS = res["channels"]
print(f"grid: {len(cells)} cells × M={res['M']} sims  |  built in {res['elapsed_s']:.0f}s offline")
print(f"κ=0 null false-positive rate: {res['null_kappa_fp']:.0%}")

# %% [markdown]
# ## 2 · The grid at a glance
#
# One row per scenario: the scarcity knobs, the recovered metrics, and the verdict.

# %%
def row(c):
    p = c["pooled_geo"]
    return {"scenario": c["label"], "stresses": c["axis"], "N": c["knobs"]["N"], "ρ": c["knobs"]["rho"],
            "geo": "✓" if c["knobs"]["geo"] else "—", "sims": p.get("n_sims", 0),
            "|bias|": round(p.get("median_abs_rel_bias", np.nan), 2),
            "coverage": round(p.get("coverage", np.nan), 2),
            "keep/cut": round(p.get("class_accuracy", np.nan), 2),
            "RMSE": round(p.get("mroas_rmse", np.nan), 2), "verdict": c["verdict"]}
grid = pd.DataFrame([row(c) for c in cells])
grid

# %% [markdown]
# ## 3 · The verdict frontier
#
# The headline picture: each scenario's **keep/cut accuracy** (the decision), coloured by its overall
# verdict. Read the *bars*, not just the colours — keep/cut stays above the 0.80 bar in **every** cell,
# eroding only toward ~0.85 in the worst case as the borderline channel (spotify) starts to straddle. The
# GO/RESCOPE **labels** flip on H2 (interval calibration), which is conservative and statistically noisy at
# this exploratory M — so treat the colours as indicative and the keep/cut bars as the real signal.

# %%
fig, ax = plt.subplots(figsize=(10, 0.6*len(cells)+1))
y = np.arange(len(cells))[::-1]
for yi, c in zip(y, cells):
    acc = c["pooled_geo"].get("class_accuracy", 0)
    ax.barh(yi, acc, color=VCOL[c["verdict"]], alpha=.85)
    ax.text(0.01, yi, f" {c['label']}", va="center", ha="left", fontsize=10, color="white", fontweight="bold")
    ax.text(acc+0.01, yi, c["verdict"], va="center", fontsize=9, color=VCOL[c["verdict"]], fontweight="bold")
ax.axvline(0.80, color="k", ls="--", lw=1); ax.text(0.80, len(cells)-.4, " keep/cut bar 0.80", fontsize=8)
ax.set_yticks([]); ax.set_xlabel("keep/cut accuracy"); ax.set_xlim(0, 1.12)
ax.set_title("Verdict frontier: keep/cut accuracy as scarcity bites")
handles = [plt.Rectangle((0,0),1,1,color=VCOL[v]) for v in ["GO","RESCOPE","KILL"]]
ax.legend(handles, ["GO","RESCOPE","KILL"], fontsize=9, loc="lower right")
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 4 · What degrades, and how
#
# Reading the three core metrics across the grid shows *which* part of inference each scarcity axis
# attacks. Two are stable and reassuring: **keep/cut stays ≥0.85** and **bias stays well under the 0.25
# bar** in every cell. The fragile one is **coverage (H2)** — it drifts out of the calibrated band (usually
# *over*-covering: intervals too wide) and is noisy at M=10. Certifying it is the decision-grade (M≥100) job.

# %%
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
labels = [c["label"] for c in cells]
x = np.arange(len(cells))
for ax, key, ttl, ref, refln in [
    (axes[0], "class_accuracy", "keep/cut accuracy", 0.80, "GO bar"),
    (axes[1], "median_abs_rel_bias", "median |rel bias|", 0.25, "GO bar"),
    (axes[2], "coverage", "80% CI coverage", None, None)]:
    vals = [c["pooled_geo"].get(key, np.nan) for c in cells]
    cols = [VCOL[c["verdict"]] for c in cells]
    ax.bar(x, vals, color=cols, alpha=.85)
    if ref is not None: ax.axhline(ref, color="k", ls="--", lw=1, label=refln)
    if key == "coverage":
        ax.axhspan(0.70, 0.90, color=GREEN, alpha=.12, label="calibrated band")
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_title(ttl); ax.legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 5 · The borderline channel — where the decision is actually at risk
#
# Bias is small for *every* channel across the grid — but it doesn't need to be large to matter, and it
# isn't uniform. meta/tiktok sit far above the bar and plugger far below, so their residual bias never
# changes the call. **spotify is planted just below the €6 bar (€5)**, so the *same* small upward bias
# occasionally pushes it over — and that single channel is what erodes keep/cut from 1.00 toward 0.85 in
# the hard cells. The honest scope: trust the call on channels clearly off the line; treat a near-bar
# channel as *"uncertain, likely below."*

# %%
base = cells[0]; hard = min(cells, key=lambda c: c["pooled_geo"].get("class_accuracy", 1.0))  # lowest keep/cut
fig, ax = plt.subplots(figsize=(9.5, 4))
x = np.arange(len(CHANNELS)); w = 0.38
for off, c, col in [(-w/2, base, BLUE), (w/2, hard, GOLD)]:
    ch = c["pooled_geo"].get("channels", {})
    ax.bar(x+off, [abs(ch.get(k, np.nan)) for k in CHANNELS], w,
           color=col, alpha=.85, label=f"{c['label']} ({c['verdict']})")
ax.axhline(0.25, color="k", ls="--", lw=1, label="H1 bar 0.25")
ax.set_xticks(x); ax.set_xticklabels(CHANNELS); ax.set_ylabel("|median rel bias|")
ax.set_title("Per-channel bias: clear channels recover; the borderline channel (spotify) is what flips"); ax.legend(fontsize=9)
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 6 · The baseline ledger & the κ=0 falsification
#
# The full H1–H5 readout for the favorable cell, plus the two κ numbers that make the multiplier claim
# credible: **power** (detect κ when it's real) vs **false-positive** (don't when it isn't).

# %%
print(f"BASELINE  {base['label']}  →  VERDICT: {base['verdict']}\n")
for h, d in base["ledger"].items():
    print(f"  [{'PASS' if d['pass'] else 'FAIL'}]  {h:14s} {d['detail']}")
print(f"\n  κ detection — power @ κ=0.8: {base['pooled_geo'].get('kappa_detected_frac', float('nan')):.0%}"
      f"   |   false-positive @ κ=0: {res['null_kappa_fp']:.0%}  (bar ≤20%)")

# %% [markdown]
# ## 7 · The verdict for music-marketing measurement
#
# **Is causal measurement for music marketing technically feasible?** The grid answers with a scoped
# yes:
#
# - **The decision is robust.** Keep/cut holds above the bar across the *entire* grid — eroding only to
#   ~0.85 in the worst case (N=18, ρ=0.85, no geo) — and the κ=0 null never invents a multiplier. **No cell
#   KILLs** in the realistic range: the platform can credibly tell a label which channels to fund.
# - **Recovery is unbiased; calibration is the open question.** Magnitude bias (H1) stays low across the
#   grid, and the *borderline* channel is the only place the decision wobbles. Interval calibration (H2) is
#   conservative and noisy at exploratory **M=10** — it's what flips the GO/RESCOPE labels, and certifying
#   it is the pending **M≥100 decision-grade** run (the compute-bound step the study always flagged).
# - **Pooling + experiments are not optional.** No-pooling collapses (keep/cut 0.67, coverage 0.17); the
#   geo anchor pins the always-on channel. **Partial pooling across releases** and **experiments-as-priors**
#   are exactly what earn the GO cells.
#
# ### Forward — distil into the platform
# These learnings are what graduate into **NB 11 (observational)** and `lyra/observational.py`: the
# hierarchical MMM behind the `Estimator` protocol, the geo-anchor calibration, and *this very harness*
# as its recovery gate — every estimator the platform ships must pass a ground-truth recovery grid
# before it's trusted. The simulator authored the world; the harness made the trust **measurable**.
