---
name: review-manuscript
description: Review a scientific manuscript (LaTeX/Markdown) against the group's versioned writing guidelines and produce a structured review report. Use when the user asks to review, check, or polish a paper/manuscript/draft.
---

# Review a manuscript against the group guidelines

You review a scientific manuscript against the rule catalogue in
`guidelines/` of this repository. The argument is the path to the manuscript
(`.tex` or `.md`); if none is given, ask for it.

## Procedure

1. **Orient.** Run the structural analysis:
   ```bash
   PYTHONPATH=src python3 -m swa.cli structure <manuscript>
   ```
   Note abstract/introduction word counts and the section outline.

2. **Lint (deterministic layer).**
   ```bash
   PYTHONPATH=src python3 -m swa.cli lint <manuscript>
   ```
   If a `.bib` file exists next to the manuscript, also:
   ```bash
   PYTHONPATH=src python3 -m swa.cli bib <refs.bib> --tex <manuscript>
   ```
   Keep all findings. Verify every finding marked *candidate* yourself by
   reading the flagged line in context before reporting it; drop false
   positives silently.

3. **Load the rules.** Read all files `guidelines/0[1-9]-*.md`. These are the
   single source of truth — never review against your general taste where a
   rule exists, and never invent rules that are not in the catalogue.

4. **Semantic review.** Work category by category in this order:
   **SL → ST → MA → FS → FG → LG → CI → TX → WF** (storyline first — it
   matters most). For every rule with `Check: llm` or `Check: hybrid`,
   follow its **How to check** instructions literally against the manuscript.
   Read the manuscript in full; for long manuscripts work section by section.

5. **Report.** Write one markdown report (to `<manuscript-stem>-review.md`
   unless the user wants it inline) containing:
   - Header: manuscript path, date, guideline version (`git rev-parse --short HEAD`).
   - **Executive summary**: 5–10 lines + the three highest-impact improvements.
   - Findings grouped by severity (critical → major → minor), each with rule
     ID, location (line/section), verbatim excerpt, explanation, and a
     concrete suggested rewrite where possible.
   - **Not checked**: rules that could not be assessed from the given
     material (e.g., rendered figures missing) with reasons.

## Honesty rules

- Quote excerpts verbatim. Never fabricate line numbers — use the line
  numbers from the lint output or section names.
- An empty findings list for a category is a valid result; do not pad.
- Do not rewrite the manuscript unless the user explicitly asks; the report
  suggests, the author decides.

## After the review

Remind the user once, briefly: if this manuscript later receives human
feedback (supervisor/reviewers), run `/distill-feedback` so the guidelines
learn from it.
