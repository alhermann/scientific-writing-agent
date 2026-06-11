# LaTeX & typesetting hygiene

Source-level cleanliness. Fully or largely deterministic.

## TX-1 — Leave no rubbish in circulated documents

*Severity: major · Check: deterministic · Scope: global*

Remove outdated text, commented-out blocks, and dead alternatives before
sending the document to anyone. Preserve old material in version control or
a private copy — never in the circulated source.

**Rationale:** A publication is an exercise in ordering things so others can
understand them; rubbish in the source creates confusion, and there is
nothing worse than confusion in that process.

**How to check:** Flag large commented-out regions (> ~3 consecutive comment
lines containing prose/math), leftover TODO/FIXME/XXX markers, `\iffalse`
blocks, tracked-changes remnants, and alternative formulations parked in
comments.

**Examples:**
- ✗ 40 commented-out lines of a previous derivation above the current one.
- ✓ Clean source; the old derivation lives in git history.

## TX-2 — Use TeX constructs consistently

*Severity: minor · Check: deterministic · Scope: global*

Typeset the same thing the same way everywhere: `$[1\,1\,1]$` in one place
and bare `[1 1 1]` in another *look different* in the compiled document.
The same holds for `\text{…}` vs. roman subscripts, `\,` spacing in units,
`Fig.` vs. `Figure`, and quotation marks.

**Rationale:** Minor visual inconsistencies trigger confusion — and there is
nothing worse than confusion in a paper.

**How to check:** Detect mixed conventions: same token sequence appearing
inside and outside math mode; mixed `Fig.`/`Figure`; mixed `"`/``` `` ```
quotes; units with and without `\,`/`\si`; inline numbers as digits and words
for the same magnitude class.

**Examples:**
- ✗ "direction $[1 1 1]$" in Section 2 but "direction [1 1 1]" in Section 5.
- ✓ One macro `\dir{1 1 1}` used everywhere.

## TX-3 — Reference mechanically, never by hand

*Severity: minor · Check: deterministic · Scope: global*

All cross-references (sections, equations, figures, tables, citations) must
use `\ref`/`\eqref`/`\cite` (or `cleveref`); never hard-code numbers.

**Rationale:** Hand-written numbers silently break on every revision —
exactly when nobody re-checks them.

**How to check:** Flag patterns like "Section 3", "Eq. (12)", "Figure 4"
in the source that are not produced by a reference macro.

**Examples:**
- ✗ "as shown in Figure 4" (typed literally while figures were reordered).
- ✓ `as shown in \cref{fig:convergence}`.
