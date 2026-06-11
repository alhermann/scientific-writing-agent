# Evaluation: does the guideline-driven agent beat off-the-shelf review?

Rigorous benchmark suite for the manuscript-review system. The question every
result must answer: **how much does the guideline system add over the same
model without it?**

## Benchmarks

### B1 — Planted-flaw detection (synthetic, exact ground truth)

`data/eval_manuscript.tex` is a realistic 2-page computational-mechanics
manuscript with **24 planted flaws** (`data/ground_truth.json`): 5
deterministic (regex-detectable) and 19 semantic (requiring judgement),
spanning 9 critical / 10 major / 5 minor.

The manuscript contains **no annotations** — it must never leak the answers.
It was constructed *after* the guideline catalogue and instantiates its
rules; B1 therefore measures **rule enforcement**, not generalization to
unseen flaw types (that is B2's job).

### B2 — Real-feedback coverage (gold = human feedback)

For a real manuscript where supervisor/reviewer feedback exists: give the
agent the *pre-feedback* version and measure which fraction of the actual
human feedback items it anticipates. This is the metric that matters
operationally: **% of human feedback that would have been unnecessary.**
Requires private data → results stay internal; protocol is identical to B1
with the human feedback items as the flaw manifest.

### B3 — Distillation quality

Feed the system k feedback items whose "correct" abstraction is known
(e.g., the worked example in `docs/distillation-example.md`). Score each
produced proposal on a 1–5 rubric: abstraction (no manuscript specifics),
operationality (executable how-to-check), correct classification
(new vs. existing rule vs. drop), format compliance. Judged by a panel of
3 LLM judges + human spot-check.

## Conditions

| | Condition | What it isolates |
|---|---|---|
| A | **Full system**: deterministic lint + guidelines-guided LLM review (skill / `swa review`) | the whole product |
| B | **Off-the-shelf**: same model, prompt "review this manuscript and list all problems", no guidelines, no tools | the baseline |
| C | **Deterministic only**: `swa lint` + `swa bib` | the free, reproducible floor |
| D | **Ablation**: same model + raw unstructured checklist text in the prompt | structure/protocol contribution vs. mere guideline text |

Same model in A, B, D. Repeat across model tiers (frontier API model,
open-weight ~8B, open-weight ~70B) to measure how much model quality the
guideline scaffold can substitute for.

## Metrics

For each condition, after judge matching (below):

- **Recall** = matched flaws / 24 — overall, and broken down **by severity**,
  **by check type** (deterministic vs. semantic), **by category**.
- **Weighted recall** — severity weights critical=4, major=2, minor=1
  (a system that finds only typos must not look good).
- **Precision** = valid findings / total findings, where a finding is valid
  if it matches a planted flaw OR a judge panel deems it a genuine issue
  (planting flaws does not make the rest of the text perfect).
- **F1 (weighted)** on the planted set.
- **Localization accuracy** — fraction of matched flaws with correct
  section/line.
- **Stability** — mean pairwise Jaccard similarity of matched-flaw sets
  across n≥3 repetitions (a review tool must not be a dice roll).
- **Cost & latency** per review (tokens, seconds).

### Matching protocol (findings → flaws)

A finding matches a flaw iff it identifies the *same defect* at the *same
location* — wording and cited rule are irrelevant. Matching is done by an
LLM judge prompted with `ground_truth.json` (`match_hints` included), then
human-verified for every disputed pair. Report judge–human agreement
(Cohen's κ); if κ < 0.8, all matchings are human-redone. The judge model
must differ from the reviewed model where possible.

### Honesty rules for reporting

- Always report **all** conditions, including when B beats A.
- Report per-check-type recall separately — deterministic flaws are "free"
  for condition A (the linter hands them over) and must not inflate the
  semantic comparison.
- n≥3 repetitions; report mean ± sd. Pilot runs with n=1 must be labeled
  PILOT.

## Running

```bash
# Condition C (deterministic floor) — fully reproducible
PYTHONPATH=src python3 -m swa.cli lint evals/data/eval_manuscript.tex

# Condition A via the LangGraph agent
SWA_MODEL=... swa review evals/data/eval_manuscript.tex --out /tmp/condA.md

# Scoring (after judge matching produces a matches file)
python3 evals/score.py evals/results/<run>/matches_condA.json
```

Results live in `evals/results/<date>-<model>/`, one directory per run, with
raw outputs, the matching file, and the score table.
