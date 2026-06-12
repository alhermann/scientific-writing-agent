## FG-? — Use colorblind-safe palettes

*Severity: major · Check: deterministic · Scope: global*

Use colorblind-safe color palettes (e.g., viridis) in all figures to ensure accessibility for all readers.

**Rationale:** Approximately 8% of male readers are red-green colorblind, and using unsafe color combinations can make figures difficult or impossible to interpret for these readers.

**How to check:** Inspect all figures for color combinations and replace any that are not colorblind-safe with a palette like viridis.

**Examples:**
- ✗ A figure uses a red-to-green color scale.
- ✓ A figure uses a viridis color scale.

**Provenance:** distilled from manuscript feedback on 2026-06-12
