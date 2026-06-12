# Distillation pipeline live test (B3 pilot, n=1)

*2026-06-12 · `swa distill` (LangGraph) with qwen/qwen3-32b via OpenRouter,
synthetic but realistic supervisor feedback (7 items, `input_feedback.txt`).*

## Result: pipeline works end-to-end

7 items → 6 well-formed proposals + 1 correctly dropped (manuscript-specific
grant-number reminder). All proposals: correct format incl. Provenance,
properly abstracted (no page numbers, no project nouns), sensible categories.

## Curation-level defects found (the human step earns its place)

1. Check-type over-optimism: dimensional consistency and palette inspection
   labeled `deterministic`; both are `hybrid`/`llm`.
2. Double classification: the dropped item also appeared under matched
   (TX-1 — a wrong match on top).
3. No fold-in suggestions produced (the protocol asks for them when feedback
   sharpens an existing rule).

## Note for maintainers

Several of these synthetic-test proposals are genuinely good candidate rules
(colorblind-safe palettes, dimensional consistency, conclusion ≠ abstract,
cite-the-original). If adopted, re-distill them from REAL feedback or adopt
manually with honest provenance — these files carry test provenance and were
therefore moved out of the live proposals/ inbox.
