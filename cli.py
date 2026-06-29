"""Vega CLI — reproducible by command (CLAUDE.md).

A single entrypoint to run a full experiment end to end. Subcommands:

    python -m cli run        # engine: simulate, emit events/ from config.yaml + seed
    python -m cli metrics    # dbt: build staging → intermediate → marts over the event log
    python -m cli infer      # run inference.estimators, write readouts
    python -m cli validate   # validation/criteo.py real-data leg
    python -m cli all        # run → metrics → infer (the full pipeline)

Everything is driven by config.yaml; nothing here hardcodes run parameters.
"""

from __future__ import annotations

import argparse
import json


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="vega", description="Vega marketplace experimentation lab")
    p.add_argument("--config", default="config.yaml", help="path to run config")
    sub = p.add_subparsers(dest="command", required=True)
    for name, help_ in [
        ("run", "simulate and emit the event log"),
        ("metrics", "build the dbt metrics layer over the event log"),
        ("infer", "run the inference estimators"),
        ("validate", "run the real-data (Criteo) validation leg"),
        ("all", "run -> metrics -> infer"),
    ]:
        sp = sub.add_parser(name, help=help_)
        if name == "run":
            sp.add_argument("--quiet", action="store_true", help="suppress per-day progress")
    return p


def _cmd_run(args) -> int:
    from engine.config import load_config
    from engine.market import run

    cfg = load_config(args.config)
    print(f"vega run | {cfg.meta.run_name} | seed={cfg.seed} | horizon={cfg.meta.horizon_days}d "
          f"| users={cfg.market.n_users_initial} | mode={cfg.mode}")
    summary = run(cfg, verbose=not args.quiet)

    print("\n-- summary -------------------------------------------")
    print(f"events written : {summary['n_events']:,}  ->  {cfg.output.event_log_dir}")
    print(f"event types    : {summary['type_counts']}")
    m = summary["metrics"]
    print(f"conversions    : {m['conversions']:,}")
    print(f"margin/active-user-day : {m['margin_per_active_user_day']:.4f}")
    cal = summary["calibration"]
    print(f"conv/day       : first={cal['conv_first_day']:,}  last={cal['conv_last_day']:,}")
    print(f"active/day      : first={cal['active_first_day']:,}  last={cal['active_last_day']:,}")
    print(f"calibration ok : {cal['ok']}" + ("" if cal["ok"] else f"  {cal['warnings']}"))
    print("SRM (A/A hard-checked; ramped informational):")
    for exp, r in sorted(summary["srm"].items()):
        tag = "ramp" if r.get("ramped") else ("OK " if r["ok"] else "FLAG")
        print(f"  [{tag:>4}] {exp:<20} realized={r['realized_share']:.3f} "
              f"intended={r['intended_share']:.3f} (t={r['treatment']}, c={r['control']}, "
              f"h={r['holdout']})")
    return 0


def _cmd_infer(args) -> int:
    from engine.config import load_config
    from inference import anytime_valid, cluster, incrementality, naive

    cfg = load_config(args.config)
    inc_target = None
    _inc = cfg.experiments.get("incrementality", {})
    if _inc and _inc.get("enabled"):
        inc_target = str(_inc.get("target_experiment"))
    events_dir = str(cfg.output.event_log_dir)
    alpha = float(cfg.inference.alpha)
    print(f"vega infer | events={events_dir} | alpha={alpha}\n")
    print(f"{'experiment':<20} {'estimator':<10} {'effect':>10} {'95% CI':>22} {'p':>9}  flags")
    print("-" * 86)
    for e in cfg.experiments.list:
        exp_id = str(e.id)
        ramped = bool(e.get("uses_ramp", False))
        flag = "RAMPED: cohort-confounded" if ramped else ""
        try:
            eff = naive.estimate_from_log(events_dir, exp_id, alpha)
            print(f"{exp_id:<20} {'naive':<10} {eff.point:>+10.5f} "
                  f"[{eff.ci_low:>+8.5f},{eff.ci_high:>+8.5f}] {eff.p_value:>9.2e}  {flag}")
            if str(e.randomization) == "cluster":
                ec = cluster.estimate_from_log(events_dir, exp_id, alpha)
                print(f"{'':<20} {'cluster':<10} {ec.point:>+10.5f} "
                      f"[{ec.ci_low:>+8.5f},{ec.ci_high:>+8.5f}] {ec.p_value:>9.2e}")
            av = anytime_valid.estimate_from_log(events_dir, exp_id, alpha)
            print(f"{'':<20} {'anytime-CS':<10} {av.point:>+10.5f} "
                  f"[{av.ci_low:>+8.5f},{av.ci_high:>+8.5f}] {'':>9}  always-valid")
            if exp_id == inc_target:
                inc = incrementality.estimate_from_log(events_dir, exp_id, alpha)
                print(f"{'':<20} {'incr(t-h)':<10} {inc.point:>+10.5f} "
                      f"[{inc.ci_low:>+8.5f},{inc.ci_high:>+8.5f}] {inc.p_value:>9.2e}  ghost-ads lift")
        except Exception as exc:  # noqa: BLE001
            print(f"{exp_id:<20} {'—':<10} (skipped: {exc})")
    print(
        "\nNotes:\n"
        "  • 'real' mode — no ground truth in the log; the recovery/bias TESTS assert the naive\n"
        "    estimate's bias against the shadow-run ATE at FIXED allocation (run `make test`).\n"
        "  • RAMPED experiments carry an assignment-cohort selection confound (monotone ramp +\n"
        "    churn ⇒ 'treatment' over-represents long-survivors). The rigorous money-shot is the\n"
        "    fixed-allocation comparison; the constant-allocation A/A nulls above are unconfounded\n"
        "    and correctly do not flag. See pm/DECISIONS.md D-13."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    import sys
    try:  # Windows consoles default to cp1252; make our output utf-8-safe.
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = build_parser().parse_args(argv)
    if args.command == "run":
        return _cmd_run(args)
    if args.command == "infer":
        return _cmd_infer(args)
    if args.command == "metrics":
        return _cmd_metrics(args)
    raise SystemExit(f"`{args.command}` not implemented yet — see pm/PROGRESS.md (T-17..)")


def _cmd_metrics(args) -> int:
    """Build the dbt metrics layer over the event log (staging → intermediate → marts + tests)."""
    import subprocess

    print("vega metrics | dbt build over events/ (DuckDB)\n")
    proc = subprocess.run(
        ["dbt", "build", "--profiles-dir", "."], cwd="metrics", text=True
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
