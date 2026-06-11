# Mathematics & nomenclature

Rules on symbols, equations, and naming. MA-1 is among the most common and
most damaging defects in submitted manuscripts.

## MA-1 — Define every symbol before or at first use

*Severity: critical · Check: hybrid · Scope: global*

Every operator, parameter, and variable appearing in any equation or figure
must be explicitly defined in the surrounding text or caption. No exceptions
beyond truly elementary operators (+, −, sin, cos, ∂, …).

**Rationale:** A single undefined symbol can make a derivation unverifiable.
Reviewers read equations symbol by symbol; an undefined one stops them
exactly like a logical gap stops a reader (see SL-2).

**How to check:** Deterministic: extract all symbols from math environments
and figure labels; for each, search preceding text for a definition pattern
("where X denotes/is…", "X := …", "the X-th …"). LLM: resolve aliases
(bold vs. index notation), judge whether a "definition" actually defines, and
whitelist field-standard symbols only if the venue's audience guarantees them.

**Examples:**
- ✗ Equation uses **C** without any statement of what it is.
- ✓ "…where **C** denotes the fourth-order elasticity tensor."

## MA-2 — Use one symbol per quantity, one quantity per symbol

*Severity: critical · Check: hybrid · Scope: global*

Nomenclature must be consistent: the same quantity or phenomenon carries the
same symbol/name everywhere; no symbol is reused for a second meaning.

**Rationale:** Inconsistencies easily confuse readers — they cannot know
whether σ and **σ** and "the stress s" are one object or three. Such defects
typically arise from merging text written at different times.

**How to check:** Deterministic: build a symbol table with usage locations;
flag near-duplicates (same letter, varying decoration) and terminology pairs
used interchangeably ("horizon size" vs. "neighborhood radius"). LLM: decide
which flagged pairs truly denote the same object and propose the canonical
choice.

**Examples:**
- ✗ Calling δ the "horizon" in Section 2 and the same quantity the
  "interaction radius ε" in Section 4.
- ✓ One name, one symbol, fixed at first introduction and used throughout.

## MA-3 — Keep nomenclature as simple as possible

*Severity: major · Check: llm · Scope: global*

After revisions, re-examine all sub-/superscripts and decorations: if a
simpler nomenclature would still be unambiguous, simplify.

**Rationale:** Notation accretes during writing; what needed three indices in
draft 1 often needs one in the final storyline. Every needless index taxes
the reader on every occurrence.

**How to check:** From the symbol table, identify decorations that never vary
within the paper (an index that always takes the same value, a superscript
distinguishing cases of which only one remains) and propose their removal.

**Examples:**
- ✗ Writing u̅ᵢʰ'ᵏ throughout although k is fixed after Section 2.
- ✓ Stating once "we drop the index k in the following" and writing u̅ᵢʰ.

## MA-4 — State equations as part of the sentence

*Severity: minor · Check: llm · Scope: sentence*

Equations are grammatical parts of sentences: introduce them, punctuate them,
and connect them ("Substituting (3) into (5) yields …, where …").

**Rationale:** Free-floating equation blocks without connecting prose break
C⁰ continuity (SL-2) inside the mathematical exposition.

**How to check:** Flag display equations preceded by a colon-less fragment or
followed by an unconnected new paragraph; check "where"-clauses define all
newly appearing symbols (ties into MA-1).

**Examples:**
- ✗ "The energy. \[equation\] The next step is discretization."
- ✓ "The total energy reads \[equation\], where Ψ denotes the strain-energy
  density. Discretizing (7) by …"
