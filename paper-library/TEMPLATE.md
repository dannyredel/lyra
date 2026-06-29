---
title: "<full title>"
authors: "<authors>"
year: <year>
venue: "<journal/conf/blog>"
pdf: ../pdfs/<file>.pdf
tags: [causal-inference, ...]
feeds: [inference/cluster.py, "D-03", "ramp diagnostic"]   # exact modules/decisions this changes
related: [[other-slug]]
status: processed   # to-read | reading | processed
read_on: <YYYY-MM-DD>
---

# <short title>

## One-line claim
> The single sentence the paper exists to prove.

## Why it's in Vega
What part of the build or thesis this informs (point at the LITERATURE.md rationale + the module).

## First-person takeaways
- …what *I* take from it, in my words — not an abstract summary.
- The mechanism / estimator / design rule, stated operationally.
- The failure mode it warns against (and how Vega avoids it).

## How we exploit it (concrete)
- **Module:** `inference/<x>.py` — what to implement.
- **Test:** what the recovery/null test should assert because of this paper.
- **Design/decision:** any DECISIONS.md entry it supports or challenges.

## Numbers worth stealing (calibration)
Effect sizes, elasticities, carryover, coverage rates we can anchor the simulator to.

## Open questions / disagreements
Where it doesn't fit our setting, or where two papers conflict.

## Cross-links
- [[slug]] — how they relate.
