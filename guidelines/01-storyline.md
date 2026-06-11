# Storyline & narrative

Rules governing the single most important property of a scientific paper:
a focused, gap-free, linear story. These rules operate on the whole manuscript
and almost always require semantic judgement (LLM or human review).

## SL-1 — Follow a single storyline

*Severity: critical · Check: llm · Scope: global*

Identify one key problem the paper addresses and report only what most
directly serves that problem. Remove every side quest, however interesting.

**Rationale:** During a project you try out a hundred things; the temptation
to report them all is the single biggest mistake in paper writing. Material
that is not on the storyline dilutes the contribution, exhausts the reader,
and hides the actual novelty. Work that is cut was not wasted — it was the
evidence that the reported approach is the right one. Keep an
"AdditionalThoughts" document for everything you cut; it is a reliable source
of future papers.

**How to check:** State the paper's key problem in one sentence. Then walk
through every paragraph and ask: does this paragraph advance the reader from
the problem to the proposed solution? Flag every paragraph, subsection, or
result that serves a different story.

**Examples:**
- ✗ A paper on a new peridynamic discretization that also reports, across two
  sections, an unrelated mesh-generation utility and a parameter study of a
  legacy method "for completeness".
- ✓ The same paper reporting only the new discretization, its verification,
  and its application — with the utility moved to a repository README and the
  legacy study to private notes.

## SL-2 — Start from zero and stay C⁰-continuous

*Severity: critical · Check: llm · Scope: global*

Begin the story at a point a non-specialist reader can follow and never leave
a logical gap: each sentence must follow from the previous one.

**Rationale:** Authors have lived inside their project for months and
unconsciously skip steps that are non-trivial for everyone else. The first
gap in the logical chain is where the reader stops reading — and a reader who
stops reading does not adopt your ideas, cite your work, or accept your paper.
Mathematically speaking, your storyline must be at least a C⁰ function.

**How to check:** Read the manuscript sentence by sentence and after each one
ask: does this follow from what was stated before, using only knowledge a
graduate student in the broader field has? Flag every jump — undefined
context in the abstract's first sentence, results invoked before methods,
concepts used a section before they are introduced.

**Examples:**
- ✗ Abstract opening: "Our adaptive coupling reduces the ghost-force error by
  two orders of magnitude." (The reader does not yet know the topic, the
  setting, or what ghost forces are.)
- ✓ Abstract opening: "Simulating fracture requires numerical methods that
  can represent discontinuous displacement fields. Peridynamics offers this
  capability, but coupling it efficiently with finite elements remains
  challenging because …"

## SL-3 — Avoid redundancy and premature forward references

*Severity: major · Check: llm · Scope: global*

Discuss each technical point exactly once, in the section dedicated to it.
Do not pre-discuss details of later sections.

**Rationale:** Pre-discussion causes double treatment (once in advance, once
in place) and relies on content the reader is not yet prepared for. Brief,
general signposts ("Section 4 quantifies this effect") are fine; technical
forward discussion is not.

**How to check:** For each paragraph, identify its technical content and
check whether the same content is treated again later. Flag pairs of passages
that cover the same material; flag forward references that go beyond a
one-clause signpost.

**Examples:**
- ✗ Explaining the stabilization parameter's calibration in the introduction,
  then again in Section 3.
- ✓ Introduction: "…which requires a stabilization parameter (Section 3)."
  All calibration detail appears only in Section 3.

## SL-4 — Describe what works, not what does not

*Severity: major · Check: llm · Scope: global*

Report the approach that works. Do not narrate failed attempts, except when
the reader would reasonably expect the simple solution to work — then explain
briefly why it does not, ideally isolated in a remark or appendix.

**Rationale:** There is no value for the reader in the 1000 things that
failed; tell them about the 1001st that worked. Failure narratives bloat the
paper and obscure the storyline. The single exception: pre-empting the
reviewer question "why didn't you just do X?".

**How to check:** Flag passages describing abandoned approaches, negative
results, or detours. For each, decide: is this pre-empting an obvious
objection? If yes, recommend compressing it into a remark/appendix; if no,
recommend deletion.

**Examples:**
- ✗ "We first attempted a collocation approach, which proved unstable. We
  then tried …" (half a page of history).
- ✓ "Remark 2. A direct collocation approach suffers from instabilities near
  the boundary [12]; we therefore employ a weak-form discretization."

## SL-5 — Rest, reread, shorten

*Severity: major · Check: llm · Scope: global*

After finishing a draft, let it rest (≈2 days), then reread the whole text
with one goal: cut. Remove everything not essential to the key message and
simplify every sentence that can be simplified.

**Rationale:** Conciseness is a feature, not a loss. Do not suffer from fear
of loss when cutting details that were necessary for you to obtain the
results but are not necessary for the reader to understand them. Shorter
papers are read, understood, and accepted more often.

**How to check:** For every paragraph ask: would the key message survive
deleting this? For every sentence ask: can it be said in fewer words? Typical
targets: "The results in Figure 4 show…" → "Figure 4 shows…"; "(see Figure
8)" → "(Figure 8)"; filler adverbs; nominalizations ("perform an
investigation of" → "investigate").

**Examples:**
- ✗ "In order to be able to perform a quantitative assessment of the accuracy
  of the proposed method, we carried out an investigation of the convergence
  behavior."
- ✓ "To quantify the method's accuracy, we study its convergence."
