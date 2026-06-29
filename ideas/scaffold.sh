#!/usr/bin/env bash
# scaffold.sh — create every chapter file referenced in _quarto.yml as a stub.
# Idempotent: never overwrites an existing file. Run from the book root:
#   bash scaffold.sh && quarto render
set -euo pipefail

# path|Human Title
chapters=(
"00-foundational/01-experimentation-mindset.qmd|The Experimentation Mindset"
"00-foundational/02-potential-outcomes.qmd|Potential Outcomes & the Assignment Mechanism"
"00-foundational/03-estimands.qmd|Estimands: ATE, ATT, CATE, LATE, Policy Value"
"00-foundational/04-randomization-and-identification.qmd|Randomization as Identification"
"00-foundational/05-statistics-review.qmd|Statistics Review (skip if fluent)"
"00-foundational/06-frequentist-vs-bayesian.qmd|Frequentist vs Bayesian: Interpreting Intervals"
"00-foundational/07-anatomy-of-a-platform.qmd|Anatomy of an Experimentation Platform"
"05-power-and-decisions/01-ate-three-ways.qmd|Estimating the ATE Three Ways: Difference, OLS, Doubly-Robust"
"05-power-and-decisions/02-variance-reduction.qmd|Variance Reduction: CUPED, CUPAC, MLRATE"
"05-power-and-decisions/03-ratio-metrics-and-delta.qmd|Ratio Metrics & the Delta Method"
"05-power-and-decisions/04-cluster-robust-inference.qmd|Cluster-Robust Inference"
"05-power-and-decisions/05-power-and-mde.qmd|Power, Sample Size & MDE"
"05-power-and-decisions/06-decision-framework.qmd|The Ship / No-Ship Decision Framework"
"12-trustworthy-and-metrics/01-srm-and-diagnostics.qmd|Sample-Ratio Mismatch & Diagnostics"
"12-trustworthy-and-metrics/02-aa-testing.qmd|A/A Testing"
"12-trustworthy-and-metrics/03-multiple-comparisons.qmd|Multiple Comparisons"
"12-trustworthy-and-metrics/04-metric-design-and-governance.qmd|Metric Design & Governance"
"12-trustworthy-and-metrics/05-novelty-and-primacy.qmd|Novelty & Primacy Effects"
"12-trustworthy-and-metrics/06-winners-curse.qmd|The Winner's Curse & Early-Stopping Shrinkage"
"04-sequential-anytime-valid/01-the-peeking-problem.qmd|The Peeking Problem"
"04-sequential-anytime-valid/02-group-sequential.qmd|Group-Sequential Testing & Alpha-Spending"
"04-sequential-anytime-valid/03-msprt.qmd|mSPRT"
"04-sequential-anytime-valid/04-confidence-sequences.qmd|Confidence Sequences (Always-Valid Inference)"
"04-sequential-anytime-valid/05-e-values-and-betting.qmd|E-Values & Testing by Betting"
"04-sequential-anytime-valid/06-bayesian-ab.qmd|Bayesian A/B Testing"
"01-causal-ml-dml/01-unconfoundedness.qmd|Unconfoundedness & Selection on Observables"
"01-causal-ml-dml/02-ipw-and-overlap.qmd|IPW & Overlap"
"01-causal-ml-dml/03-aipw-and-tmle.qmd|Doubly-Robust Estimation: AIPW & TMLE"
"01-causal-ml-dml/04-double-machine-learning.qmd|Double/Debiased Machine Learning"
"11-hte-metalearners-forests/01-cate-estimands.qmd|CATE Estimands & What Heterogeneity Means"
"11-hte-metalearners-forests/02-meta-learners.qmd|Meta-Learners: S, T, X, R, DR, U"
"11-hte-metalearners-forests/03-causal-forests-grf.qmd|Causal Forests & GRF"
"11-hte-metalearners-forests/04-dml-for-cate.qmd|DML for CATE (the R-Learner)"
"11-hte-metalearners-forests/05-bayesian-causal-forests.qmd|Bayesian Causal Forests"
"11-hte-metalearners-forests/06-uplift-trees-and-qini.qmd|Uplift Trees & Qini Forests"
"06-evaluation-and-ranking/01-evaluating-cate.qmd|Evaluating CATE: Qini & AUUC"
"06-evaluation-and-ranking/02-rate-and-calibration.qmd|RATE & CATE Calibration"
"06-evaluation-and-ranking/03-policy-learning.qmd|Policy Learning: Who Do We Actually Treat?"
"06-evaluation-and-ranking/04-interleaving-for-ranking.qmd|Interleaving for Ranking Experiments"
"02-marketplace-interference/01-when-sutva-breaks.qmd|When SUTVA Breaks"
"02-marketplace-interference/02-exposure-mappings.qmd|Exposure Mappings & Partial Interference"
"02-marketplace-interference/03-cluster-randomization.qmd|Graph Cluster Randomization"
"02-marketplace-interference/04-two-sided-randomization.qmd|Two-Sided & Multiple Randomization"
"03-switchback/01-why-switchback.qmd|Why Switchback?"
"03-switchback/02-time-region-design.qmd|Time-Region Design"
"03-switchback/03-carryover-robust-estimation.qmd|Carryover-Robust Estimation"
"03-switchback/04-optimal-switchback-design.qmd|Optimal Switchback Design"
"13-quasi-experimental/01-difference-in-differences.qmd|Difference-in-Differences (the Modern Canon)"
"13-quasi-experimental/02-synthetic-control.qmd|Synthetic Control, SDiD & Matrix Completion"
"13-quasi-experimental/03-causalimpact-bsts.qmd|CausalImpact & BSTS"
"13-quasi-experimental/04-rdd-and-its.qmd|Regression Discontinuity & Interrupted Time Series"
"13-quasi-experimental/05-iv-and-noncompliance.qmd|IV & Noncompliance: LATE / CACE"
"10-incrementality-attribution/01-ghost-ads-and-psa.qmd|Ghost Ads & PSA Holdouts"
"10-incrementality-attribution/02-geo-experiments.qmd|Geo Experiments & Geo-DiD"
"10-incrementality-attribution/03-incrementality-vs-mmm.qmd|Incrementality vs MMM"
"10-incrementality-attribution/04-attribution-models.qmd|Attribution Models vs Causal Attribution"
"07-demand-pricing-and-llm-agents/01-demand-and-elasticity.qmd|Demand Estimation & Elasticity"
"07-demand-pricing-and-llm-agents/02-price-experiments.qmd|Price Experiments"
"07-demand-pricing-and-llm-agents/03-structural-vs-experimental.qmd|Structural vs Experimental"
"07-demand-pricing-and-llm-agents/04-wtp-and-conjoint.qmd|Willingness-to-Pay & Conjoint"
"07-demand-pricing-and-llm-agents/05-llm-synthetic-respondents.qmd|LLM-as-Synthetic-Respondent (and Where It Breaks)"
"09-long-term-and-surrogates/01-short-vs-long-term.qmd|The Short-vs-Long-Term Tension"
"09-long-term-and-surrogates/02-surrogate-index.qmd|The Surrogate Index"
"09-long-term-and-surrogates/03-downstream-proxy-metrics.qmd|Downstream & Proxy Metrics"
"08-personalization-and-platform-craft/01-contextual-bandits.qmd|Contextual Bandits & Adaptive Experiments"
"08-personalization-and-platform-craft/02-post-adaptive-inference.qmd|Post-Adaptive Inference"
"08-personalization-and-platform-craft/03-building-lyra.qmd|Building Lyra: Assignment, Registry, Event Log"
"08-personalization-and-platform-craft/04-the-estimator-interface.qmd|The Estimator Interface"
"08-personalization-and-platform-craft/05-scorecard-and-decisions.qmd|The Scorecard & Recording Decisions"
"appendices/A-simulation-and-validation-vega.qmd|Appendix A — Simulation & Validation (Vega)"
"appendices/B-notation-and-estimand-glossary.qmd|Appendix B — Notation & Estimand Glossary"
"appendices/C-tooling-and-environment.qmd|Appendix C — Tooling & Environment"
)

created=0; skipped=0
for entry in "${chapters[@]}"; do
  path="${entry%%|*}"
  title="${entry##*|}"
  mkdir -p "$(dirname "$path")"
  if [[ -e "$path" ]]; then
    skipped=$((skipped+1)); continue
  fi
  cat > "$path" <<EOF
---
title: "$title"
---

::: {.callout-note title="The platform problem"}
*What experimentation problem does this chapter solve? State it in one or two
sentences before introducing any method.*
:::

## Intuition

## Method

## Implementation

\`\`\`{python}
# Python by default. For an R chapter, add \`engine: knitr\` to the YAML above
# and use \`\`\`{r} blocks instead.
\`\`\`

## Validate against ground truth (Vega)

*Recover a known effect from a simulated DGP. Report bias, RMSE, and CI
coverage. This is the section that makes the chapter trustworthy — and doubles
as a test for the platform.*

\`\`\`{python}
# from vega import DGP            # set a known true effect
# from lyra.estimators import ... # estimate it
# assert covers(true_effect, ci)
\`\`\`

## Further reading

*Pull anchors from the paper-library; cite with [@key].*
EOF
  created=$((created+1))
done

echo "Scaffold complete: $created created, $skipped already existed."
echo "Next: quarto render"
