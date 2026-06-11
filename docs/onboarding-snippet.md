# Onboarding snippet — Scientific Writing Agent

Ready-to-paste text for the group onboarding documents (contact the
colleagues responsible for the respective onboarding documents). Adjust the
repository URL if the repo moves to a group org.

---

## Manuscript writing & revision: use the Scientific Writing Agent

Our group maintains a guideline-driven AI tool for the fine-polishing of
manuscripts: **https://github.com/alhermann/scientific-writing-agent**

**Before you write:** read `guidelines/` once — it is our group's distilled
experience on scientific writing (storyline, structure, figures, notation,
language, bibliography), starting from the group's publication checklist.

**Before you circulate a draft** to your supervisor or co-authors:

1. Clone the repository and open it in Claude Code (or connect the MCP
   server to your preferred AI client — see the README).
2. Run `/review-manuscript path/to/your/paper.tex` and work through the
   report. Fix everything marked critical/major before sending the draft.
   This typically saves one full feedback iteration.

**After every feedback round** (supervisor comments, reviewer reports):

3. Run `/distill-feedback` on the feedback you received. The agent abstracts
   the generalizable lessons into rule proposals that — after curation —
   make the tool better for everybody. This step is how the group's writing
   knowledge compounds over the years; please don't skip it.

No AI subscription? The deterministic checks run without any LLM:
`pip install -e . && swa lint paper.tex`. Helmholtz members can run the full
agent for free via Blablador (see README, "Which model should I use?").

---
