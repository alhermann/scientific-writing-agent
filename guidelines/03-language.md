# Language & style

Sentence-level rules. Many have deterministic detectors with low false-positive
rates; the semantic ones (LG-1, LG-2) are the hardest and most valuable checks
in the whole catalogue.

## LG-1 — Use logically accurate language

*Severity: critical · Check: llm · Scope: sentence*

Every formulation must be logically exact: attribute properties to the
mathematical object that actually carries them, not to a related quantity.

**Rationale:** Inaccurate language is one of the most prevalent reasons why
scientific papers are hard to understand. Good scientists spend substantial
effort on exact wording; sloppy wording signals sloppy thinking to reviewers.

**How to check:** Pause after every sentence and ask: is each property
ascribed to the right object? Classic traps: a *quantity* cannot be nonlinear
— only a *relation/function* between quantities can; a *kink* is not a point
but a relation between adjacent segments located *at* a point; a *material*
is not nonlinear, its *response* is; an *error* does not converge, the
*sequence of solutions* does.

**Examples:**
- ✗ "The plot shows a nonlinear stress."
- ✓ "The plot shows a nonlinear stress–strain relation."
- ✗ "…up to the yield strength, which is a sharp kink in the curve."
- ✓ "…up to the yield strength, at which the curve exhibits a sharp kink."

## LG-2 — Use tenses consistently

*Severity: major · Check: llm · Scope: section*

Choose a tense scheme and keep it: present for what the paper does and for
established facts ("Section 3 presents…", "stress depends on…"), simple past
for actions performed ("we computed 200 samples"), present perfect for prior
literature where appropriate. Never mix tenses thoughtlessly within a
passage.

**Rationale:** Unmotivated tense switches force the reader to re-orient and
suggest carelessness.

**How to check:** For each paragraph, list the tenses used and check each
switch has a semantic reason (general fact vs. performed action vs. prior
work).

**Examples:**
- ✗ "Figure 5 showed the results. The error decreases with mesh refinement
  and reached 1 %."
- ✓ "Figure 5 shows the results. The error decreases with mesh refinement
  and reaches 1 %."

## LG-3 — Replace "in order to" by "to"

*Severity: minor · Check: deterministic · Scope: sentence*

"In order to" is almost always better replaced by a simple "to".

**Rationale:** Keeps text short and sentences simple — the cheapest
conciseness win available.

**How to check:** Deterministic search for "in order to" (case-insensitive);
suggest "to". The rare legitimate uses (sentence-initial where "To" would be
ambiguous) survive human review.

**Examples:**
- ✗ "In order to verify the implementation, we…"
- ✓ "To verify the implementation, we…"

## LG-4 — Capitalize sparingly (English ≠ German)

*Severity: minor · Check: hybrid · Scope: global*

In running text capitalize only names and sentence beginnings. In section
titles, capitalize only the first word (plus names) — sentence case. In axis
labels and sub-plot titles use no capitals at all (except names). Chemical
elements and species are lowercase in English: "magnesium", not "Magnesium".

**Rationale:** German writers over-capitalize by habit. Full Title Case is
permitted in principle but almost never applied consistently — sentence case
is the rule that survives revisions.

**How to check:** Deterministic: scan headings for mid-title capitalized
non-name words; scan text for capitalized common nouns (German-interference
candidates: element names, "Finite Elements", "Simulation"). LLM: filter
proper names and established acronym expansions.

**Examples:**
- ✗ "4.2 Comparison With Experimental Data For Magnesium"
- ✓ "4.2 Comparison with experimental data for magnesium"

## LG-5 — Hyphenate compound modifiers

*Severity: minor · Check: hybrid · Scope: sentence*

Compound adjectives before a noun take hyphens: "one-dimensional",
"stress-mediated", "stress–strain curve", "single-minded",
"finite-element method" (as modifier), "mesh-free", "rate-dependent".

**Rationale:** Missing hyphens are the most frequent typo class of non-native
writers and immediately visible to native reviewers. Improving such details
determines whether you are taken seriously.

**How to check:** Deterministic: flag known unhyphenated pairs ("one
dimensional", "two dimensional", "stress strain", "well known" + noun,
"data driven", "physics informed", "mesh free", "rate dependent",
"first order" + noun…). LLM: filter cases where the pair is not a modifier
("the method is well known" — correctly unhyphenated).

**Examples:**
- ✗ "a one dimensional stress strain relation"
- ✓ "a one-dimensional stress–strain relation"

## LG-6 — Eliminate typos and spelling errors

*Severity: major · Check: hybrid · Scope: global*

Reread the entire paper at least once with the single purpose of catching
typos, spelling errors, duplicated words, and missing words.

**Rationale:** Every surviving typo costs credibility; reviewers extrapolate
from surface sloppiness to scientific sloppiness.

**How to check:** Deterministic: spell-check, duplicated-word detector
("the the"), common confusions (its/it's, then/than, principal/principle,
discrete/discreet). LLM: context-dependent errors a spell-checker misses.

**Examples:**
- ✗ "the the proposed method", "discreet element method"
- ✓ "the proposed method", "discrete element method"

## LG-7 — Prefer the direct formulation

*Severity: minor · Check: hybrid · Scope: sentence*

Replace scaffolding phrases by direct statements: "The results in Figure 4
show…" → "Figure 4 shows…"; "(see Figure 8)" → "(Figure 8)"; "It can be seen
that X" → "X"; "We note that X" → "X" (where nothing is lost).

**Rationale:** Scaffolding adds words but no meaning; cumulative across a
paper it costs half a page and the reader's patience.

**How to check:** Deterministic: search for the marker phrases ("see Figure",
"see Fig.", "It can be seen", "It should be noted", "The results in",
"it is worth mentioning"). LLM: confirm the direct rewrite preserves meaning.

**Examples:**
- ✗ "It can clearly be seen from Figure 3 that the error decreases."
- ✓ "Figure 3 shows the error decreasing." / "The error decreases (Figure 3)."
