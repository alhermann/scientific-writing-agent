# Scientific Writing Agent — agent instructions

This repository is a guideline-driven manuscript review system. The single
source of truth is `guidelines/` — a versioned catalogue of writing rules
(IDs like SL-1, ST-2, …) defined per the format in `guidelines/00-meta.md`.

## When asked to review/check/polish a manuscript

Use the `/review-manuscript` skill (`.claude/skills/review-manuscript/`).
Never review against personal taste where a catalogue rule exists; never
invent rules outside the catalogue.

## When given feedback from supervisors/reviewers

Use the `/distill-feedback` skill. New rules go to `guidelines/proposals/`
only — NEVER edit the category files `guidelines/0*-*.md` directly; a human
maintainer curates proposals into the catalogue.

## Code conventions

- `src/swa/` core modules (rules, manuscript, checks, bibliography, report)
  are stdlib-only — do not add dependencies there. MCP server (`[mcp]` extra)
  and LangGraph agent (`[agent]` extra) carry the dependencies.
- New deterministic checks in `checks.py` must reference an existing rule ID
  (rule first, check second).
- Smoke test: `python -m tests.smoke` (no LLM, no network).

## Useful commands

```bash
PYTHONPATH=src python3 -m swa.cli rules              # list the catalogue
PYTHONPATH=src python3 -m swa.cli lint <file.tex>    # deterministic checks
PYTHONPATH=src python3 -m swa.cli structure <file>   # section/word-count skeleton
python -m tests.smoke                # self-test
```
