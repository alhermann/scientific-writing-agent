# Figures & tables

Rules on visual material. Figures are read before the text — often *instead*
of the text — so defects here have outsized impact.

## FG-1 — Make figure text large enough (and not larger)

*Severity: major · Check: hybrid · Scope: global*

All text inside figures (axis labels, legends, tick numbers, annotations)
must be approximately the font size of the figure caption — neither smaller
nor conspicuously larger.

**Rationale:** Too-small text forces tedious zooming and distracts from the
science; oversized text looks strange and wastes space.

**How to check:** Deterministic (when source available): compare font sizes
in vector graphics / matplotlib scripts against document font size and
`\includegraphics` scaling. Visual/LLM: inspect rendered figures at print
size; flag any label that would be < ~80 % or > ~150 % of caption size.

**Examples:**
- ✗ A matplotlib default-size figure scaled to 0.45\textwidth — tick labels
  become ~4 pt.
- ✓ Setting figure size and font so labels print at 8–10 pt in the final
  layout.

## FG-2 — Choose the axis scale that carries the message

*Severity: major · Check: llm · Scope: global*

For every function plot, deliberately choose linear, semi-logarithmic, or
log–log axes — whichever makes the key message visible. Convergence plots
almost always demand log–log (algebraic rates) or semi-log (exponential
rates).

**Rationale:** On the wrong scale the message disappears: algebraic
convergence on linear axes is an uninformative hockey stick; on log–log it is
a straight line whose slope *is* the result.

**How to check:** For each plot, identify the message (rate, saturation,
power law, relative differences over decades) and check the scale matches.
Flag convergence/error plots on linear axes; flag log scales where data spans
less than one decade.

**Examples:**
- ✗ Error vs. element size on linear axes, all points crowded near zero.
- ✓ Log–log error plot with a reference-slope triangle annotating the rate.

## FG-3 — Keep overlapping curves distinguishable

*Severity: major · Check: llm · Scope: global*

When curves (nearly) coincide — e.g., experiment vs. well-fitting simulation
— style them so both remain visible: one solid, one dashed, in clearly
different colors. Perfect overlap then shows as an alternating-color dashed
line, which is itself the message.

**Rationale:** Two identically-styled overlapping curves are
indistinguishable from one curve; the reader cannot see the agreement that is
the very point of the figure.

**How to check:** Flag plots comparing model vs. reference where line styles
do not differ in both dash pattern and color; check legends distinguish all
curves.

**Examples:**
- ✗ Simulation and experiment both as thin solid blue lines.
- ✓ Experiment: solid gray, thick; simulation: dashed red, on top.

## FG-4 — Keep captions short and message-bearing

*Severity: major · Check: hybrid · Scope: section*

Each caption conveys the central message of the figure — and nothing more.
Lengthy explanations belong in the main text.

**Rationale:** Captions are read in figure-skimming mode; a caption that is a
paragraph defeats that mode, and explanation duplicated from the text
violates SL-3.

**How to check:** Deterministic: flag captions > ~3 lines (~50 words).
LLM: check the caption states what the figure *shows* (message), not how it
was produced (methods), and that the figure is interpretable from
caption + legend alone.

**Examples:**
- ✗ Eight-line caption re-deriving the loading protocol.
- ✓ "Fracture pattern at final load: the model (right) reproduces the
  experimentally observed branching (left)."

## FG-5 — Make every figure self-contained and referenced

*Severity: major · Check: hybrid · Scope: global*

Every figure/table must be referenced in the text, appear near its first
reference, and be interpretable without hunting through the text (axes
labeled with quantity and unit, legend complete).

**Rationale:** Unreferenced figures signal leftover material (cf. TX-1);
unlabeled axes make a figure scientifically void.

**How to check:** Deterministic: cross-check `\ref`/figure-number usage
against figure environments; check axis-label presence in sources. LLM:
verify labels carry units and the figure stands alone.

**Examples:**
- ✗ A contour plot whose colorbar has no quantity or unit.
- ✓ Colorbar labeled "von Mises stress σ_v [MPa]".
