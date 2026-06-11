# PILOT run — B1 planted-flaw benchmark (n=1)

*2026-06-11 · Conditions A/B model: Claude Opus 4.8 (Claude Code subagents,
same model, same day). Condition C: no LLM.*

**PILOT caveats (read before citing numbers):** single repetition (no
stability estimate); findings→flaw matching judged by the ground-truth author
(self-judging — independent judging required for citable results); conditions
A and B ran as Claude Code subagents rather than the LangGraph pipeline.

## Results

| Metric | C — lint only | B — off-the-shelf | A — guided (lint + guidelines) |
|---|---|---|---|
| Recall (24 flaws) | 5/24 = **0.21** | 20/24 = **0.83** | 22/24 = **0.92** |
| Weighted recall (crit=4, maj=2, min=1) | 0.14 | 0.83 | **0.91** |
| Critical-flaw recall | 1/10 | 8/10 | **9/10** |
| Semantic-flaw recall | 1/19 | 16/19 | **17/19** |
| Deterministic-flaw recall | 4/5 | 4/5 | **5/5** |
| Precision | 0.42¹ | 1.0 | 1.0 |
| Findings traceable to versioned rules | — | no | **yes (rule IDs)** |
| Subagent tokens | 0 | 18.5k | 39.7k |

¹ C's "imprecision" is by design: 7 of its 12 findings are *candidate*
findings awaiting semantic confirmation (and several flagged genuine issues
not in the planted set).

## What each condition missed

- **B (off-the-shelf)** missed: **GT-10 — the verification/validation
  confusion (critical)**, GT-02 (abstract too technical for non-specialists),
  GT-17 ("in order to"), GT-21 (tense mixing). The V&V miss is the
  signature result: a *field-convention* rule that generic competence does
  not reliably enforce — exactly the knowledge the catalogue encodes.
- **A (guided)** missed: GT-20 (future-work laundry list — SL-1 applied to
  the conclusion), GT-24 (secondary undefined symbols ℓ, c_d). Both are
  rule-application gaps, not rule gaps; worth re-testing across repetitions.
- **C** found 4/5 deterministic + ST-2 (structural heuristic) — the free,
  reproducible floor.

## Side findings (the eval audited the system itself)

1. The LG-4 deterministic check ignored `\title{…}` — fixed in this commit
   (now fires on the eval manuscript's Title Case).
2. Condition B found several genuine non-planted flaws (missing citations,
   no constitutive model, static-load example with an explicit dynamic
   integrator). These were judged valid, and the GT manifest should grow by
   the reproducible ones in a revision (GT must stay the union of all
   *agreed* flaws, versioned like the guidelines).

## Interpretation (pilot-level only)

With a frontier model, the guideline system added +0.08 weighted recall and,
more importantly, caught the remaining **critical** field-convention flaw and
made every finding auditable against a versioned rule. The bare frontier
model is already a strong reviewer — the interesting open question is the
gap on small open-weight models (8B-class), where generic review competence
is much weaker and the guideline scaffold should carry proportionally more.
That is the next experiment (Ollama conditions).

## Files

- `matches_cond{A,B,C}.json` — judged matchings (input to `../../score.py`)
- `raw_condA.json`, `raw_condB.json` — verbatim agent outputs
- `raw_condC.txt` — lint output
