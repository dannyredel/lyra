"""The scorecard (LYRA §7-8) — a **pure function of statistical state**.

Runs the experiment's typed estimator (`lyra/metrics` or `lyra/se`) over its Vega/DGP event source and
returns a state-gated readout: the **CI-colored-bar** rule (green/red/grey by sign), the Etsy
state→message vocabulary, the **SRM** gate, power, an accrual **timeseries** (narrowing band), and —
Lyra's superpower — the **ground-truth "certified" badge** (the Monte-Carlo harness coverage vs the known
truth). Steal: Etsy scorecard semantics; eBay SRM; the "never show a verdict on an underpowered test" rule.
"""

from __future__ import annotations

import numpy as np

from chassis.assignment import srm_chi2
from lyra.harness import harness


def _control_baseline(df, exp) -> float:
    c = df[df.treat == 0]
    if {"conversions", "sessions"} <= set(df.columns):
        return float(c.conversions.sum() / c.sessions.sum())
    if "y" in df.columns:
        return float(c.y.mean())
    return float("nan")


def compute(exp, dgp, estimator, required_n_total: int, *, harness_R: int = 120, seed0: int = 1000) -> dict:
    """Full scorecard dict for one experiment backed by ``dgp`` + ``estimator`` (both from lyra)."""
    truth = float(dgp.ground_truth().ate)
    npd, days = exp.n_per_day, exp.days

    # accrual timeseries — estimate the effect each "day" as data accumulates (the band narrows)
    ts = []; last_res = None
    for d in range(1, days + 1):
        df_d = dgp.sample(d * npd, seed=seed0 + d)
        res = estimator.estimate(df_d); last_res = res
        lo, hi = res.ci
        ts.append({"day": d, "point": float(res.point), "ci_low": float(lo), "ci_high": float(hi),
                   "se": float(res.se or 0.0), "n": int(len(df_d))})
    last = ts[-1]
    point, lo, hi, se = last["point"], last["ci_low"], last["ci_high"], last["se"]
    n_total = days * npd

    df = dgp.sample(n_total, seed=seed0 + days)
    base = _control_baseline(df, exp)
    # show a relative % only with a meaningful positive baseline (absolute for cluster / interference metrics,
    # so the naive vs cluster marketplace readouts are directly comparable)
    use_pct = bool(np.isfinite(base) and base > 0.02 and exp.design != "cluster"
                   and not exp.world.get("interference"))
    rel = point / base if use_pct else point

    # SRM gate (assignment balance)
    counts = {"control": int((df.treat == 0).sum()), "treatment": int((df.treat == 1).sum())}
    srm_chi, srm_p = srm_chi2(counts, exp.allocations)

    # the CI-colored-bar + Etsy state→message vocabulary (a pure function of statistical state)
    spans0 = lo <= 0 <= hi
    powered = n_total >= required_n_total
    if (not powered) and n_total < 0.5 * required_n_total:
        state, headline, color = "collecting", "Collecting data", "grey"
    elif spans0:
        state, headline, color = "no_change", "No detectable change", "grey"
    else:
        sign = "+" if point > 0 else "−"
        mag = f"{abs(rel) * 100:.1f}%" if use_pct else f"{abs(point):.3f}"
        state, headline, color = "change", f"{sign}{mag}", ("green" if point > 0 else "red")

    # CROSS-CUTTING LAYER (NB 07): an always-valid confidence sequence + advisory stop on EVERY experiment
    from lyra.sequential import advisory, confidence_sequence
    ts = confidence_sequence(ts)                 # adds peek-safe cs_low/cs_high to each look
    seq_advisory = advisory(ts, powered=powered)

    # the superpower: certify the readout against the known truth via the Monte-Carlo harness
    rep = harness(estimator, dgp, R=harness_R, n=min(20_000, n_total), return_draws=True)
    certified = rep["coverage"] >= 0.88          # floor for the badge (nominal 0.95, robust to MC noise)
    is_aa = abs(truth) < 1e-9

    # detailed analytics (the "see more" view): the MC sampling distribution, coverage, per-arm outcomes
    d = rep["draws"]
    yc = df.loc[df.treat == 0, "y"].to_numpy(float); yt = df.loc[df.treat == 1, "y"].to_numpy(float)
    allv = np.concatenate([yc, yt]); nb = 2 if np.unique(allv).size <= 2 else 24
    edges = np.histogram_bin_edges(allv, bins=nb)
    hc, _ = np.histogram(yc, bins=edges); ht, _ = np.histogram(yt, bins=edges)
    analytics = {
        "sampling": [round(p, 6) for p in d["points"]], "truth": truth, "coverage": rep["coverage"],
        "intervals": [[round(a, 6), round(b, 6), cov] for a, b, cov in zip(d["lo"], d["hi"], d["covers"])][:50],
        "arm_hist": {"edges": [round(float(e), 5) for e in edges], "control": hc.tolist(),
                     "treatment": ht.tolist(), "control_mean": float(yc.mean()), "treatment_mean": float(yt.mean())},
    }

    # CROSS-CUTTING LAYER (NB 08): the ship rule — OEC superiority ∧ guardrails non-inferior ∧ certified
    from lyra.decisions import ship_decision
    decision_rec = ship_decision(
        {"effect": point, "ci_low": lo, "ci_high": hi, "direction": exp.metric.get("direction", "up")},
        exp.guardrail_readouts)
    if decision_rec["ship"] and not certified:   # never ship an estimate the platform can't certify
        decision_rec = {**decision_rec, "ship": False, "blocked_by_certification": True,
                        "reason": "design not certified — the estimate may be biased (see Validation)"}

    return {
        "id": exp.id, "name": exp.name, "owner": exp.owner, "state": exp.state,
        "hypothesis": exp.hypothesis, "design": exp.design,
        "metric": exp.metric,
        "readout": {
            "point": point, "ci_low": lo, "ci_high": hi, "se": se,
            "headline": headline, "headline_state": state, "ci_color": color,
            "relative_pct": float(rel * 100) if use_pct else None, "is_pct": bool(use_pct),
            "p_value": float(last_res.p_value),
            "cs_low": float(ts[-1]["cs_low"]), "cs_high": float(ts[-1]["cs_high"]),
        },
        "sequential": seq_advisory,
        "truth": {                                   # ← what real platforms can't show
            "value": truth, "covered": bool(lo <= truth <= hi),
            "certified": bool(certified), "coverage_pct": round(100 * rep["coverage"], 1),
            "label": exp.world.get("truth_label", "true effect"),
        },
        "diagnostics": {
            "srm_p": round(srm_p, 3), "srm_ok": bool(srm_p > 0.001),
            "n_control": counts["control"], "n_treatment": counts["treatment"],
            "is_aa": bool(is_aa), "aa_ok": bool(is_aa and spans0),
        },
        "power": {
            "required_n": int(required_n_total), "current_n": int(n_total),
            "pct_powered": round(min(100.0, 100 * n_total / required_n_total), 1) if required_n_total else 100.0,
            "powered": bool(powered),
        },
        "timeseries": ts,
        "analytics": analytics,                  # the "see more" validation view
        "decision": exp.decision,
        "decision_rec": decision_rec,            # the ship recommendation (conjunction rule)
    }
