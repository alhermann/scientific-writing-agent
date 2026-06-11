---
name: distill-feedback
description: Distill manuscript/revision feedback (supervisor comments, reviewer reports) into new guideline-rule proposals — the learning loop of the writing-agent system. Use when the user shares feedback they received on a manuscript.
---

# Distill feedback into guideline-rule proposals

Input: feedback on a manuscript — pasted text, a file path, or an annotated
document. Optionally the manuscript itself for context. If neither is given,
ask for the feedback.

## Procedure

1. **Split** the feedback into atomic items (one criticism/advice each).
   Number them.

2. **Load the rule index**: `PYTHONPATH=src python3 -m swa.cli rules` (or read
   `guidelines/README.md` + category files).

3. **Classify** each item:
   - **(a) instance of an existing rule** → record `RULE-ID: <item>`. If the
     feedback contains a sharper formulation or a new instructive example,
     note it as a *fold-in* suggestion for that rule.
   - **(b) genuinely new, generalizable principle** → draft a new rule.
   - **(c) manuscript-specific** (typo lists, content questions, project
     details) → record under *dropped*.

4. **Abstract** each new rule away from the specific manuscript: no project
   nouns, no author names, phrased so it applies to any future paper of the
   group. If you cannot phrase it generally, it belongs in (c).

5. **Draft** each rule in the exact format of `guidelines/00-meta.md`:
   - heading `## XX-? — <imperative title>` (keep the literal `?`; the
     maintainer assigns the number),
   - metadata line `*Severity: … · Check: … · Scope: …*`,
   - normative statement, **Rationale**, **How to check** (operational!),
     ✗/✓ **Examples** (anonymized),
   - `**Provenance:** distilled from <source> on <YYYY-MM-DD>`.

6. **File** each draft as
   `guidelines/proposals/<YYYY-MM-DD>-<slug>.md`.
   NEVER edit the category files `guidelines/0*-*.md` directly — proposals
   are curated by a human maintainer (see CONTRIBUTING.md).

7. **Summarize** for the user: matched rules (with fold-in suggestions),
   new proposal files, dropped items. Close by reminding them a maintainer
   must curate the proposals.

## Quality bar for proposals

- One rule per concern — split multi-idea items.
- "How to check" must be executable by an agent or human without further
  interpretation.
- Severity honestly: would this cause rejection (critical), visibly hurt
  quality (major), or is it polish (minor)?
- When in doubt between (a) and (b), prefer (a) with a fold-in — catalogue
  growth must not come at the cost of duplication.
