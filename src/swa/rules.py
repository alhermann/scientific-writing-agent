"""Parse the versioned guideline catalogue into rule objects.

The guideline files in ``guidelines/`` follow the contract specified in
``guidelines/00-meta.md``::

    ## SL-1 — Follow a single storyline

    *Severity: critical · Check: llm · Scope: global*

    <body until the next rule heading>

This module is intentionally dependency-free (stdlib only).
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

# "## SL-1 — Title" (em dash, en dash or hyphen accepted)
_RULE_HEADING = re.compile(r"^##\s+([A-Z]{2}-\d+)\s+[—–-]\s+(.+?)\s*$", re.MULTILINE)
_META_LINE = re.compile(
    r"\*Severity:\s*(?P<severity>\w+)\s*[·,;|]\s*"
    r"Check:\s*(?P<check>\w+)\s*[·,;|]\s*"
    r"Scope:\s*(?P<scope>[\w-]+)\s*\*"
)
_RETIRED = re.compile(r"\*\(retired\s+(\d{4}-\d{2}-\d{2})", re.IGNORECASE)

CATEGORY_NAMES = {
    "SL": "Storyline & narrative",
    "ST": "Structure",
    "LG": "Language & style",
    "MA": "Mathematics & nomenclature",
    "FG": "Figures & tables",
    "CI": "Citations & bibliography",
    "TX": "LaTeX & typesetting hygiene",
    "WF": "Workflow before writing",
    "FS": "Field-specific (computational mechanics & materials)",
}


@dataclass
class Rule:
    """One guideline rule."""

    id: str
    title: str
    severity: str  # critical | major | minor
    check: str  # llm | deterministic | hybrid
    scope: str  # global | section | sentence
    body: str  # full markdown body (rationale, how-to-check, examples)
    source_file: str
    retired: bool = False

    @property
    def category(self) -> str:
        return self.id.split("-", 1)[0]

    @property
    def category_name(self) -> str:
        return CATEGORY_NAMES.get(self.category, self.category)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity,
            "check": self.check,
            "scope": self.scope,
            "category": self.category,
            "category_name": self.category_name,
            "retired": self.retired,
            "source_file": self.source_file,
        }

    def to_markdown(self) -> str:
        return (
            f"## {self.id} — {self.title}\n\n"
            f"*Severity: {self.severity} · Check: {self.check} · "
            f"Scope: {self.scope}*\n\n{self.body.strip()}\n"
        )


@dataclass
class Catalogue:
    """The full, parsed guideline catalogue."""

    rules: list[Rule] = field(default_factory=list)
    guidelines_dir: Path | None = None

    def get(self, rule_id: str) -> Rule | None:
        rid = rule_id.strip().upper()
        return next((r for r in self.rules if r.id == rid), None)

    def filter(
        self,
        category: str | None = None,
        severity: str | None = None,
        check: str | None = None,
        include_retired: bool = False,
    ) -> list[Rule]:
        out = []
        for r in self.rules:
            if r.retired and not include_retired:
                continue
            if category and r.category != category.strip().upper():
                continue
            if severity and r.severity != severity.strip().lower():
                continue
            if check and r.check != check.strip().lower():
                continue
            out.append(r)
        return out

    @property
    def categories(self) -> list[str]:
        seen: list[str] = []
        for r in self.rules:
            if r.category not in seen:
                seen.append(r.category)
        return seen


def find_guidelines_dir(start: Path | None = None) -> Path:
    """Locate the guidelines directory.

    Resolution order:
      1. ``SWA_GUIDELINES_DIR`` environment variable
      2. ``guidelines/`` walking up from *start* (default: cwd)
      3. ``guidelines/`` relative to the repository containing this package
    """
    env = os.environ.get("SWA_GUIDELINES_DIR")
    if env:
        p = Path(env).expanduser()
        if p.is_dir():
            return p
        raise FileNotFoundError(f"SWA_GUIDELINES_DIR={env} is not a directory")

    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        g = candidate / "guidelines"
        if (g / "00-meta.md").is_file():
            return g

    # installed package: src/swa/rules.py -> repo root two levels up
    pkg_root = Path(__file__).resolve().parents[2]
    g = pkg_root / "guidelines"
    if (g / "00-meta.md").is_file():
        return g

    raise FileNotFoundError(
        "Could not locate the guidelines directory. Set SWA_GUIDELINES_DIR "
        "or run from inside the repository."
    )


def parse_file(path: Path) -> list[Rule]:
    text = path.read_text(encoding="utf-8")
    rules: list[Rule] = []
    matches = list(_RULE_HEADING.finditer(text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[m.end() : end]
        meta = _META_LINE.search(block)
        if not meta:
            # malformed rule: keep it visible rather than dropping it silently
            severity, check, scope = "unknown", "unknown", "unknown"
            body = block.strip()
        else:
            severity = meta.group("severity").lower()
            check = meta.group("check").lower()
            scope = meta.group("scope").lower()
            body = block[meta.end() :].strip()
        rules.append(
            Rule(
                id=m.group(1),
                title=m.group(2).strip(),
                severity=severity,
                check=check,
                scope=scope,
                body=body,
                source_file=path.name,
                retired=bool(_RETIRED.search(block)),
            )
        )
    return rules


def load_catalogue(guidelines_dir: Path | None = None) -> Catalogue:
    gdir = guidelines_dir or find_guidelines_dir()
    rules: list[Rule] = []
    for path in sorted(gdir.glob("[0-9][0-9]-*.md")):
        if path.name.startswith("00-"):
            continue  # format spec, not rules
        rules.extend(parse_file(path))
    return Catalogue(rules=rules, guidelines_dir=gdir)
