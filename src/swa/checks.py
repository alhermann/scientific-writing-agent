"""Deterministic (LLM-free) rule checks.

Each check implements the *deterministic half* of a rule from the guideline
catalogue and yields :class:`Finding` objects pointing at concrete lines.
Hybrid rules emit candidates that an LLM (or human) pass filters afterwards;
findings therefore carry a ``confidence`` field.

Stdlib only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Callable, Iterator

from .manuscript import Manuscript, count_words

CheckFn = Callable[[Manuscript], Iterator["Finding"]]
_REGISTRY: dict[str, list[CheckFn]] = {}


@dataclass
class Finding:
    rule_id: str
    severity: str
    line: int | None
    excerpt: str
    message: str
    suggestion: str | None = None
    confidence: str = "high"  # high = act on it; candidate = needs LLM/human filter

    def to_dict(self) -> dict:
        return asdict(self)


def register(rule_id: str, severity: str):
    def deco(fn: Callable[[Manuscript, str, str], Iterator[Finding]]):
        def wrapped(ms: Manuscript) -> Iterator[Finding]:
            return fn(ms, rule_id, severity)

        wrapped.__name__ = fn.__name__
        _REGISTRY.setdefault(rule_id, []).append(wrapped)
        return wrapped

    return deco


def run_all(ms: Manuscript, only: set[str] | None = None) -> list[Finding]:
    findings: list[Finding] = []
    for rule_id, fns in sorted(_REGISTRY.items()):
        if only and rule_id not in only:
            continue
        for fn in fns:
            findings.extend(fn(ms))
    findings.sort(key=lambda f: (f.line or 0))
    return findings


def available_checks() -> list[str]:
    return sorted(_REGISTRY)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _grep(ms: Manuscript, pattern: re.Pattern) -> Iterator[tuple[int, str, re.Match]]:
    for i, line in enumerate(ms.lines, start=1):
        for m in pattern.finditer(line):
            yield i, line.strip(), m


def _excerpt(line: str, width: int = 100) -> str:
    line = line.strip()
    return line if len(line) <= width else line[: width - 1] + "…"


# --------------------------------------------------------------------------
# LG — language & style
# --------------------------------------------------------------------------

_IN_ORDER_TO = re.compile(r"\bin order to\b", re.IGNORECASE)


@register("LG-3", "minor")
def check_in_order_to(ms, rule_id, severity):
    for ln, line, _ in _grep(ms, _IN_ORDER_TO):
        yield Finding(rule_id, severity, ln, _excerpt(line),
                      '"in order to" — almost always better as plain "to"',
                      suggestion='Replace "in order to" with "to".')


_SCAFFOLD = re.compile(
    r"\b(see\s+Fig(?:ure|\.)|It\s+can\s+(?:clearly\s+)?be\s+seen|"
    r"It\s+(?:should|is\s+to)\s+be\s+noted|it\s+is\s+worth\s+(?:mentioning|noting)|"
    r"The\s+results\s+in\s+Fig(?:ure|\.))",
    re.IGNORECASE,
)


@register("LG-7", "minor")
def check_scaffolding(ms, rule_id, severity):
    for ln, line, m in _grep(ms, _SCAFFOLD):
        yield Finding(rule_id, severity, ln, _excerpt(line),
                      f'Scaffolding phrase "{m.group(0)}" — prefer the direct formulation',
                      suggestion='E.g. "(see Figure 8)" → "(Figure 8)"; '
                                 '"It can be seen that X" → "X".')


_DOUBLED_WORD = re.compile(r"\b([A-Za-z]{2,})\s+\1\b", re.IGNORECASE)
_DOUBLED_OK = {"that", "had"}  # "that that", "had had" can be legitimate


@register("LG-6", "major")
def check_doubled_words(ms, rule_id, severity):
    for ln, line, m in _grep(ms, _DOUBLED_WORD):
        if m.group(1).lower() in _DOUBLED_OK:
            continue
        yield Finding(rule_id, severity, ln, _excerpt(line),
                      f'Duplicated word: "{m.group(0)}"',
                      suggestion=f'Probably meant a single "{m.group(1)}".')


# unhyphenated compound modifiers (candidates; LLM filters non-modifier uses)
_HYPHEN_PAIRS = [
    "one dimensional", "two dimensional", "three dimensional",
    "stress strain", "load displacement", "force displacement",
    "data driven", "physics informed", "mesh free", "lattice based",
    "rate dependent", "rate independent", "first order", "second order",
    "higher order", "finite element", "state based", "bond based",
    "well known", "long term", "short term", "real time", "large scale",
]
_HYPHEN_RE = re.compile(
    r"\b(" + "|".join(p.replace(" ", r"\s+") for p in _HYPHEN_PAIRS) + r")\s+(\w+)",
    re.IGNORECASE,
)


@register("LG-5", "minor")
def check_hyphenation(ms, rule_id, severity):
    for ln, line, m in _grep(ms, _HYPHEN_RE):
        pair = re.sub(r"\s+", " ", m.group(1))
        yield Finding(rule_id, severity, ln, _excerpt(line),
                      f'Possible missing hyphen in compound modifier: "{pair} {m.group(2)}"',
                      suggestion=f'If used as modifier: "{pair.replace(" ", "-")} {m.group(2)}".',
                      confidence="candidate")


# --------------------------------------------------------------------------
# ST — structure
# --------------------------------------------------------------------------

_NOVELTY_MARKERS = re.compile(
    r"(in this (paper|work|article|study)|we (introduce|present|propose|develop)|"
    r"the (main |key |central )?contribution|for the first time|novel)",
    re.IGNORECASE,
)


@register("ST-1", "critical")
def check_abstract_length(ms, rule_id, severity):
    if ms.abstract is None:
        yield Finding(rule_id, severity, None, "",
                      "No abstract found (or not detectable in this format).",
                      confidence="candidate")
        return
    n = count_words(ms.abstract)
    if n > 250:
        yield Finding(rule_id, severity, None, _excerpt(ms.abstract.splitlines()[0]),
                      f"Abstract has ~{n} words; the guideline asks for 10–15 lines "
                      f"(≈150–250 words).",
                      suggestion="Cut technical detail; keep problem + solution/novelty.")


@register("ST-2", "critical")
def check_novelty_paragraph(ms, rule_id, severity):
    intro = ms.introduction
    if intro is None:
        return
    paragraphs = [p for p in re.split(r"\n\s*\n", intro.text) if count_words(p) > 10]
    tail = "\n\n".join(paragraphs[-2:]) if paragraphs else ""
    if not _NOVELTY_MARKERS.search(tail):
        yield Finding(rule_id, severity, intro.end_line, "",
                      "No novelty-summary paragraph detected at the end of the "
                      'introduction (no "In this paper, we introduce/present…" marker).',
                      suggestion="Add a closing paragraph enumerating the novel "
                                 "contributions relative to the cited state of the art.",
                      confidence="candidate")


@register("ST-3", "major")
def check_intro_length(ms, rule_id, severity):
    intro = ms.introduction
    if intro is None:
        return
    n = intro.word_count
    if n > 900:  # ≈ 1 page two-column / generous single-column estimate
        yield Finding(rule_id, severity, intro.start_line, intro.title,
                      f"Introduction has ~{n} words — likely beyond one page.",
                      suggestion="Move technical material into later sections; "
                                 "keep ≤3/4 page state of the art + 1/4 page novelty.",
                      confidence="candidate")


_TITLE_CASE_WORD = re.compile(r"\b[A-Z][a-z]+\b")
_TITLE_SMALL_WORDS = {"a", "an", "the", "of", "for", "and", "or", "in", "on",
                      "with", "to", "via", "by", "from"}


@register("LG-4", "minor")
def check_heading_case(ms, rule_id, severity):
    for s in ms.sections:
        words = s.title.split()
        if len(words) < 2:
            continue
        caps = [w for w in words[1:]
                if _TITLE_CASE_WORD.fullmatch(w) and w.lower() not in _TITLE_SMALL_WORDS]
        if len(caps) >= 2:  # looks like Title Case
            yield Finding(rule_id, severity, s.start_line, s.title,
                          f'Heading appears to use Title Case: "{s.title}"',
                          suggestion="Use sentence case: capitalize only the first "
                                     "word and names.",
                          confidence="candidate")


# --------------------------------------------------------------------------
# TX — LaTeX hygiene  (operate on the *raw* source incl. comments)
# --------------------------------------------------------------------------

_TODO = re.compile(r"\b(TODO|FIXME|XXX|TBD)\b")


@register("TX-1", "major")
def check_leftovers(ms, rule_id, severity):
    if ms.fmt != "latex":
        return
    raw_lines = ms.raw.splitlines()
    # TODO markers
    for i, line in enumerate(raw_lines, start=1):
        if _TODO.search(line):
            yield Finding(rule_id, severity, i, _excerpt(line),
                          "Leftover TODO/FIXME marker in source.",
                          suggestion="Resolve or remove before circulating.")
    # blocks of >=4 consecutive comment lines that contain prose/math
    run_start, run = None, 0
    for i, line in enumerate(raw_lines + [""], start=1):
        stripped = line.lstrip()
        if stripped.startswith("%") and len(stripped) > 2:
            run += 1
            run_start = run_start or i
        else:
            if run >= 4 and run_start is not None:
                yield Finding(rule_id, severity, run_start,
                              _excerpt(raw_lines[run_start - 1]),
                              f"Commented-out block of {run} lines — likely outdated "
                              "text left in the document.",
                              suggestion="Delete it; git history preserves it.",
                              confidence="candidate")
            run_start, run = None, 0
    if "\\iffalse" in ms.raw:
        yield Finding(rule_id, severity, None, "\\iffalse",
                      "\\iffalse block found — dead text in circulated source.",
                      suggestion="Remove the disabled block.")


_HARDCODED_REF = re.compile(
    r"\b(Section|Sec\.|Figure|Fig\.|Table|Tab\.|Equation|Eq\.)\s+\(?\d+\)?",
)


@register("TX-3", "minor")
def check_hardcoded_refs(ms, rule_id, severity):
    if ms.fmt != "latex":
        return
    for ln, line, m in _grep(ms, _HARDCODED_REF):
        if "\\ref" in line or "\\cref" in line or "\\eqref" in line:
            continue
        yield Finding(rule_id, severity, ln, _excerpt(line),
                      f'Hard-coded cross-reference "{m.group(0)}" — breaks silently '
                      "on renumbering.",
                      suggestion="Use \\cref/\\ref/\\eqref with a label.",
                      confidence="candidate")


@register("TX-2", "minor")
def check_fig_figure_mix(ms, rule_id, severity):
    n_fig = len(re.findall(r"\bFig\.\s", ms.text))
    n_figure = len(re.findall(r"\bFigure\s", ms.text))
    if n_fig and n_figure:
        yield Finding(rule_id, severity, None, "",
                      f'Mixed figure references: "Fig." ×{n_fig} and "Figure" '
                      f"×{n_figure}.",
                      suggestion="Pick one convention (check the journal style) "
                                 "and apply it everywhere — ideally via cleveref.")


# --------------------------------------------------------------------------
# FG — figures
# --------------------------------------------------------------------------

@register("FG-5", "major")
def check_unreferenced_figures(ms, rule_id, severity):
    if ms.fmt != "latex":
        return
    labels = re.findall(r"\\label\{(fig:[^}]+)\}", ms.text)
    refs = set(re.findall(r"\\(?:c|C)?ref\*?\{([^}]+)\}", ms.text))
    refs |= {r for grp in re.findall(r"\\cref\{([^}]+)\}", ms.text)
             for r in grp.split(",")}
    for lab in labels:
        if lab not in refs:
            yield Finding(rule_id, severity, None, lab,
                          f"Figure label '{lab}' is never referenced in the text.",
                          suggestion="Reference the figure or remove it (SL-1/TX-1).")
