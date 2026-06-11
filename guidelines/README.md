# Guidelines — single source of truth

This directory is the **asset** of the whole system: a versioned, structured,
machine-readable catalogue of scientific-writing and manuscript-revision
rules. Everything else in this repository (skills, MCP server, LangGraph
agent) merely *consumes* these files.

| File | Category | Rules |
|------|----------|-------|
| [00-meta.md](00-meta.md) | Format specification | — |
| [01-storyline.md](01-storyline.md) | Storyline & narrative | SL-1 … SL-5 |
| [02-structure.md](02-structure.md) | Abstract, introduction, sections | ST-1 … ST-5 |
| [03-language.md](03-language.md) | Language & style | LG-1 … LG-7 |
| [04-mathematics.md](04-mathematics.md) | Mathematics & nomenclature | MA-1 … MA-4 |
| [05-figures.md](05-figures.md) | Figures & tables | FG-1 … FG-5 |
| [06-citations.md](06-citations.md) | Citations & bibliography | CI-1 … CI-3 |
| [07-latex.md](07-latex.md) | LaTeX & typesetting hygiene | TX-1 … TX-3 |
| [08-before-writing.md](08-before-writing.md) | Workflow before writing | WF-1 … WF-2 |
| [09-field-specific.md](09-field-specific.md) | Computational mechanics & materials | FS-1 … FS-6 |
| proposals/ | Incoming rules from feedback distillation | — |

The initial catalogue was distilled from an internal *Check-list for
scientific publications* (2021-07-03 / 2022-12-17 version, kept in the
group's internal archive) and extended with established scientific-writing
canon and field conventions.

## How the catalogue grows

After every manuscript or revision round, feedback is **distilled** into
abstract rules (see [CONTRIBUTING.md](../CONTRIBUTING.md) and the
`distill-feedback` skill). Proposals land in `proposals/`, are curated by a
human, and merged here. The system does not get better "by itself" — it gets
better through this loop, every time someone feeds their review experience
back.
