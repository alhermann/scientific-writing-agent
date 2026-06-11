"""Load and structure manuscripts (LaTeX and Markdown).

Produces a light structural model (abstract, sections, line-indexed text)
that the deterministic checks and the LLM review nodes operate on.
Stdlib only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_TEX_COMMENT = re.compile(r"(?<!\\)%.*$", re.MULTILINE)
_TEX_SECTION = re.compile(
    r"\\(?P<level>(?:sub){0,2}section)\*?\s*\{(?P<title>[^}]*)\}"
)
_MD_HEADING = re.compile(r"^(?P<hashes>#{1,4})\s+(?P<title>.+?)\s*$", re.MULTILINE)
_TEX_ABSTRACT = re.compile(
    r"\\begin\{abstract\}(?P<body>.*?)\\end\{abstract\}", re.DOTALL
)


@dataclass
class Section:
    title: str
    level: int  # 1 = section, 2 = subsection, 3 = subsubsection
    start_line: int  # 1-based, inclusive
    end_line: int  # 1-based, inclusive
    text: str

    @property
    def word_count(self) -> int:
        return count_words(self.text)


@dataclass
class Manuscript:
    path: Path
    fmt: str  # "latex" | "markdown"
    raw: str  # original source
    text: str  # comment-stripped source
    lines: list[str] = field(default_factory=list)
    abstract: str | None = None
    sections: list[Section] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        return count_words(self.text)

    def section(self, name_fragment: str) -> Section | None:
        frag = name_fragment.lower()
        return next(
            (s for s in self.sections if frag in s.title.lower()), None
        )

    @property
    def introduction(self) -> Section | None:
        return self.section("introduction")

    def structure_summary(self) -> dict:
        return {
            "path": str(self.path),
            "format": self.fmt,
            "total_words": self.word_count,
            "abstract_words": count_words(self.abstract) if self.abstract else None,
            "sections": [
                {
                    "title": s.title,
                    "level": s.level,
                    "lines": [s.start_line, s.end_line],
                    "words": s.word_count,
                }
                for s in self.sections
            ],
        }


def count_words(text: str | None) -> int:
    if not text:
        return 0
    # drop math and commands so counts approximate rendered prose
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\begin\{(equation|align|gather)\*?\}.*?\\end\{\1\*?\}",
                  " ", text, flags=re.DOTALL)
    text = re.sub(r"\\[a-zA-Z]+(\[[^\]]*\])?(\{[^}]*\})?", " ", text)
    return len(re.findall(r"[A-Za-z][\w'-]*", text))


def strip_tex_comments(src: str) -> str:
    """Remove % comments while keeping line numbers stable."""
    return _TEX_COMMENT.sub("", src)


def _sections_from_matches(
    text: str, matches: list[tuple[int, str, int]]
) -> list[Section]:
    """matches: list of (char_offset, title, level)."""
    line_starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            line_starts.append(i + 1)

    def line_of(offset: int) -> int:
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= offset:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1  # 1-based

    total_lines = text.count("\n") + 1
    sections: list[Section] = []
    for i, (off, title, level) in enumerate(matches):
        start = line_of(off)
        end = line_of(matches[i + 1][0]) - 1 if i + 1 < len(matches) else total_lines
        body = "\n".join(text.splitlines()[start - 1 : end])
        sections.append(Section(title=title, level=level,
                                start_line=start, end_line=end, text=body))
    return sections


def load(path: str | Path) -> Manuscript:
    p = Path(path).expanduser().resolve()
    raw = p.read_text(encoding="utf-8", errors="replace")
    suffix = p.suffix.lower()

    if suffix in {".tex", ".ltx", ".latex"}:
        text = strip_tex_comments(raw)
        abstract = None
        m = _TEX_ABSTRACT.search(text)
        if m:
            abstract = m.group("body").strip()
        matches = [
            (m.start(), m.group("title").strip(),
             m.group("level").count("sub") + 1)
            for m in _TEX_SECTION.finditer(text)
        ]
        ms = Manuscript(path=p, fmt="latex", raw=raw, text=text,
                        lines=text.splitlines(), abstract=abstract,
                        sections=_sections_from_matches(text, matches))
        return ms

    # default: markdown / plain text
    text = raw
    matches = [
        (m.start(), m.group("title").strip(), len(m.group("hashes")))
        for m in _MD_HEADING.finditer(text)
    ]
    sections = _sections_from_matches(text, matches)
    abstract = None
    for s in sections:
        if "abstract" in s.title.lower():
            abstract = "\n".join(s.text.splitlines()[1:]).strip()
            break
    return Manuscript(path=p, fmt="markdown", raw=raw, text=text,
                      lines=text.splitlines(), abstract=abstract,
                      sections=sections)
