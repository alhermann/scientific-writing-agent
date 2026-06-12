"""LangGraph pipelines: manuscript review and feedback distillation.

Review graph
------------

    load_and_lint ──► review_category ──► synthesize ──► END
                        ▲   │ (loop while categories pending)
                        └───┘

The deterministic layer (swa.checks) runs once; the LLM then reviews one
rule category per step, each with only the rules and manuscript context it
needs. A loop instead of a parallel fan-out keeps token use observable and
the graph trivially debuggable — parallelize later if review time matters.

Distillation graph
------------------

    distill ──► save_proposals ──► END

Model selection (env vars):
    SWA_MODEL     provider:model for langchain's init_chat_model
                  (default "anthropic:claude-sonnet-4-6")
    SWA_BASE_URL  OpenAI-compatible endpoint for self-hosted / academic
                  inference — e.g. Helmholtz Blablador (free for Helmholtz
                  employees, manuscripts stay on Helmholtz infrastructure),
                  GWDG Chat AI, vLLM, or Ollama's OpenAI endpoint.
                  Use with SWA_MODEL="openai:<model-name>".
    SWA_API_KEY   key for that endpoint (falls back to the provider's
                  standard variable, e.g. ANTHROPIC_API_KEY/OPENAI_API_KEY)

Examples:
    # Anthropic API (default)
    export ANTHROPIC_API_KEY=…

    # Helmholtz Blablador (free, on-premise for Helmholtz staff)
    export SWA_MODEL="openai:alias-large"
    export SWA_BASE_URL="https://api.helmholtz-blablador.fz-juelich.de/v1"
    export SWA_API_KEY=<your blablador key>

    # local Ollama
    export SWA_MODEL="openai:qwen3:32b"
    export SWA_BASE_URL="http://localhost:11434/v1"
    export SWA_API_KEY=ollama

Note on subscriptions: chat subscriptions (Claude Pro/Max, ChatGPT) cannot
back an API pipeline like this one — subscription users should use Track A
(the skills + MCP server inside Claude Code) instead, where inference runs
on their subscription.
"""

from __future__ import annotations

import datetime as _dt
import os
import re

from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph

from .. import checks as _checks
from .. import manuscript as _manuscript
from .. import rules as _rules
from ..report import render_markdown
from .state import CategoryReview, Distillation, DistillState, ReviewState

# Review order: most important categories first (storyline before polish).
CATEGORY_ORDER = ["SL", "ST", "MA", "FS", "FG", "LG", "CI", "TX", "WF"]

_MAX_MANUSCRIPT_CHARS = 120_000  # ~30k tokens; truncate beyond with a notice


def _suffix(prompt: str) -> str:
    """Append SWA_PROMPT_SUFFIX to every prompt (e.g. '/no_think' to disable
    qwen3 thinking mode on slow hardware)."""
    return prompt + os.environ.get("SWA_PROMPT_SUFFIX", "")


def _llm():
    model = os.environ.get("SWA_MODEL", "anthropic:claude-sonnet-4-6")
    # Cap generation: small models can loop in constrained-JSON mode; without
    # a cap they burn the whole context (and hours of CPU) before failing.
    kwargs: dict = {"temperature": 0,
                    "max_tokens": int(os.environ.get("SWA_MAX_TOKENS", "6000"))}
    if os.environ.get("SWA_BASE_URL"):
        kwargs["base_url"] = os.environ["SWA_BASE_URL"]
    if os.environ.get("SWA_API_KEY"):
        kwargs["api_key"] = os.environ["SWA_API_KEY"]
    return init_chat_model(model, **kwargs)


def _manuscript_context(path: str) -> str:
    ms = _manuscript.load(path)
    text = ms.text
    if len(text) > _MAX_MANUSCRIPT_CHARS:
        text = (text[:_MAX_MANUSCRIPT_CHARS]
                + "\n\n[... manuscript truncated for context length ...]")
    return text


# ---------------------------------------------------------------------------
# Review graph nodes
# ---------------------------------------------------------------------------

def load_and_lint(state: ReviewState) -> ReviewState:
    ms = _manuscript.load(state["manuscript_path"])
    findings = _checks.run_all(ms)
    catalogue = _rules.load_catalogue()
    pending = [c for c in CATEGORY_ORDER if catalogue.filter(c)]
    return {
        "structure": ms.structure_summary(),
        "deterministic_report": render_markdown(
            findings, title="Deterministic findings", source=str(ms.path)),
        "pending_categories": pending,
        "category_reviews": [],
    }


def review_category(state: ReviewState) -> ReviewState:
    category = state["pending_categories"][0]
    catalogue = _rules.load_catalogue()
    rules_md = "\n".join(r.to_markdown() for r in catalogue.filter(category)
                         if r.check in {"llm", "hybrid"})
    if not rules_md:
        return {"pending_categories": state["pending_categories"][1:]}

    llm = _llm().with_structured_output(CategoryReview)
    prompt = f"""You are a meticulous scientific-writing reviewer for a \
computational mechanics research group. Review the manuscript below against \
ONLY the following guideline rules (category {category}). Follow each rule's \
"How to check" instructions literally.

Honesty requirements:
- Quote excerpts verbatim from the manuscript; never fabricate text.
- Use approximate locations (section names); never invent line numbers.
- If a rule cannot be checked from the given material (e.g., it needs \
rendered figures), list its ID under not_checked with a reason.
- Report only genuine violations — an empty findings list is a valid result.

## Rules

{rules_md}

## Manuscript structure

{state.get('structure')}

## Manuscript

{_manuscript_context(state['manuscript_path'])}
"""
    # Fault isolation: one failing category (model loops, schema mismatch,
    # endpoint hiccup) must not destroy the rest of the review.
    try:
        review = llm.invoke(_suffix(prompt))
        result = (review.model_dump() if hasattr(review, "model_dump")
                  else dict(review))
    except Exception as e:  # noqa: BLE001 — recorded, not swallowed
        result = {"findings": [],
                  "not_checked": [f"all {category} rules: review call failed "
                                  f"({type(e).__name__}: {str(e)[:200]})"]}
    result["category"] = category
    return {
        "pending_categories": state["pending_categories"][1:],
        "category_reviews": state.get("category_reviews", []) + [result],
    }


def synthesize(state: ReviewState) -> ReviewState:
    sections = [f"# Manuscript review — {state['manuscript_path']}",
                f"*{_dt.date.today().isoformat()} · generated by the "
                f"Scientific Writing Agent (LangGraph pipeline)*", ""]

    # collect LLM findings by severity
    sev_rank = {"critical": 0, "major": 1, "minor": 2}
    all_findings = [(f, r["category"])
                    for r in state.get("category_reviews", [])
                    for f in r.get("findings", [])]
    all_findings.sort(key=lambda x: sev_rank.get(x[0].get("severity", "minor"), 3))

    sections.append(f"## Semantic findings ({len(all_findings)})\n")
    for f, _cat in all_findings:
        sections.append(
            f"- **{f.get('rule_id')}** ({f.get('severity')}) — "
            f"{f.get('location')}\n"
            f"  > {f.get('excerpt')}\n\n  {f.get('message')}"
            + (f"\n  - 💡 {f['suggestion']}" if f.get("suggestion") else ""))
    sections.append("")

    not_checked = [(r["category"], nc)
                   for r in state.get("category_reviews", [])
                   for nc in r.get("not_checked", [])]
    if not_checked:
        sections.append("## Not checked\n")
        sections += [f"- {nc}" for _c, nc in not_checked]
        sections.append("")

    sections.append(state.get("deterministic_report", ""))

    # executive summary on top, written by the LLM from the findings
    body = "\n".join(sections)
    summary = _llm().invoke(_suffix(
        "Write a 5-10 line executive summary of this manuscript review for "
        "the author: overall assessment, then the three highest-impact "
        "improvements as a numbered list. Be direct and specific; no praise "
        "padding. Review:\n\n" + body[:40_000])
    ).content
    report = body.replace(
        "## Semantic findings",
        f"## Executive summary\n\n{summary}\n\n## Semantic findings", 1)
    return {"report": report}


def _route_review(state: ReviewState) -> str:
    return "review_category" if state.get("pending_categories") else "synthesize"


def build_review_graph():
    g = StateGraph(ReviewState)
    g.add_node("load_and_lint", load_and_lint)
    g.add_node("review_category", review_category)
    g.add_node("synthesize", synthesize)
    g.add_edge(START, "load_and_lint")
    g.add_conditional_edges("load_and_lint", _route_review,
                            ["review_category", "synthesize"])
    g.add_conditional_edges("review_category", _route_review,
                            ["review_category", "synthesize"])
    g.add_edge("synthesize", END)
    return g.compile()


# ---------------------------------------------------------------------------
# Distillation graph nodes (the learning loop)
# ---------------------------------------------------------------------------

def distill(state: DistillState) -> DistillState:
    catalogue = _rules.load_catalogue()
    index = "\n".join(f"- {r.id}: {r.title} ({r.severity})"
                      for r in catalogue.filter())
    context = ""
    if state.get("manuscript_path"):
        context = ("\n## Manuscript (context)\n\n"
                   + _manuscript_context(state["manuscript_path"])[:40_000])

    llm = _llm().with_structured_output(Distillation)
    result = llm.invoke(_suffix(f"""You distill manuscript feedback into reusable \
writing guidelines for a research group (the learning loop of our writing \
agent).

Procedure:
1. Split the feedback into atomic items.
2. For each item decide: (a) instance of an existing rule (list under \
'matched' as 'RULE-ID: item'), (b) genuinely new generalizable principle \
(draft a proposal), (c) manuscript-specific (list under 'dropped').
3. Abstract new rules away from this manuscript: no project nouns or names; \
phrase them so they apply to any future paper.
4. Draft each proposal in EXACTLY this markdown format:

## XX-? — <imperative title>

*Severity: critical|major|minor · Check: llm|deterministic|hybrid · Scope: global|section|sentence*

<normative statement>

**Rationale:** <why>

**How to check:** <operational instructions>

**Examples:**
- ✗ <violating example (anonymized)>
- ✓ <corrected example>

**Provenance:** distilled from manuscript feedback on {_dt.date.today().isoformat()}

where XX is the best-fitting category of: SL (storyline), ST (structure), \
LG (language), MA (math/nomenclature), FG (figures), CI (citations), \
TX (LaTeX), WF (workflow), FS (field-specific mechanics). Keep the literal \
'?' in the heading — the maintainer assigns the final number.

## Existing rule index

{index}

## Feedback to distill

{state['feedback_text']}
{context}
"""))
    dump = result.model_dump() if hasattr(result, "model_dump") else dict(result)
    return {"distillation": dump}


def save_proposals(state: DistillState) -> DistillState:
    catalogue = _rules.load_catalogue()
    assert catalogue.guidelines_dir is not None
    proposals_dir = catalogue.guidelines_dir / "proposals"
    proposals_dir.mkdir(exist_ok=True)

    saved: list[str] = []
    date = _dt.date.today().isoformat()
    for p in state.get("distillation", {}).get("proposals", []):
        slug = re.sub(r"[^a-z0-9-]+", "-", p["slug"].lower()).strip("-") or "proposal"
        path = proposals_dir / f"{date}-{slug}.md"
        n = 1
        while path.exists():
            n += 1
            path = proposals_dir / f"{date}-{slug}-{n}.md"
        path.write_text(p["rule_markdown"].rstrip() + "\n", encoding="utf-8")
        saved.append(str(path))

    d = state.get("distillation", {})
    summary = "\n".join(
        ["# Feedback distillation summary", "",
         f"**New proposals ({len(saved)}):**"]
        + [f"- {s}" for s in saved]
        + ["", f"**Matched existing rules ({len(d.get('matched', []))}):**"]
        + [f"- {m}" for m in d.get("matched", [])]
        + ["", f"**Dropped as manuscript-specific ({len(d.get('dropped', []))}):**"]
        + [f"- {x}" for x in d.get("dropped", [])]
        + ["", "Next step: a maintainer reviews guidelines/proposals/ and "
               "merges accepted rules into the catalogue."])
    return {"saved_paths": saved, "summary": summary}


def build_distill_graph():
    g = StateGraph(DistillState)
    g.add_node("distill", distill)
    g.add_node("save_proposals", save_proposals)
    g.add_edge(START, "distill")
    g.add_edge("distill", "save_proposals")
    g.add_edge("save_proposals", END)
    return g.compile()
