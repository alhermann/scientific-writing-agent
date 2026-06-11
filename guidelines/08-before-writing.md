# Workflow before writing

What to do *before* the first sentence is written. These rules cannot be
checked against a manuscript text alone, but the agent checks their
*symptoms* and reminds authors at project start.

## WF-1 — Re-run key studies systematically before writing

*Severity: critical · Check: llm · Scope: global*

Before writing, repeat the most important studies in a rigorously structured
manner: vary only the key parameters, hold everything else fixed, and fill
the unspectacular gaps in the parameter space that round off the work.

**Rationale:** During exploration you changed minor settings (time-step
size, tolerances, mesh details) for convenience, leaving a pile of results
that differ in more than the parameters under study. Writing this down
honestly becomes complicated and lengthy — troublesome for you and worse for
the reader. A clean re-run makes both the writing and the reading simple.

**How to check (symptoms in the manuscript):** Flag results sections where
nominally comparable cases differ in incidental parameters ("for case A we
used Δt = 10⁻³, for case B Δt = 5·10⁻⁴"), apologetic footnotes about
setting differences, and parameter tables with irregular gaps.

**Examples:**
- ✗ "Simulations were performed with slightly different solver settings,
  which we expect not to influence the results."
- ✓ One parameter table; all cases differ only in the studied parameters.

## WF-2 — Fix the storyline before the text

*Severity: major · Check: llm · Scope: global*

Before writing prose, write the skeleton: the one-sentence key problem
(SL-1), the section outline, the list of figures with their messages
(FG-2), and the novelty bullets (ST-2). Write text only once the skeleton is
stable.

**Rationale:** Text written before the storyline is fixed produces exactly
the redundancies (SL-3), drifted structures (ST-4), and nomenclature
inconsistencies (MA-2) that the other rules then have to catch. An hour on
the skeleton saves a revision cycle.

**How to check:** At review time, indirectly: papers without a skeleton show
the symptom cluster above. As a pre-writing service, the agent interviews
the author for problem statement, novelty bullets, and figure list, and
checks them for SL-1/ST-2 compliance before any prose exists.

**Examples:**
- ✗ Starting to write Section 2 "because the methods are clear anyway".
- ✓ A half-page skeleton agreed with all co-authors before drafting.
