# PILOT run — B1 benchmark on open-weight qwen3:8b (n=1, CPU)

*2026-06-11/12 · qwen3:8b via local Ollama (v0.30.7), thinking disabled,
CPU-only (62 GB RAM, no usable GPU). Same protocol and judge as the
claude-opus-4.8 pilot (self-judged by the ground-truth author — PILOT only).*

## Results — and comparison across model tiers

| Metric | lint only | qwen3:8b bare | **qwen3:8b guided** | Opus 4.8 bare | Opus 4.8 guided |
|---|---|---|---|---|---|
| Recall (24 flaws) | 0.21 | 0.29 | **0.71** | 0.83 | 0.92 |
| Weighted recall | 0.14 | 0.28 | **0.69** | 0.83 | 0.91 |
| Critical-flaw recall | 1/10 | 2/10 | **7/10** | 8/10 | 9/10 |
| Semantic-flaw recall | 1/19 | 6/19 | **12/19** | 16/19 | 17/19 |
| Precision | 0.42 | 0.87 | 0.85 | 1.0 | 1.0 |
| Wall time (CPU) | seconds | 11 min | 2 h 44 min | — | — |

**Headline: the guideline system lifts the small model from 0.28 to 0.69
weighted recall (+0.41) — five times the uplift it gives the frontier model
(+0.08).** The scaffold substitutes for model capability: guided qwen3:8b
catches the V&V confusion, the missing novelty paragraph, the failed-attempts
narrative, the linear-scale convergence plot, the indistinguishable curves,
and the incidental-parameter inconsistency — all of which bare qwen3:8b
missed entirely.

## Failure modes observed (as important as the scores)

1. **Reasoning-mode token burn.** With thinking enabled, qwen3:8b spent the
   entire completion budget on `<think>` and returned nothing (38 min wasted).
   Thinking must be disabled for this workload on CPU (`think: false` native
   parameter or `/no_think` soft switch).
2. **Constrained-JSON looping on the MA category.** In structured-output
   mode the model looped to 13.7k tokens on the mathematics category —
   twice, reproducibly. The first time this *crashed the whole pipeline
   after 2 h 11 min*; the per-category fault isolation added in response
   turned it into a clean "Not checked: all MA rules" entry. Cost: GT-06,
   GT-09, GT-24 (all in MA) became unreachable — with a working MA pass,
   guided recall would plausibly reach ~20/24.
   Known issue: the SWA_MAX_TOKENS cap did not propagate through the
   LangChain structured-output path; the cap must be enforced server-side
   (ollama `num_predict`) until fixed.
3. **Honest non-claims work.** The guided model correctly reported FG-1/4/5
   as not checkable (figures not provided) instead of hallucinating figure
   judgements — the protocol's honesty instructions are followed even by an
   8B model.
4. **Bare-condition redundancy.** Bare qwen3:8b produced 8 verbatim duplicate
   findings in 31; the guided pipeline's per-category structure eliminated
   mass duplication (and its findings carry rule IDs).

## Practical takeaway for the group

- CPU-only 8B: **works, but overnight-batch territory** (~3 h/manuscript).
- The economics: the catalogue's value is largest exactly where inference is
  free (small/local/Blablador models) — guided-small ≈ between bare-small
  and bare-frontier at zero cost.
- Next: same conditions on a ~70B model (Blablador) to locate the
  quality/cost sweet spot, and n≥3 repetitions + independent judging before
  citing any of these numbers outside the group.
