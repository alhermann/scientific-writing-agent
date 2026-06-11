# Worked example: distilling feedback into a rule

This shows one full pass of the learning loop on a realistic piece of
supervisor feedback, so everyone knows what good distillation looks like.

## Input (feedback received on a draft)

> p. 7: You write "the simulation results agree well with the experiment".
> How well is "well"? Give a number (relative error, R², …). We are a
> quantitative discipline — every claim of agreement or improvement in the
> paper must carry a number. Same problem on p. 9 ("significantly faster")
> and p. 11 ("much more accurate").

## Step 1 — atomic items

One item: *claims of agreement/improvement are made without quantification*
(three instances of the same principle).

## Step 2 — classify

Partially covered by FS-3 (convergence reporting), but the principle is
broader: it concerns **every** comparative claim, not only convergence
studies. → genuinely new, generalizable rule.

## Step 3/4 — abstracted draft (filed to `guidelines/proposals/`)

```markdown
## LG-? — Quantify every claim of agreement or improvement

*Severity: major · Check: hybrid · Scope: sentence*

Every claim that something agrees, improves, or outperforms must carry a
number: an error measure, a speed-up factor, a statistical metric.

**Rationale:** "Agrees well", "significantly faster", and "much more
accurate" are opinions; reviewers in a quantitative discipline read them as
either hiding a weak result or not having measured one.

**How to check:** Deterministic: flag comparative/agreement phrases
("agree(s) well", "good agreement", "significantly", "much more", "clearly
better", "excellent") without a number in the same or adjacent sentence.
LLM: confirm the claim is quantitative in nature and a metric is missing.

**Examples:**
- ✗ "The simulation results agree well with the experiment."
- ✓ "The simulated peak load deviates by 3.2 % from the experiment."

**Provenance:** distilled from supervisor feedback (draft revision round)
on 2026-06-11
```

## Step 5 — curation (maintainer)

The maintainer assigns the next free LG number, merges the rule into
`03-language.md`, and commits. From this day on, every manuscript reviewed
by anyone in the group is checked for unquantified claims — the feedback
never has to be given by a human again.
