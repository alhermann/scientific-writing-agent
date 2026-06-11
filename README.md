# Scientific Writing Agent

Guideline-driven agent system for scientific writing and manuscript revision,
developed for an academic research group in computational mechanics and
materials modeling.

The core of this repository is not code — it is
[`guidelines/`](guidelines/): a **versioned, machine-readable catalogue of
writing and revision rules**, initially distilled from an internal
*Check-list for scientific publications* and designed to grow with every
feedback round the group goes through (see
[How the system learns](#how-the-system-learns)).

Two tracks consume the same catalogue:

```
                       ┌──────────────────────────────┐
                       │   guidelines/  (the asset)    │
                       │   SL ST LG MA FG CI TX WF FS  │
                       └──────┬───────────────┬───────┘
            Track A           │               │           Track B
   ┌──────────────────────────┴──┐         ┌──┴──────────────────────────┐
   │ Off-the-shelf agents        │         │ Custom-built agent          │
   │                             │         │                             │
   │ .claude/skills/  (Claude    │         │ LangGraph pipeline          │
   │   Code: /review-manuscript, │         │   load ─► lint ─► semantic  │
   │   /distill-feedback, …)     │         │   review ─► report          │
   │ MCP server (swa-mcp) for    │         │   + distillation graph      │
   │   ANY MCP client            │         │ CLI: swa review / distill   │
   └─────────────────────────────┘         └─────────────────────────────┘
```

- **Track A — off-the-shelf**: open this repository in Claude Code (or
  connect any MCP client to the bundled MCP server) and you have a manuscript
  reviewer today, zero custom code running.
- **Track B — custom-built**: a ground-up [LangGraph](https://github.com/langchain-ai/langgraph)
  agent with a deterministic linting layer and per-category semantic review,
  usable from the command line or as a library, model-agnostic.

## Quick start

### Track A · Claude Code (no installation)

```bash
git clone <this-repo> && cd Scientific-Writing-Agent
claude
> /review-manuscript path/to/paper.tex
> /distill-feedback path/to/reviewer-comments.txt
> /plan-paper
```

### Track A · MCP server (any MCP client)

```bash
pip install -e ".[mcp]"
```

Claude Code: `claude mcp add scientific-writing -- swa-mcp`
Claude Desktop / others (stdio):

```json
{ "mcpServers": { "scientific-writing": { "command": "swa-mcp" } } }
```

Tools exposed: `get_guidelines`, `list_rules`, `get_rule`,
`run_deterministic_checks`, `analyze_structure`, `get_section_text`,
`check_bibliography`, `get_review_protocol`, `get_distillation_protocol`,
`save_rule_proposal`. Point the server at the central catalogue with
`SWA_GUIDELINES_DIR` if you run it outside this repo.

### Track B · Custom LangGraph agent

```bash
pip install -e ".[agent]"
export ANTHROPIC_API_KEY=…           # or any provider; see SWA_MODEL below

swa review paper.tex --out review.md   # full guideline review
swa distill feedback.txt --manuscript paper.tex   # learning loop
```

Model selection: `SWA_MODEL` (default `anthropic:claude-sonnet-4-6`), any
[init_chat_model](https://python.langchain.com/docs/how_to/chat_models_universal_init/)
provider string works.

**Which model should I use?**

| You have… | Use | How |
|-----------|-----|-----|
| An Anthropic/OpenAI/… API key | Track B, frontier model | `export ANTHROPIC_API_KEY=…` (best review quality) |
| A Helmholtz account | Track B via **[Blablador](https://helmholtz-blablador.fz-juelich.de)** — free, manuscripts stay on Helmholtz infrastructure | `SWA_MODEL="openai:<alias>"`, `SWA_BASE_URL="https://api.helmholtz-blablador.fz-juelich.de/v1"`, `SWA_API_KEY=<key>` |
| A GPU and privacy requirements | Track B via Ollama/vLLM (open weights) | `SWA_MODEL="openai:<model>"`, `SWA_BASE_URL="http://localhost:11434/v1"` — realistically needs ≳70B-class models for useful reviews |
| A Claude Pro/Max subscription | **Track A** — skills + MCP inside Claude Code | chat subscriptions cannot back an API pipeline; in Claude Code your subscription pays for the inference |

### LLM-free tools (base install, stdlib only)

```bash
pip install -e .
swa rules --category SL --full   # browse the catalogue
swa lint paper.tex               # deterministic checks
swa bib refs.bib --tex paper.tex # bibliography lint
swa structure paper.tex          # structural skeleton
```

## How the system learns

Every supervisor or reviewer feedback round is **distilled**: the agent
abstracts the generalizable core of each comment into a rule proposal
(`guidelines/proposals/`), a human maintainer curates proposals into the
catalogue, and every future review — by anyone in the group — applies the
lesson automatically. The full process: [CONTRIBUTING.md](CONTRIBUTING.md).

This is deliberate design, not a limitation: rules enter the catalogue only
through human curation, so the catalogue stays trustworthy and the system's
behavior stays explainable — every finding cites a versioned rule with
provenance.

## Repository layout

| Path | Content |
|------|---------|
| `guidelines/` | The rule catalogue (single source of truth) + `proposals/` inbox |
| `.claude/skills/` | Track A: skills for Claude Code |
| `src/swa/` | Shared core: rule parser, manuscript model, deterministic checks |
| `src/swa/mcp_server.py` | Track A: MCP server |
| `src/swa/agent/` | Track B: LangGraph graphs (review + distillation) |
| `tests/` | Smoke tests incl. an intentionally flawed example manuscript |

## Design decisions

- **Guidelines over weights.** The system's knowledge lives in versioned
  markdown, not in a fine-tuned model: inspectable, diff-able, transferable
  to any future model or framework.
- **Deterministic before semantic.** Everything checkable without an LLM
  (`swa lint`) is checked without an LLM — reproducible, free, and it keeps
  the LLM focused on the judgement calls (storyline, logical gaps, accuracy).
- **Stdlib core.** Rule parsing and linting have zero dependencies; the MCP
  server and the LangGraph agent are optional extras on top.
- **Human-curated learning.** Proposals never auto-merge. See above.

## License

MIT — see [LICENSE](LICENSE).
