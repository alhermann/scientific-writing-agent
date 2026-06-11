"""Command-line interface.

LLM-free commands (work with the base install):
    swa rules [--category SL] [--severity critical]
    swa lint  paper.tex  [--json]
    swa bib   refs.bib   [--tex paper.tex]
    swa structure paper.tex

LLM commands (need ``pip install -e ".[agent]"`` and an API key):
    swa review  paper.tex  [--out review.md]
    swa distill feedback.txt  [--manuscript paper.tex]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import checks as _checks
from . import manuscript as _manuscript
from . import rules as _rules
from .bibliography import check_bibliography
from .report import render_markdown


def cmd_rules(args: argparse.Namespace) -> int:
    cat = _rules.load_catalogue()
    rs = cat.filter(args.category, args.severity)
    if args.full:
        for r in rs:
            print(r.to_markdown())
    else:
        for r in rs:
            print(f"{r.id:6s} {r.severity:9s} {r.check:13s} {r.title}")
    print(f"\n{len(rs)} rules (guidelines: {cat.guidelines_dir})", file=sys.stderr)
    return 0


def cmd_lint(args: argparse.Namespace) -> int:
    ms = _manuscript.load(args.manuscript)
    findings = _checks.run_all(ms)
    if args.json:
        print(json.dumps([f.to_dict() for f in findings], indent=2))
    else:
        print(render_markdown(findings, title="Deterministic check report",
                              source=str(ms.path)))
    return 1 if any(f.severity == "critical" for f in findings) else 0


def cmd_bib(args: argparse.Namespace) -> int:
    findings = check_bibliography(args.bibfile, args.tex)
    print(render_markdown(findings, title="Bibliography check report",
                          source=args.bibfile))
    return 0


def cmd_structure(args: argparse.Namespace) -> int:
    ms = _manuscript.load(args.manuscript)
    print(json.dumps(ms.structure_summary(), indent=2))
    return 0


def _require_agent_extra():
    try:
        import langgraph  # noqa: F401
    except ImportError:
        print("This command needs the agent extra:\n"
              '    pip install -e ".[agent]"\n'
              "and an API key (e.g. ANTHROPIC_API_KEY).", file=sys.stderr)
        raise SystemExit(2)


def cmd_review(args: argparse.Namespace) -> int:
    _require_agent_extra()
    from .agent.graph import build_review_graph

    graph = build_review_graph()
    print(f"Reviewing {args.manuscript} …", file=sys.stderr)
    final = graph.invoke({"manuscript_path": args.manuscript},
                         {"recursion_limit": 50})
    report = final["report"]
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"Report written to {args.out}", file=sys.stderr)
    else:
        print(report)
    return 0


def cmd_distill(args: argparse.Namespace) -> int:
    _require_agent_extra()
    from .agent.graph import build_distill_graph

    feedback = Path(args.feedback).read_text(encoding="utf-8")
    graph = build_distill_graph()
    final = graph.invoke({"feedback_text": feedback,
                          "manuscript_path": args.manuscript or ""})
    print(final["summary"])
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="swa",
                                description="Scientific Writing Agent")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("rules", help="list guideline rules")
    s.add_argument("--category", help="SL|ST|LG|MA|FG|CI|TX|WF|FS")
    s.add_argument("--severity", help="critical|major|minor")
    s.add_argument("--full", action="store_true", help="print full rule text")
    s.set_defaults(fn=cmd_rules)

    s = sub.add_parser("lint", help="deterministic checks on a manuscript")
    s.add_argument("manuscript")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_lint)

    s = sub.add_parser("bib", help="lint a BibTeX file")
    s.add_argument("bibfile")
    s.add_argument("--tex", help="cross-check \\cite keys against this .tex")
    s.set_defaults(fn=cmd_bib)

    s = sub.add_parser("structure", help="structural summary of a manuscript")
    s.add_argument("manuscript")
    s.set_defaults(fn=cmd_structure)

    s = sub.add_parser("review", help="full LLM review (LangGraph)")
    s.add_argument("manuscript")
    s.add_argument("--out", help="write the report to this file")
    s.set_defaults(fn=cmd_review)

    s = sub.add_parser("distill",
                       help="distill feedback into rule proposals (LangGraph)")
    s.add_argument("feedback", help="text file with the feedback")
    s.add_argument("--manuscript", help="optional manuscript for context")
    s.set_defaults(fn=cmd_distill)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
