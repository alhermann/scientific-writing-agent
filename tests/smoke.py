"""Smoke test: no LLM, no network, stdlib only.

Run from the repository root:  python -m tests.smoke
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from swa import checks, manuscript, rules  # noqa: E402
from swa.bibliography import check_bibliography  # noqa: E402
from swa.report import render_markdown  # noqa: E402

DATA = ROOT / "tests" / "data"
FAILURES: list[str] = []


def expect(cond: bool, msg: str) -> None:
    status = "ok  " if cond else "FAIL"
    print(f"  [{status}] {msg}")
    if not cond:
        FAILURES.append(msg)


def main() -> int:
    print("1. Guideline catalogue")
    cat = rules.load_catalogue(ROOT / "guidelines")
    expect(len(cat.rules) >= 35, f"catalogue parses ≥35 rules (got {len(cat.rules)})")
    expect(set(cat.categories) >= {"SL", "ST", "LG", "MA", "FG", "CI", "TX", "WF", "FS"},
           "all nine categories present")
    expect(all(r.severity in {"critical", "major", "minor"} for r in cat.rules),
           "every rule has a valid severity")
    expect(all(r.check in {"llm", "deterministic", "hybrid"} for r in cat.rules),
           "every rule has a valid check type")
    sl1 = cat.get("sl-1")
    expect(sl1 is not None and "storyline" in sl1.title.lower(),
           "get('sl-1') finds the single-storyline rule")
    expect(len(cat.filter(category="LG")) >= 6, "LG category has ≥6 rules")

    print("2. Manuscript model (LaTeX)")
    ms = manuscript.load(DATA / "flawed_example.tex")
    expect(ms.fmt == "latex", "format detected as latex")
    expect(ms.abstract is not None and ms.word_count > 100, "abstract + text extracted")
    expect(ms.introduction is not None, "introduction section found")
    expect(any(s.level == 2 for s in ms.sections), "subsections detected")

    print("3. Deterministic checks")
    findings = checks.run_all(ms)
    hit_rules = {f.rule_id for f in findings}
    for expected in ["LG-3", "LG-5", "LG-6", "LG-7", "ST-1", "ST-2",
                     "LG-4", "TX-1", "TX-2", "TX-3", "FG-5"]:
        expect(expected in hit_rules, f"{expected} fires on the flawed example")
    expect(all(f.line is None or 1 <= f.line <= len(ms.lines) for f in findings),
           "all line numbers within bounds")

    print("4. Bibliography checks")
    bfindings = check_bibliography(DATA / "flawed_refs.bib")
    brules = {f.rule_id for f in bfindings}
    expect("CI-1" in brules, "CI-1 fires (incomplete entry / 'and others')")
    expect("CI-2" in brules, "CI-2 fires (unprotected particle surname)")

    print("5. Report rendering")
    md = render_markdown(findings, source=str(ms.path))
    expect(md.startswith("# ") and "findings" in md, "markdown report renders")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURE(S):")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("All smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
