# Structure: abstract, introduction, sections

Rules on the macroscopic skeleton of the manuscript. Several of these are
partially checkable by deterministic means (lengths, presence of marker
phrases); the semantic half needs an LLM or human pass.

## ST-1 — Keep the abstract short and two-part

*Severity: critical · Check: hybrid · Scope: section*

The abstract must be understandable with very limited background knowledge,
contain no technical detail, and cover exactly two things: (1) the key
scientific question/problem and (2) the proposed solution/novelty.
10–15 lines (≈150–250 words) suffice.

**Rationale:** The abstract is read by far more people than the paper, often
by non-specialists deciding whether to read on. Technical detail and
secondary results waste this one chance.

**How to check:** Deterministic: word count ≤ ~250. LLM: verify the
problem→solution arc is present, no symbols or technical jargon appear that a
non-specialist cannot parse, and no content beyond problem + solution +
headline result is included.

**Examples:**
- ✗ An abstract listing the discretization order, the solver tolerances, and
  four secondary findings.
- ✓ Problem (3–4 sentences, from zero) → gap → "We propose…" → headline
  result → one sentence on impact.

## ST-2 — Summarize novelties at the end of the introduction

*Severity: critical · Check: hybrid · Scope: section*

The last paragraph of the introduction must start with a phrase like
"In this paper, we introduce/present…" and briefly enumerate the novel
contributions relative to the state of the art reviewed before.

**Rationale:** Without this paragraph, readers and reviewers may not
understand what is novel — and then they reject or ignore the paper.
Redundancy with the abstract is expected and acceptable: abstract and
introduction must each be understandable on their own.

**How to check:** Deterministic: search the final introduction paragraph(s)
for novelty markers ("In this paper", "we introduce", "we present", "the
contribution", "for the first time", "novel"). LLM: verify the paragraph
actually enumerates contributions and that each claimed novelty is
distinguishable from the cited state of the art.

**Examples:**
- ✗ An introduction that reviews literature for a page and then jumps to
  "The paper is organized as follows."
- ✓ "In this paper, we introduce a peridynamic formulation that (i) …,
  (ii) …, and (iii) …. To the best of our knowledge, no existing approach
  combines …"

## ST-3 — Keep the introduction at or below one page

*Severity: major · Check: hybrid · Scope: section*

State of the art: ≤ 3/4 page. Novelty summary: ≈ 1/4 page. Total: ≤ 1 page
(rare, justified exceptions aside). If longer, move material into later
sections.

**Rationale:** The introduction exists so a reader understands very quickly
what the paper is about. An introduction that does not fulfil that purpose
loses readers to better-written papers.

**How to check:** Deterministic: estimate rendered length from word count
(≈500–700 words/page single-column, ≈900–1000 two-column). LLM: if overlong,
identify which paragraphs are method/result detail that belongs in later
sections.

**Examples:**
- ✗ A 2.5-page introduction containing a mini-review of all nonlocal methods
  since 2000.
- ✓ One page: context (from zero) → focused state of the art → gap →
  novelty paragraph.

## ST-4 — Re-check structure against content when quasi-final

*Severity: major · Check: llm · Scope: global*

Once the draft is quasi-final, re-read the abstract and all (sub)section
headings and verify they still match the content; restructure or retitle
where they diverged.

**Rationale:** Content drifts during writing and revision; headings and
abstract written early often describe an older version of the paper.

**How to check:** Build the outline (headings only) and compare it against a
one-sentence summary of each section's actual content. Flag mismatches,
sections that grew beyond their title, and abstract claims no longer backed
by the content.

**Examples:**
- ✗ Section titled "Validation" that now mostly contains a parameter study.
- ✓ Splitting it into "Validation" and "Sensitivity analysis", and updating
  the abstract accordingly.

## ST-5 — Use systematic, parallel section titles

*Severity: minor · Check: hybrid · Scope: global*

Titles of sections at the same level must follow one consistent style — all
short noun phrases or all long descriptive phrases, never a mixture.

**Rationale:** Mixing styles ("Image registration" next to "Methods for deep
learning") makes the impression of unsystematic thinking.

**How to check:** Deterministic: extract all same-level headings, compare
their grammatical pattern and length. LLM: confirm flagged inconsistencies
are real style breaks and propose a uniform set.

**Examples:**
- ✗ 3.1 "Image registration" / 3.2 "Methods for deep learning"
- ✓ 3.1 "Image registration" / 3.2 "Deep learning" — or both with the
  "Methods for …" prefix.
