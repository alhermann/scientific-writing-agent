"""Deterministic bibliography checks (CI rules) on BibTeX files.

A small, dependency-free BibTeX reader — robust enough for linting, not a
full parser. Stdlib only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .checks import Finding

_ENTRY_HEAD = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
_FIELD = re.compile(r"(\w+)\s*=\s*(\{|\")")

REQUIRED_FIELDS = {
    "article": ["author", "title", "journal", "volume", "year"],
    "book": ["author", "title", "publisher", "year"],
    "inproceedings": ["author", "title", "booktitle", "year"],
    "incollection": ["author", "title", "booktitle", "publisher", "year"],
    "phdthesis": ["author", "title", "school", "year"],
    "misc": ["author", "title", "year"],
}

# pages OR an article number ("articleno"/"eid"/elsevier "pages = {116234}")
_PAGES_LIKE = ("pages", "articleno", "eid", "article-number", "number")

_NAME_PARTICLES = re.compile(
    r"\b(van|von|de|der|den|del|della|di|da|le|la|ter|ten)\b", re.IGNORECASE
)


@dataclass
class BibEntry:
    key: str
    type: str
    line: int
    fields: dict[str, str] = field(default_factory=dict)


def _read_balanced(text: str, start: int) -> tuple[str, int]:
    """Read a {...} or "..." value starting at the opening delimiter."""
    open_ch = text[start]
    if open_ch == "{":
        depth, i = 1, start + 1
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        return text[start + 1 : i - 1], i
    # quoted
    i = start + 1
    while i < len(text) and text[i] != '"':
        i += 1
    return text[start + 1 : i], i + 1


def parse_bib(path: str | Path) -> list[BibEntry]:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    entries: list[BibEntry] = []
    for m in _ENTRY_HEAD.finditer(text):
        etype = m.group(1).lower()
        if etype in {"comment", "preamble", "string"}:
            continue
        entry = BibEntry(key=m.group(2), type=etype,
                         line=text[: m.start()].count("\n") + 1)
        pos = m.end()
        while pos < len(text):
            fm = _FIELD.match(text, pos) or _FIELD.search(text, pos, pos + 200)
            if not fm:
                break
            value, pos = _read_balanced(text, fm.end() - 1)
            entry.fields[fm.group(1).lower()] = " ".join(value.split())
            # stop at the closing brace of the entry
            nxt = re.compile(r"\s*,?\s*").match(text, pos)
            pos = nxt.end() if nxt else pos
            if pos < len(text) and text[pos] == "}":
                break
        entries.append(entry)
    return entries


def check_bibliography(bib_path: str | Path,
                       tex_path: str | Path | None = None) -> list[Finding]:
    findings: list[Finding] = []
    entries = parse_bib(bib_path)

    journal_styles = {"full": 0, "abbrev": 0}
    for e in entries:
        required = REQUIRED_FIELDS.get(e.type, ["author", "title", "year"])
        missing = [f for f in required if not e.fields.get(f)]
        if e.type == "article" and not any(e.fields.get(p) for p in _PAGES_LIKE):
            missing.append("pages/article number")
        if missing:
            findings.append(Finding(
                "CI-1", "major", e.line, e.key,
                f"@{e.type} '{e.key}' is missing: {', '.join(missing)}.",
                suggestion="Complete the entry from the publisher page or DOI."))

        author = e.fields.get("author", "")
        if re.search(r"\bothers\b|et al", author, re.IGNORECASE):
            findings.append(Finding(
                "CI-1", "major", e.line, e.key,
                f"'{e.key}' truncates the author list ('and others'/'et al.').",
                suggestion="List all authors; the bibliography style truncates "
                           "if the journal wants it."))
        # ignore TeX accent groups like {\'e} when looking for brace protection
        author_unaccented = re.sub(r"\{\\[^}]*\}", "", author)
        if _NAME_PARTICLES.search(author) and "{" not in author_unaccented:
            findings.append(Finding(
                "CI-2", "major", e.line, e.key,
                f"'{e.key}' has a multi-word/particle surname without brace "
                f"protection: '{author[:60]}'.",
                suggestion="Protect the surname: author = {{de Borst}, René}.",
                confidence="candidate"))

        journal = e.fields.get("journal", "")
        if journal:
            if "." in journal or re.fullmatch(r"[A-Z]{2,6}", journal):
                journal_styles["abbrev"] += 1
            else:
                journal_styles["full"] += 1

    if journal_styles["full"] and journal_styles["abbrev"]:
        findings.append(Finding(
            "CI-1", "major", None, "",
            f"Mixed journal-name styles: {journal_styles['full']} full vs. "
            f"{journal_styles['abbrev']} abbreviated.",
            suggestion="Use one style consistently (check the journal's "
                       "requirements)."))

    if tex_path is not None:
        tex = Path(tex_path).read_text(encoding="utf-8", errors="replace")
        cited: set[str] = set()
        for grp in re.findall(r"\\(?:no|short|text|paren)?cite[a-zA-Z*]*\s*"
                              r"(?:\[[^\]]*\]\s*)*\{([^}]+)\}", tex):
            cited |= {k.strip() for k in grp.split(",")}
        keys = {e.key for e in entries}
        for k in sorted(cited - keys):
            findings.append(Finding("CI-3", "major", None, k,
                                    f"\\cite{{{k}}} has no entry in the .bib file."))
        for k in sorted(keys - cited):
            findings.append(Finding(
                "CI-3", "minor", None, k,
                f"Bibliography entry '{k}' is never cited (orphan).",
                suggestion="Remove it or cite it.", confidence="candidate"))

    findings.sort(key=lambda f: (f.line or 0))
    return findings
