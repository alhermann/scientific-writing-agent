# Citations & bibliography

Bibliography hygiene. Almost fully deterministic — the agent can lint a
`.bib` file mechanically.

## CI-1 — Keep the bibliography complete and correct

*Severity: major · Check: deterministic · Scope: global*

Every journal-article entry must contain at least: full author list, full
journal name, volume, pages (or article number), and year. Books and
proceedings need their respective fields (editor, publisher, place, …).
Double-check the compiled bibliography before circulating the manuscript.

**Rationale:** Use a citation manager from day one, but never trust its
downloads blindly — imported metadata is incomplete or wrong surprisingly
often, and a defective bibliography is the first thing a meticulous reviewer
notices.

**How to check:** Parse the `.bib` file; for each entry type, verify required
fields are present and non-placeholder; flag "et al." inside author fields,
abbreviated journal names mixed with full ones, missing page/article numbers,
and year mismatches between key and field.

**Examples:**
- ✗ `@article{x, author={Smith, J. and others}, journal={CMAME}, year={2023}}`
- ✓ Full author list, `journal={Computer Methods in Applied Mechanics and
  Engineering}, volume={415}, pages={116234}, year={2023}`.

## CI-2 — Verify names that citation managers break

*Severity: major · Check: hybrid · Scope: global*

Check entries whose author names citation managers typically mangle:
multi-word surnames ("Van Der Giessen", "De Borst"), particles, accents, and
hyphenated names. Verify the surname/given-name split is correct.

**Rationale:** Managers often interpret one word of a two-word surname as a
given name and reduce it to an initial — a visible insult to the cited
colleague and a broken reference for indexing.

**How to check:** Deterministic: flag entries with particles/multi-word name
patterns and missing brace protection (`{De Borst}, René`). LLM/human:
confirm the correct split for flagged names.

**Examples:**
- ✗ `author={Borst, R. de}` rendered as "B. R. de".
- ✓ `author={{de Borst}, René}`.

## CI-3 — Cite consistently and where the claim is made

*Severity: major · Check: hybrid · Scope: global*

Every non-trivial claim about prior work carries its citation at the claim;
one citation style throughout; no orphan bibliography entries (uncited) and
no dangling citations (unresolved keys).

**Rationale:** Claims without citations read as either trivial or
appropriated; orphans and danglers signal leftover rubbish (TX-1).

**How to check:** Deterministic: cross-check `\cite` keys against `.bib`
entries in both directions; flag "it is well known", "previous studies have
shown" without an adjacent citation. LLM: judge whether flagged claims indeed
need a source.

**Examples:**
- ✗ "Several authors have extended peridynamics to coupled problems." (no
  citations)
- ✓ "Several authors have extended peridynamics to coupled problems
  [12–15]."
