"""MCP server exposing the guideline catalogue and manuscript checks.

This is Track A's machine interface: any MCP client (Claude Code, Claude
Desktop, VS Code, a LangGraph agent, …) connects to this server and gets

  * the versioned writing guidelines as context (resources/tools),
  * deterministic manuscript and bibliography linting,
  * the review and feedback-distillation protocols,
  * a safe way to file new rule proposals (the learning loop).

Run:  swa-mcp            (stdio transport, for local clients)
      SWA_GUIDELINES_DIR=/path/to/guidelines swa-mcp

Requires the ``mcp`` extra:  pip install -e ".[mcp]"
"""

from __future__ import annotations

import datetime as _dt
import json
import re

from mcp.server.fastmcp import FastMCP

from . import rules as _rules
from . import checks as _checks
from . import manuscript as _manuscript
from .bibliography import check_bibliography as _check_bib
from .report import render_markdown

mcp = FastMCP(
    "scientific-writing",
    instructions=(
        "Guideline-driven scientific-writing assistant for a computational "
        "mechanics research group. Use get_review_protocol() "
        "to learn how to review a manuscript, list_rules()/get_rule() for "
        "the guideline catalogue, run_deterministic_checks() for LLM-free "
        "linting, and get_distillation_protocol()/save_rule_proposal() to "
        "feed revision feedback back into the guidelines."
    ),
)


def _catalogue() -> _rules.Catalogue:
    # re-load on every call: the guidelines are a living document
    return _rules.load_catalogue()


# ---------------------------------------------------------------------------
# Guideline access
# ---------------------------------------------------------------------------

@mcp.tool()
def list_rules(category: str = "", severity: str = "", check: str = "") -> str:
    """List all writing-guideline rules, optionally filtered.

    Args:
        category: rule prefix (SL, ST, LG, MA, FG, CI, TX, WF, FS) or empty.
        severity: critical | major | minor, or empty.
        check: llm | deterministic | hybrid, or empty.
    """
    cat = _catalogue()
    rs = cat.filter(category or None, severity or None, check or None)
    return json.dumps([r.to_dict() for r in rs], indent=2)


@mcp.tool()
def get_rule(rule_id: str) -> str:
    """Return the full markdown of one rule (e.g. 'SL-1'), including
    rationale, how-to-check instructions, and examples."""
    rule = _catalogue().get(rule_id)
    if rule is None:
        return f"Unknown rule '{rule_id}'. Use list_rules() for valid IDs."
    return rule.to_markdown()


@mcp.tool()
def get_guidelines(category: str = "") -> str:
    """Return the complete guideline text — all categories, or one category
    by prefix (SL, ST, LG, MA, FG, CI, TX, WF, FS). Load this as context
    before reviewing or polishing a manuscript."""
    cat = _catalogue()
    rs = cat.filter(category or None)
    if not rs:
        return f"No rules found for category '{category}'."
    out, current = [], None
    for r in rs:
        if r.category != current:
            current = r.category
            out.append(f"# {r.category_name} ({r.category})\n")
        out.append(r.to_markdown())
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Deterministic manuscript checks
# ---------------------------------------------------------------------------

@mcp.tool()
def run_deterministic_checks(manuscript_path: str, as_markdown: bool = True) -> str:
    """Run all LLM-free checks (language patterns, structure metrics, LaTeX
    hygiene, figure referencing) on a LaTeX or Markdown manuscript and return
    the findings. Findings marked 'candidate' need semantic confirmation."""
    ms = _manuscript.load(manuscript_path)
    findings = _checks.run_all(ms)
    if as_markdown:
        return render_markdown(findings, title="Deterministic check report",
                               source=str(ms.path))
    return json.dumps([f.to_dict() for f in findings], indent=2)


@mcp.tool()
def analyze_structure(manuscript_path: str) -> str:
    """Return the structural skeleton of a manuscript: sections with levels,
    line ranges and word counts, plus abstract/introduction statistics.
    Use this to plan a review and to check rules ST-1…ST-5."""
    ms = _manuscript.load(manuscript_path)
    return json.dumps(ms.structure_summary(), indent=2)


@mcp.tool()
def get_section_text(manuscript_path: str, section_title_fragment: str) -> str:
    """Return the full text of the first section whose title contains the
    given fragment (case-insensitive), e.g. 'introduction'."""
    ms = _manuscript.load(manuscript_path)
    sec = ms.section(section_title_fragment)
    if sec is None:
        titles = [s.title for s in ms.sections]
        return f"No section matching '{section_title_fragment}'. Sections: {titles}"
    return f"## {sec.title} (lines {sec.start_line}–{sec.end_line})\n\n{sec.text}"


@mcp.tool()
def check_bibliography(bib_path: str, tex_path: str = "") -> str:
    """Lint a BibTeX file (rules CI-1…CI-3): missing fields, truncated author
    lists, particle surnames without brace protection, mixed journal-name
    styles. If tex_path is given, also cross-check \\cite keys both ways."""
    findings = _check_bib(bib_path, tex_path or None)
    return render_markdown(findings, title="Bibliography check report",
                           source=bib_path)


# ---------------------------------------------------------------------------
# Protocols (instructions for the LLM side of hybrid/llm rules)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_review_protocol() -> str:
    """Return the step-by-step protocol for performing a full manuscript
    review against the guideline catalogue. Follow it exactly."""
    return REVIEW_PROTOCOL


@mcp.tool()
def get_distillation_protocol() -> str:
    """Return the protocol for distilling manuscript/revision feedback into
    new guideline-rule proposals (the learning loop)."""
    return DISTILLATION_PROTOCOL


# ---------------------------------------------------------------------------
# Learning loop
# ---------------------------------------------------------------------------

@mcp.tool()
def save_rule_proposal(slug: str, rule_markdown: str) -> str:
    """File a new guideline-rule proposal in guidelines/proposals/ for human
    curation. 'slug' is a short kebab-case name; 'rule_markdown' must follow
    the format of guidelines/00-meta.md including a Provenance line.
    Never edits the category files directly."""
    cat = _catalogue()
    assert cat.guidelines_dir is not None
    proposals = cat.guidelines_dir / "proposals"
    proposals.mkdir(exist_ok=True)
    slug = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-") or "proposal"
    date = _dt.date.today().isoformat()
    path = proposals / f"{date}-{slug}.md"
    counter = 1
    while path.exists():
        counter += 1
        path = proposals / f"{date}-{slug}-{counter}.md"
    if "Provenance" not in rule_markdown:
        return ("Rejected: the proposal must contain a '**Provenance:**' line "
                "(see guidelines/00-meta.md).")
    path.write_text(rule_markdown.rstrip() + "\n", encoding="utf-8")
    return f"Proposal saved to {path}. A maintainer curates it into the catalogue."


REVIEW_PROTOCOL = """\
# Manuscript review protocol

You are reviewing a scientific manuscript against the group's versioned
writing guidelines. Work through these steps in order; do not skip any.

1. **Orient.** Call analyze_structure() on the manuscript. Note abstract and
   introduction word counts and the section outline.
2. **Lint.** Call run_deterministic_checks() (and check_bibliography() if a
   .bib file exists). Keep the findings; verify every finding marked
   'candidate' yourself before reporting it.
3. **Load the rules.** Call get_guidelines() — or per category while working.
4. **Semantic review, category by category**, in this order (most important
   first): SL → ST → MA → FS → FG → LG → CI/TX/WF.
   For each rule with Check = llm or hybrid, follow its "How to check"
   instructions literally against the manuscript text. Read the manuscript
   sections via get_section_text() as needed.
5. **Report.** Produce one markdown report:
   - header: manuscript, date, guideline version (git hash if available)
   - findings grouped by severity (critical → major → minor), each with
     rule ID, location (line/section), quoted excerpt, explanation, and a
     concrete suggested rewrite where possible
   - end with the three highest-impact improvements as a short list.
6. **Honesty rules.** Never invent line numbers. Quote excerpts verbatim.
   If a rule cannot be checked from the given material (e.g., figures not
   provided), say so explicitly under "Not checked".
"""

DISTILLATION_PROTOCOL = """\
# Feedback distillation protocol (the learning loop)

Input: feedback from a supervisor/reviewer on a manuscript (comments,
annotated PDF text, review reports) — and ideally the manuscript itself.

1. **Split** the feedback into atomic items (one criticism/advice each).
2. **Classify** each item:
   a. instance of an EXISTING rule → note rule ID; if the feedback adds a
      genuinely new example or sharper wording, propose folding it in;
   b. genuinely NEW, generalizable principle → draft a new rule;
   c. manuscript-specific, not generalizable → drop (list under 'dropped').
3. **Abstract** each new rule away from the specific manuscript: no project
   nouns, no author names, phrased so it applies to any future paper.
4. **Draft** each new rule in the exact format of guidelines/00-meta.md:
   heading with the next free ID in the best-fitting category, metadata line
   (severity, check type, scope), normative statement, rationale,
   how-to-check, ✗/✓ examples, and a Provenance line
   ('distilled from <source> on <date>').
5. **File** each draft via save_rule_proposal(). NEVER edit the category
   files directly — proposals are curated by a human maintainer.
6. **Summarize** to the user: matched rules, new proposals (paths), dropped
   items. The summary is the audit trail of the learning loop.
"""


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
