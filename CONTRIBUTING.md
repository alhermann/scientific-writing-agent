# Contributing — and how the system learns

This repository improves in exactly one way: **feedback from real manuscript
and revision rounds is distilled into abstract rules and merged into the
guideline catalogue.** The system does not get better by itself; it gets
better every time you close this loop. Budget 15 minutes for it after every
feedback round — it pays back to the whole group, forever.

## The learning loop

```
   manuscript ──► supervisor / reviewer feedback
        ▲                   │
        │                   ▼
   better next      distill (agent-assisted):
   manuscripts      abstract the generalizable core
        ▲                   │
        │                   ▼
   guidelines/  ◄── human curation ◄── guidelines/proposals/
```

### 1. Distill

After you received feedback on a manuscript, run one of:

- **Claude Code** (Track A): `/distill-feedback` in this repository, pasting
  or pointing to the feedback.
- **CLI** (Track B): `swa distill feedback.txt --manuscript paper.tex`
- **Any MCP client**: call `get_distillation_protocol()` and follow it.

The agent splits the feedback into atomic items, matches them against
existing rules, abstracts the genuinely new principles, and files proposals
in `guidelines/proposals/` — it never edits the catalogue directly.

### 2. Curate (humans only)

A maintainer reviews each proposal:

- **Merge**: assign the next free ID in the category, move the rule into the
  category file, keep the Provenance line.
- **Fold**: add the example/wording to an existing rule.
- **Reject**: rename the file `rejected-…` with a one-line reason.

Curation standards:

- Rules must be **abstract** (apply to any future paper — no project nouns),
  **operational** (the "How to check" must be executable by an agent or
  human), and **non-duplicative**.
- Rule IDs are immutable; retired rules are marked, never deleted
  (see `guidelines/00-meta.md`).
- One rule per concern. If a proposal contains two ideas, split it.

### 3. Version

Every merge is a commit; the guideline version a review used is the git
hash in its report header. This makes review reports reproducible and
disagreements diff-able.

## Contributing code

- Core (`src/swa/{rules,manuscript,checks,bibliography,report}.py`) is
  stdlib-only by design — keep it that way.
- New deterministic checks: implement in `checks.py` with the `@register`
  decorator, referencing an existing rule ID. A check without a rule is not
  allowed — write the rule first.
- Run the smoke test before committing: `python -m tests.smoke`.

## Scope

Pull requests that add rules without provenance ("I think papers should…")
are rejected — the catalogue documents the *group's* standards, evidenced
by real feedback, not personal taste. Start from a real feedback round or
discuss in an issue first.
