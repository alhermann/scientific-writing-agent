# Guideline format specification

This file defines the format every guideline file in this directory must follow.
The MCP server and the LangGraph agent parse these files mechanically, so the
format is a contract, not a suggestion.

## File layout

Each category lives in one file `NN-category.md`:

```markdown
# <Category title>

<one-paragraph scope statement>

## <ID> — <Rule title>

*Severity: critical | major | minor · Check: llm | deterministic | hybrid · Scope: global | section | sentence*

<normative rule statement, imperative voice, 1–3 sentences>

**Rationale:** <why this rule exists>

**How to check:** <operational instructions an agent (or human) follows to verify the rule>

**Examples:**
- ✗ <violating example>
- ✓ <corrected example>
```

## Rule IDs

| Prefix | Category | File |
|--------|----------|------|
| SL | Storyline & narrative | 01-storyline.md |
| ST | Structure (abstract, introduction, sections) | 02-structure.md |
| LG | Language & style | 03-language.md |
| MA | Mathematics & nomenclature | 04-mathematics.md |
| FG | Figures & tables | 05-figures.md |
| CI | Citations & bibliography | 06-citations.md |
| TX | LaTeX & typesetting hygiene | 07-latex.md |
| WF | Workflow before writing | 08-before-writing.md |
| FS | Field-specific (computational mechanics & materials) | 09-field-specific.md |

IDs are immutable: never renumber or reuse an ID. New rules get the next free
number in their category. Retired rules keep their ID with the marker
`*(retired YYYY-MM-DD: reason)*` so old review reports stay interpretable.

## Severity levels

- **critical** — violations typically cause rejection or major-revision
  verdicts, or make the paper unintelligible (e.g., broken storyline,
  undefined symbols).
- **major** — violations visibly reduce quality and credibility
  (e.g., overlong introduction, inconsistent nomenclature).
- **minor** — polish-level issues (e.g., "in order to", capitalization).

## Check types

- **deterministic** — verifiable by a script without an LLM
  (regex, counting, structural parsing). Implemented in `src/swa/checks.py`.
- **llm** — requires semantic judgement; the agent evaluates the rule against
  the manuscript with a rule-specific prompt.
- **hybrid** — a deterministic pass produces candidates, an LLM pass filters
  false positives.

## Provenance and the learning loop

Every rule added after the initial import must carry a provenance line:

```markdown
**Provenance:** distilled from <source, e.g. "revision feedback, MS-2026-04, reviewer 2"> on YYYY-MM-DD
```

New rules enter via `guidelines/proposals/` (see CONTRIBUTING.md) and are
merged into the category files only after human curation. This is how the
system learns: feedback in → abstracted rule out → versioned forever.
