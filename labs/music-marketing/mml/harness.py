"""mml.harness — the identification-study engine (Track R / REPLICATE).

Where the rest of `mml` *demonstrates* estimators once (Track M), this module *stress-tests whether they
recover a known truth* under music's data poverty. It is a Monte-Carlo recovery harness:

    plant per-channel mROAS truth -> simulate a scarce roster -> fit a hierarchical MMM ->
    score recovery (bias / coverage / keep-cut / kappa) -> repeat M x across a scarcity grid -> VERDICT.

This is the PyMC rebuild of the (now-absent) ``vega/`` NumPyro package described in REPLICATE.md, sharing
the platform's "plant truth -> score recovery" discipline (``lyra.harness``). The MMM is ch4's hierarchical
nutpie model extended to multiple channels + an organic->paid multiplier (kappa) + an optional geo anchor.

Layout (one file, sectioned):
    Scenario / constants            the scarcity knobs + planted channel mROAS + the break-even bar
    simulate_roster(scn, seed)      DGP: plant truth, emit a release x week x channel panel
    fit_mmm / mroas_posterior       the estimator under test (nopool | pooled | pooled_geo)
    geo_prior                       the simulated geo-lift anchor on the high-spend channel
    score_fit / run_cell            scoring + the Monte-Carlo loop with convergence gating
    conclude                        the H1-H5 ledger -> GO / RESCOPE / KILL
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from mml.primitives import adstock

# --- planted truth -------------------------------------------------------------------------------
# Channel mROAS = incremental streams per EUR. Two high-spend channels clear the break-even bar (keep),
# two low-spend channels sit below it (cut). The keep/cut split is the decision the study must get right.
CHANNELS = ["meta", "tiktok", "spotify", "plugger"]
MROAS = {"meta": 9.0, "tiktok": 14.0, "spotify": 5.0, "plugger": 2.5}  # spotify sits just below the €6 bar -> straddles under bias (REPLICATE's weak point)
BREAKEVEN = 6.0                                   # EUR mROAS a channel must beat to be worth funding
SPEND_SHARE = {"meta": 0.30, "tiktok": 0.28, "spotify": 0.22, "plugger": 0.20}  # comparable budgets -> ROAS, not spend, decides keep/cut
ADSTOCK = {"meta": 0.45, "tiktok": 0.55, "spotify": 0.30, "plugger": 0.20}      # geometric carryover theta
GEO_CHANNEL = "meta"                              # the channel a geo holdout can anchor (broad-reach)

# decision thresholds (the GO bars) — mirror REPLICATE.md's H-ledger
REL_BIAS_GO = 0.25            # H1  median |relative bias| must be under this
COVERAGE_LO, COVERAGE_HI = 0.70, 0.90   # H2  80% CI coverage band
CLASS_ACCURACY_GO = 0.80     # H3  keep/cut accuracy
KAPPA_FP_MAX = 0.20          # H4  false-positive rate of kappa-detection at kappa=0
KAPPA_ROPE = 0.05            # kappa "detected" iff its 80% CI clears +/- this band around 0
POOLING_RMSE_GO = 0.20       # H5  pooling must cut per-channel mROAS RMSE by >= this vs no-pool


@dataclass(frozen=True)
class Scenario:
    """A point on the scarcity grid. Defaults = the GO cell (the regime we expect to pass)."""
    N: int = 40                 # number of releases (data poverty knob: fewer = harder)
    rho: float = 0.6            # cross-channel spend collinearity (higher = channels harder to separate)
    kappa: float = 0.8          # organic->paid multiplier (0 = no interaction; the H4 null sets this 0)
    gamma: float = 0.5          # spend endogeneity: budget ~ expected-success^gamma (0 = exogenous)
    geo_anchor: bool = True     # is a geo-lift prior on the high-spend channel available?
    W: int = 12                 # weeks observed per release

    def label(self) -> str:
        return (f"N{self.N}_rho{self.rho}_k{self.kappa}_g{self.gamma}"
                f"_{'geo' if self.geo_anchor else 'nogeo'}")


def _adstock_norm(x: np.ndarray, theta: float) -> np.ndarray:
    """Mass-conserving geometric adstock: carry spend forward but keep sum(out) == sum(in), so the
    response coefficient reads directly as mROAS (streams per EUR) rather than being inflated by 1/(1-theta)."""
    return adstock(x, theta) * (1.0 - theta)


def simulate_roster(scn: Scenario, seed: int = 0):
    """Plant the truth and simulate one label's roster. Returns ``(data, truth)``.

    ``data`` is a release x week long panel: ``rid, week, streams, organic, orgmom`` + one spend column
    per channel. ``truth`` exposes the realized per-channel mROAS, the keep/cut labels, and kappa — what
    every estimator on this panel is scored against. Endogeneity (``gamma``) ties spend to a release's
    expected success and collinearity (``rho``) ties the channels' weekly spend together — the two forces
    that make naive spend->streams regressions lie.
    """
    rng = np.random.default_rng(seed)
    N, W = scn.N, scn.W
    wk = np.arange(W)
    decay = 0.18                                         # organic weekly decay

    # release sizes (log-normal, heavy-tailed like a real roster) and their organic momentum z-score
    log_peak = rng.normal(np.log(40_000), 0.9, N)
    peak = np.exp(log_peak)
    orgmom = (log_peak - log_peak.mean()) / log_peak.std()   # standardized "expected success"

    # release-level budget is endogenous: bigger expected success -> more spend (gamma). The 0.06 factor
    # puts paid media at ~12-15% of streams -> identifiable from the data given distinct flighting.
    budget = 0.06 * peak * np.exp(scn.gamma * orgmom) * np.exp(rng.normal(0, 0.25, N))

    # distinct per-channel weekly flighting (real MMM identification comes from channels moving differently
    # in time). Each profile differs from the others AND from the organic decay exp(-decay*w), so no channel
    # aliases "more baseline". tiktok is a *hump* (rise-then-fall), deliberately un-decay-like.
    prof = {"meta": np.ones(W),                                 # flat always-on
            "tiktok": wk * np.exp(-0.6 * wk),                   # launch hump, peaks ~week 2
            "spotify": (wk / (wk + 2.0)) * np.exp(-0.04 * wk),  # editorial-playlist ramp then plateau
            "plugger": np.maximum(np.cos(2 * np.pi * wk / 4 - 0.4), 0) ** 1.5}  # sharp pulses every ~4 wks
    WPROF = {c: np.clip(prof[c], 1e-3, None) for c in CHANNELS}
    WPROF = {c: v / v.sum() for c, v in WPROF.items()}

    # per-release channel MIX varies (a TikTok-led campaign vs a playlist-led one) -> the channels' spend is
    # NOT proportional across releases, which is what actually identifies each mROAS. rho is the collinearity
    # knob: high rho -> high Dirichlet concentration -> nearly the same mix every release -> channels collinear
    # and hard to separate; low rho -> mix varies a lot -> well-identified.
    conc = 2.5 + 60.0 * scn.rho ** 2                            # Dirichlet concentration grows with rho
    base_share = np.array([SPEND_SHARE[c] for c in CHANNELS])
    shares = rng.dirichlet(conc * base_share, size=N)           # (N, n_channels), rows sum to 1
    share = {c: shares[:, i] for i, c in enumerate(CHANNELS)}

    organic = peak[:, None] * np.exp(-decay * wk)[None, :] * np.exp(rng.normal(0, 0.025, (N, W)))
    kfac = 1.0 + scn.kappa * orgmom                          # per-release organic->paid multiplier

    # build per-channel spend + incremental as (N, W) arrays. kappa redistributes the channel's incremental
    # across releases (paid converts better on hot ones) but is rescaled so the *channel* mROAS stays exactly
    # MROAS[c] for any kappa/gamma -> the keep/cut ground truth never moves with the grid cell.
    spend, incr = {}, {}
    for c in CHANNELS:
        sp = budget[:, None] * share[c][:, None] * WPROF[c][None, :] * np.exp(rng.normal(0, 0.10, (N, W)))
        ad = np.vstack([_adstock_norm(sp[r], ADSTOCK[c]) for r in range(N)])
        raw = ad * kfac[:, None]                              # carryover x organic-momentum multiplier
        scale = MROAS[c] * sp.sum() / raw.sum()               # pin realized channel mROAS to MROAS[c] exactly
        spend[c], incr[c] = sp, scale * raw

    mu = np.maximum(organic + sum(incr.values()), 1.0)
    streams = rng.poisson(mu).astype(float)
    rows = []
    for r in range(N):
        for w in range(W):
            row = dict(rid=r, week=w, streams=streams[r, w], organic=organic[r, w], orgmom=orgmom[r])
            for c in CHANNELS:
                row[c] = spend[c][r, w]
            rows.append(row)

    data = pd.DataFrame(rows)
    spend_tot = {c: spend[c].sum() for c in CHANNELS}
    mroas = {c: incr[c].sum() / spend_tot[c] for c in CHANNELS}   # realized per-channel mROAS = the estimand
    truth = dict(
        mroas=mroas,
        keep={c: mroas[c] >= BREAKEVEN for c in CHANNELS},
        kappa=scn.kappa,
        spend={c: spend_tot[c] for c in CHANNELS},
        breakeven=BREAKEVEN,
        scenario=scn.label(),
    )
    return data, truth


def naive_roas(data: pd.DataFrame) -> dict:
    """The straw man: pooled OLS of weekly streams on each channel's spend, no baseline, no pooling.
    Endogeneity + the organic baseline make this wildly biased — the bias we are trying to beat."""
    import numpy as np
    X = np.column_stack([np.ones(len(data))] + [data[c].values for c in CHANNELS])
    beta, *_ = np.linalg.lstsq(X, data.streams.values, rcond=None)
    return {c: float(beta[i + 1]) for i, c in enumerate(CHANNELS)}


# --- the estimator under test --------------------------------------------------------------------
# A multi-channel hierarchical NB-MMM (ch4's nutpie model extended): per-release, per-channel response
# coefficients partially pooled toward a channel-level mROAS, an organic->paid multiplier kappa, an
# optional geo anchor on the high-spend channel. Three estimators differ only in how beta is pooled.
_LMAX = 8
FAST = dict(draws=500, tune=500, chains=2, cores=1, nuts_sampler="nutpie",
            target_accept=0.9, progressbar=False)


def _lagmat(data: pd.DataFrame, col: str) -> np.ndarray:
    """Lagged-spend design matrix (rows align to data; lag l up to _LMAX), reset within each release."""
    M = np.zeros((len(data), _LMAX + 1))
    for _, g in data.groupby("rid"):
        idx = g.index.values
        x = g[col].values                               # EUR: mass-conserving adstock -> beta reads as mROAS
        for l in range(_LMAX + 1):
            M[idx[l:], l] = x[: len(x) - l] if l > 0 else x
    return M


def geo_prior(data: pd.DataFrame, truth: dict, seed: int = 0) -> dict:
    """Simulate a randomized geo holdout on the broad-reach channel: a noisy but unbiased read of its
    true mROAS, as a meta-analytic Normal(mean, sd). This is the anchor the ``pooled_geo`` estimator adds."""
    rng = np.random.default_rng(seed + 9_973)
    n_exp = 6                                            # number of geo experiments pooled
    truth_m = truth["mroas"][GEO_CHANNEL]
    reads = truth_m + rng.normal(0, 0.30 * truth_m, n_exp)   # unbiased, ~30% noise per experiment
    return {"channel": GEO_CHANNEL, "mean": float(reads.mean()),
            "sd": float(reads.std(ddof=1) / np.sqrt(n_exp)), "n_experiments": n_exp}


def fit_mmm(data: pd.DataFrame, truth: dict, estimator: str = "pooled",
            gp: dict | None = None, nuts: dict | None = None, seed: int = 0):
    """Fit the MMM. ``estimator`` in {nopool, pooled, pooled_geo}. Returns an ArviZ idata whose posterior
    carries one ``mroas_<channel>`` deterministic (the estimand) plus ``kappa``."""
    import pymc as pm
    import pytensor.tensor as pt
    nuts = {**FAST, **(nuts or {})}
    rid = data.rid.values
    N = int(rid.max()) + 1
    y = data.streams.values
    wk = data.week.values
    orgmom = data.groupby("rid").orgmom.first().values
    lags = {c: _lagmat(data, c) for c in CHANNELS}
    spend_tot = {c: data[c].sum() for c in CHANNELS}            # EUR -> mroas deterministic reads as streams/EUR
    obs_logB = np.log(data.groupby("rid").streams.max().values)    # per-release intercept anchor (~launch peak)

    with pm.Model() as m:
        # informed baseline: releases decay at a known-ish rate and each release's level is anchored to its
        # observed mean streams. A free-for-all baseline soaks up the paid signal (the central MMM trap);
        # constraining it is what lets the distinct channel flighting identify each mROAS.
        d_ = pm.TruncatedNormal("d", mu=0.18, sigma=0.04, lower=0.02)
        B = pt.exp(pm.Normal("logB", obs_logB, 0.25, shape=N))
        base = B[rid] * pt.exp(-d_ * wk)
        kappa = pm.Normal("kappa", 0.0, 0.5)
        kfac = 1.0 + kappa * orgmom[rid]
        mu = base
        for c in CHANNELS:
            a = pm.Beta(f"alpha_{c}", 2, 4)
            w = (1 - a) * a ** np.arange(_LMAX + 1)                 # mass-normalized adstock weights
            ad = pt.dot(lags[c], w)
            # skeptical per-channel prior centered *below* the break-even bar: a channel is assumed not
            # worth funding until the data proves it (a sane budget default, and it stops weakly-identified
            # low-spend channels from reverting *up* to a false "keep").
            if estimator == "nopool":
                beta = pt.exp(pm.Normal(f"logbeta_{c}", np.log(4.0), 1.0, shape=N))   # per release, unpooled
            else:
                mu_b = pm.Normal(f"mu_logbeta_{c}", np.log(4.0), 1.0)
                sig_b = pm.HalfNormal(f"sig_logbeta_{c}", 0.4)
                z = pm.Normal(f"z_{c}", 0, 1, shape=N)
                beta = pt.exp(mu_b + sig_b * z)                    # partial pooling across releases
            contrib = beta[rid] * ad * kfac
            mu = mu + contrib
            pm.Deterministic(f"mroas_{c}", pt.sum(contrib) / spend_tot[c])
        if estimator == "pooled_geo" and gp is not None:           # geo anchor on the broad-reach channel
            pm.Potential("geo", pm.logp(pm.Normal.dist(gp["mean"], gp["sd"]),
                                        m[f"mroas_{gp['channel']}"]))
        # NB dispersion must be free to go LARGE (low over-dispersion): a too-tight prior here forces the
        # model to assume more count noise than exists, inflating every interval -> over-coverage.
        alpha_nb = pm.HalfNormal("alpha_nb", 1000.0)
        pm.NegativeBinomial("obs", mu=pt.maximum(mu, 1e-3), alpha=alpha_nb, observed=y)
        idata = pm.sample(random_seed=seed, **nuts)
    return idata


def mroas_posterior(idata) -> pd.DataFrame:
    """Per-channel mROAS posterior summary: median (the point estimate — robust to the right skew of the
    exp() response) + mean + 80% CI (the interval the study scores for coverage)."""
    post = idata.posterior
    rows = {}
    for c in CHANNELS:
        s = post[f"mroas_{c}"].values.ravel()
        rows[c] = dict(med=float(np.median(s)), mean=float(s.mean()),
                       lo=float(np.quantile(s, 0.10)), hi=float(np.quantile(s, 0.90)))
    return pd.DataFrame(rows).T


# --- scoring + the Monte-Carlo loop --------------------------------------------------------------
def _estimand_rhat(idata) -> float:
    """Max R-hat over the *estimand* params only (the mROAS deterministics + kappa) — not the per-release
    nuisance z's, which mix slowly without invalidating the channel-level answer (REPLICATE's gate)."""
    import arviz as az
    names = [f"mroas_{c}" for c in CHANNELS] + ["kappa"]
    sub = idata.posterior[names]
    return float(az.rhat(sub).to_array().max())


def score_fit(idata, truth: dict) -> dict:
    """Score one fit against planted truth: per-channel rel bias + 80%-CI coverage + keep/cut accuracy,
    plus kappa detection (does the 80% CI clear the +/- ROPE band around 0)."""
    post = mroas_posterior(idata)
    rel_bias, covered, correct = {}, {}, {}
    for c in CHANNELS:
        t = truth["mroas"][c]; m = post.loc[c]
        rel_bias[c] = (m["med"] - t) / t
        covered[c] = bool(m["lo"] <= t <= m["hi"])
        correct[c] = bool((m["med"] >= BREAKEVEN) == truth["keep"][c])
    k = idata.posterior["kappa"].values.ravel()
    klo, khi = np.quantile(k, 0.10), np.quantile(k, 0.90)
    kappa_detected = bool(klo > KAPPA_ROPE or khi < -KAPPA_ROPE)
    return dict(
        rel_bias=rel_bias, covered=covered, correct=correct,
        median_abs_rel_bias=float(np.median([abs(v) for v in rel_bias.values()])),
        coverage=float(np.mean(list(covered.values()))),
        class_accuracy=float(np.mean(list(correct.values()))),
        kappa_detected=kappa_detected,
        mroas=post["mean"].to_dict(),
    )


def run_cell(scn: Scenario, M: int, estimators=("nopool", "pooled", "pooled_geo"),
             nuts: dict | None = None, conv_rhat: float = 1.05, conv_div: float = 0.03, seed0: int = 0):
    """Run M simulations of one scenario; fit each estimator on the *same* roster (paired), drop sims that
    fail the convergence gate, and aggregate the survivors. Returns ``{estimator: aggregate dict}`` plus a
    ``_meta`` block. This is the unit Ch7 sweeps across the grid."""
    acc = {e: [] for e in estimators}
    attempted = {e: 0 for e in estimators}
    for j in range(M):
        seed = seed0 + j
        data, truth = simulate_roster(scn, seed=seed)
        gp = geo_prior(data, truth, seed=seed) if scn.geo_anchor else None
        for e in estimators:
            attempted[e] += 1
            try:
                idata = fit_mmm(data, truth, estimator=e, gp=gp, nuts=nuts, seed=seed)
                rhat = _estimand_rhat(idata)
                div = float(idata.sample_stats.diverging.values.mean())
                if rhat <= conv_rhat and div <= conv_div:
                    s = score_fit(idata, truth); s["_truth"] = truth["mroas"]
                    acc[e].append(s)
            except Exception:                                  # a single bad fit shouldn't sink the cell
                continue

    out = {"_meta": {"scenario": scn.label(), "M": M}}
    for e in estimators:
        S = acc[e]
        if not S:
            out[e] = {"n_sims": 0}; continue
        rmse = float(np.sqrt(np.mean([(s["mroas"][c] - s["_truth"][c]) ** 2
                                      for s in S for c in CHANNELS])))
        out[e] = dict(
            n_sims=len(S),
            median_abs_rel_bias=float(np.median([s["median_abs_rel_bias"] for s in S])),
            coverage=float(np.mean([s["coverage"] for s in S])),
            class_accuracy=float(np.mean([s["class_accuracy"] for s in S])),
            kappa_detected_frac=float(np.mean([s["kappa_detected"] for s in S])),
            mroas_rmse=rmse,
            channels={c: float(np.median([s["rel_bias"][c] for s in S])) for c in CHANNELS},
            convergence=dict(n_converged=len(S), n_attempted=attempted[e],
                             frac_dropped=1 - len(S) / max(attempted[e], 1)),
        )
    return out


def conclude(go_cell: dict, null_cell: dict | None = None,
             primary: str = "pooled_geo", baseline: str = "nopool") -> dict:
    """Apply the H1-H5 ledger to a GO cell (+ optional kappa=0 null cell) and emit GO / RESCOPE / KILL.
    The **decision** is what matters: keep/cut accuracy (H3) is the gate. KILL only if the platform can't
    even call which channels to fund (H3 fails); if it *can* but magnitudes/intervals are imperfect
    (H1/H2/etc fail), that's a RESCOPE ("trust the decision, caveat the magnitudes"); all pass -> GO."""
    p = go_cell[primary]
    led = {}
    led["H1 rel-bias"] = dict(pass_=p["median_abs_rel_bias"] < REL_BIAS_GO,
                              detail=f"median |rel bias| {p['median_abs_rel_bias']:.2f} (< {REL_BIAS_GO})")
    led["H2 coverage"] = dict(pass_=COVERAGE_LO <= p["coverage"] <= COVERAGE_HI,
                              detail=f"80% coverage {p['coverage']:.2f} (in {COVERAGE_LO}-{COVERAGE_HI})")
    led["H3 keep/cut"] = dict(pass_=p["class_accuracy"] >= CLASS_ACCURACY_GO,
                              detail=f"keep/cut acc {p['class_accuracy']:.2f} (>= {CLASS_ACCURACY_GO})")
    if null_cell is not None:
        fp = null_cell[primary]["kappa_detected_frac"]
        led["H4 kappa null"] = dict(pass_=fp <= KAPPA_FP_MAX,
                                    detail=f"kappa false-positive {fp:.2f} (<= {KAPPA_FP_MAX})")
    if baseline in go_cell and go_cell[baseline].get("n_sims", 0):
        red = 1 - p["mroas_rmse"] / go_cell[baseline]["mroas_rmse"]
        led["H5 pooling"] = dict(pass_=red >= POOLING_RMSE_GO,
                                 detail=f"pooling cuts mROAS RMSE {red:.0%} vs {baseline} (>= {POOLING_RMSE_GO:.0%})")
    decision_ok = led["H3 keep/cut"]["pass_"]              # can we even call which channels to fund?
    all_ok = all(v["pass_"] for v in led.values())
    verdict = "GO" if all_ok else ("RESCOPE" if decision_ok else "KILL")
    return {"verdict": verdict, "ledger": led, "primary": primary}


# --- the scarcity grid ---------------------------------------------------------------------------
def verdict_grid() -> list:
    """The Ch7 grid: a favorable GO baseline + one-knob-at-a-time degradations along each scarcity axis
    (releases, collinearity, geo, endogeneity). Each cell is labelled with the axis it stresses so the
    notebook can plot recovery vs the dial. The kappa=0 null is run separately (false-positive control)."""
    base = dict(N=60, rho=0.4, kappa=0.8, gamma=0.5, geo_anchor=True)
    cells = [
        ("baseline (favorable)", "—",            Scenario(**base)),
        ("releases N=40",        "data poverty", Scenario(**{**base, "N": 40})),
        ("releases N=24",        "data poverty", Scenario(**{**base, "N": 24})),
        ("collinearity ρ=0.7",   "collinearity", Scenario(**{**base, "rho": 0.7})),
        ("collinearity ρ=0.9",   "collinearity", Scenario(**{**base, "rho": 0.9})),
        ("no geo anchor",        "no experiment", Scenario(**{**base, "geo_anchor": False})),
        ("endogeneity γ=1.2",    "endogeneity",  Scenario(**{**base, "gamma": 1.2})),
        ("realistic (N=30, no geo)", "compounded", Scenario(N=30, rho=0.6, kappa=0.8, gamma=0.8, geo_anchor=False)),
        ("worst case (few+collinear+no geo)", "compounded",
         Scenario(N=18, rho=0.85, kappa=0.8, gamma=1.0, geo_anchor=False)),
    ]
    return cells


GO_BASELINE = Scenario(N=60, rho=0.4, kappa=0.8, gamma=0.5, geo_anchor=True)


if __name__ == "__main__":   # smoke: does the DGP plant a clean, recoverable, correctly-split truth?
    scn = Scenario()
    data, truth = simulate_roster(scn, seed=0)
    print("scenario:", truth["scenario"], "| rows:", len(data), "| releases:", scn.N)
    print("\nplanted channel mROAS (realized) and keep/cut vs EUR", BREAKEVEN, "bar:")
    for c in CHANNELS:
        flag = "KEEP" if truth["keep"][c] else "cut "
        print(f"  {c:8s} target {MROAS[c]:5.1f}  realized {truth['mroas'][c]:6.2f}  -> {flag}"
              f"   spend share {truth['spend'][c]/sum(truth['spend'].values()):.0%}")
    nv = naive_roas(data)
    print("\nnaive pooled-OLS mROAS (the straw man) vs truth:")
    for c in CHANNELS:
        print(f"  {c:8s} naive {nv[c]:7.2f}   truth {truth['mroas'][c]:6.2f}   "
              f"bias {nv[c]-truth['mroas'][c]:+7.2f}")
