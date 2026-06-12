# PILOT run — B1 benchmark on qwen3-32b via OpenRouter (n=1)

*2026-06-12 · qwen/qwen3-32b (thinking disabled) via OpenRouter. Same
protocol and judge as the prior pilots (self-judged — PILOT only).*

## Cross-tier comparison (weighted recall, 24 planted flaws, 64 severity points)

| Condition | lint | qwen3:8b | qwen3-32b | Opus 4.8 |
|---|---|---|---|---|
| **B — bare** | — | 0.28 | 0.38 | 0.83 |
| **A — guided** | 0.14 | 0.69 | 0.66 | 0.91 |
| Guideline uplift | — | **+0.41** | **+0.28** | +0.08 |
| A wall time | s | 2h44m (CPU) | **2m24s** | ~17m |
| A precision | 0.42 | 0.85 | 0.74 | 1.0 |

## Interpretation (pilot-level)

1. **The guided conditions of 8B and 32B land in the same band (0.66–0.69)**
   — once the scaffold provides the rules and the protocol, the small-model
   tier matters less than expected for *recall*. The scaffold, not the
   parameter count, carries the review.
2. **Bare capability scales slowly** (0.28 → 0.38 from 8B to 32B): generic
   "review this" competence is not where open-weight gains show up.
3. **Where 32B differs: reliability, speed — and new failure modes.**
   No constrained-JSON looping (MA category succeeded → GT-06 found, which
   8B could not reach), 70× faster than local CPU. But it *hallucinated
   figure-caption findings* (FG-4/5 claims about captions of figures that do
   not exist in the source — while its own not_checked list simultaneously
   and correctly declared figures unavailable). Precision dropped to 0.74,
   the lowest guided value so far.
4. Persistent blind spots across ALL qwen tiers, bare and guided: GT-09
   (δ/ε notation switch — requires cross-section symbol tracking), GT-21
   (tense consistency), GT-22 (abstract↔conclusion contradiction). These
   need whole-document reasoning that small/mid models do not deliver even
   with rules in hand — frontier territory, or candidates for new
   deterministic checks (a symbol-table cross-checker would catch GT-09
   mechanically).

## Consequences

- **Deployment guidance:** guided-32B-class hosted (Blablador) ≈ guided-8B
  recall at 70× speed — the practical free tier for the group. For final
  pre-submission passes, a frontier model remains visibly better
  (0.91 vs 0.66, and no hallucinated findings).
- **System TODO distilled from this run:** (a) add a deterministic
  symbol-consistency check (MA-2/GT-09 class); (b) the review protocol
  should hard-instruct models to skip figure-content rules when no figure
  environments exist (anti-hallucination guard); (c) enforce token caps
  server-side (SWA_MAX_TOKENS does not propagate in structured mode).

## Files

As in the other run directories: `matches_cond{A,B}.json`, `raw_condB.json`,
`raw_condA_report.md`.
