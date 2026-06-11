# Field-specific rules: computational mechanics & materials modeling

Conventions of the group's home field (continuum mechanics, peridynamics and
nonlocal methods, fracture and damage mechanics, materials modeling,
machine-learning-based constitutive modeling) and its typical venues
(CMAME, JMPS, Computational Mechanics, Engineering Fracture Mechanics,
International Journal of Plasticity, JMBBM, …).

## FS-1 — Distinguish verification from validation

*Severity: critical · Check: llm · Scope: global*

Use *verification* for "solving the equations right" (convergence to
manufactured/analytical solutions, patch tests) and *validation* for
"solving the right equations" (comparison against experiments). Never use
the words interchangeably, and never claim validation from a comparison with
another simulation.

**Rationale:** The V&V distinction is standard in computational mechanics;
confusing the two is a classic reviewer trigger in CMAME-class journals.

**How to check:** Locate all uses of verify/validate (and derivatives);
check each against what is actually compared (analytic/manufactured solution
vs. experimental data vs. other code — the last one is a *code comparison*,
neither V nor V).

**Examples:**
- ✗ "The model is validated against the analytical solution."
- ✓ "The implementation is verified against the analytical solution and the
  model is validated against the experiments of [23]."

## FS-2 — Use one tensor notation, declared once

*Severity: major · Check: hybrid · Scope: global*

Choose direct (bold: σ, **C**), index (σ_ij, C_ijkl), or Voigt notation;
declare the convention (including order of tensors by font/decoration:
e.g., lowercase bold = vector, uppercase bold = second-order tensor,
blackboard/calligraphic = fourth-order) near the first equation; never mix
notations within one derivation without an explicit conversion statement.

**Rationale:** Mechanics papers live and die by their tensor algebra being
followable. Mixed notation is the field's most common MA-2 violation.

**How to check:** Deterministic: detect co-occurrence of index-notation and
bold-symbol forms of the same quantities; detect Voigt-matrix forms.
LLM: check the convention paragraph exists and is obeyed; check operator
symbols (·, :, ⊗) are defined (MA-1).

**Examples:**
- ✗ Equation (4) in direct notation, equation (5) continuing in indices with
  no remark.
- ✓ "Throughout, lowercase/uppercase bold symbols denote vectors and
  second-order tensors; : denotes double contraction." — and the paper
  sticks to it.

## FS-3 — Report convergence the standard way

*Severity: major · Check: hybrid · Scope: section*

Convergence studies report the error norm used (L², energy, max), the
reference solution, and the observed rate — plotted log–log with a
reference-slope triangle (FG-2) and, where meaningful, tabulated rates.

**Rationale:** "The method converges" without norm, reference, and rate is
unreviewable; the log–log-with-slope-marker format is the field's lingua
franca.

**How to check:** In convergence sections, check: norm defined? reference
solution stated? rate quantified (number, not adjective)? plot log–log?
Flag qualitative claims ("converges rapidly", "excellent agreement") without
quantification.

**Examples:**
- ✗ "The error decreases quickly with mesh refinement (Figure 6)."
- ✓ "The L²-error converges at the expected rate of 2.0 (Figure 6,
  reference triangle)."

## FS-4 — State the full simulation setup, reproducibly

*Severity: major · Check: llm · Scope: section*

Every numerical example states: geometry and units, material parameters
(with sources), boundary/initial conditions, discretization (element/particle
type, characteristic size, e.g. horizon δ and m-ratio in peridynamics),
solver and tolerances, and — where applicable — code availability.

**Rationale:** Irreproducible examples are the field's chronic disease and
an increasingly frequent rejection reason; journals and funders now expect
data/code statements.

**How to check:** For each numerical example, tick the checklist above; flag
parameters appearing in figures but never given a value; flag dimensionless
plots whose normalization is undefined.

**Examples:**
- ✗ A peridynamic fracture example that never states horizon size or the
  horizon-to-spacing ratio.
- ✓ "δ = 3Δx with Δx = 0.5 mm (m = 3); parameters in Table 2; code at
  doi:…"

## FS-5 — Attribute material behavior precisely

*Severity: major · Check: llm · Scope: sentence*

Properties belong to the right level of the modeling hierarchy: the
*material* exhibits behavior, the *model* assumes it, the *specimen/response*
shows it. Standard pairs: stress *state* vs. stress *tensor*; *strength*
(stress level) vs. *toughness* (energy); *ductile/brittle* describe failure
modes, not materials per se; a *law* is constitutive, a *balance* is
universal.

**Rationale:** This is LG-1 specialized to mechanics — the misattributions
listed are the ones reviewers in this field actually flag.

**How to check:** Scan for the trap pairs: "nonlinear material" (→ nonlinear
material *response/behavior*), "the stress converges" (→ the stress *field*
in the discrete solution converges), "magnesium is brittle" (→ "the alloy
shows quasi-brittle failure under …"), strength/toughness swaps, "plastic
strain rate" vs. "rate of plastic strain" ambiguities.

**Examples:**
- ✗ "Due to the nonlinear material, the simulation requires small steps."
- ✓ "Due to the nonlinear material response, the simulation requires small
  load steps."

## FS-6 — Position novelty against the named state of the art

*Severity: major · Check: llm · Scope: section*

In this field, the novelty paragraph (ST-2) must name the specific methods
it improves upon (e.g., "in contrast to existing PD–FEM coupling schemes
[x–z], the proposed approach requires no overlap region") rather than generic
claims ("a novel framework is proposed").

**Rationale:** CMAME/JMPS reviewers are typically the authors of methods
x–z; vague novelty claims read as either ignorance of or disrespect for
their work, and "framework"-novelty without a falsifiable differentiator is
a standing rejection reason.

**How to check:** In the novelty paragraph, verify every claimed contribution
(i) names the closest existing approaches with citations and (ii) states a
checkable differentiator (a property, capability, or cost the prior methods
lack).

**Examples:**
- ✗ "We present a novel machine-learning framework for constitutive
  modeling."
- ✓ "Unlike black-box neural constitutive models [4,7], the proposed
  architecture satisfies polyconvexity and thermodynamic consistency by
  construction."
