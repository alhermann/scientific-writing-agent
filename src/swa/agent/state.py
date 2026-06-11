"""State and output schemas of the LangGraph review pipeline."""

from __future__ import annotations

from typing import TypedDict

from pydantic import BaseModel, Field


class LLMFinding(BaseModel):
    """One semantic finding produced by the LLM review of a rule category."""

    rule_id: str = Field(description="Guideline rule ID, e.g. 'SL-2'")
    severity: str = Field(description="critical | major | minor")
    location: str = Field(
        description="Where in the manuscript, e.g. 'Section 3, line ~142' "
                    "or 'abstract'. Never invent precise line numbers."
    )
    excerpt: str = Field(description="Verbatim quote of the offending passage "
                                     "(may be shortened with …)")
    message: str = Field(description="What violates the rule and why it matters")
    suggestion: str = Field(default="", description="Concrete rewrite or fix")


class CategoryReview(BaseModel):
    """Structured result of reviewing one rule category."""

    category: str = Field(description="Category prefix, e.g. 'SL'")
    findings: list[LLMFinding] = Field(default_factory=list)
    not_checked: list[str] = Field(
        default_factory=list,
        description="Rule IDs that could not be checked from the given "
                    "material, with a brief reason each",
    )


class RuleProposal(BaseModel):
    """One distilled rule proposal (learning loop)."""

    slug: str = Field(description="Short kebab-case name for the proposal file")
    matched_existing: str = Field(
        default="",
        description="Existing rule ID this feedback is an instance of, if any",
    )
    rule_markdown: str = Field(
        description="Complete rule draft in the guidelines/00-meta.md format, "
                    "including the Provenance line"
    )


class Distillation(BaseModel):
    proposals: list[RuleProposal] = Field(default_factory=list)
    matched: list[str] = Field(
        default_factory=list,
        description="Feedback items that map to existing rules: 'rule-id: item'",
    )
    dropped: list[str] = Field(
        default_factory=list,
        description="Manuscript-specific items not worth generalizing",
    )


class ReviewState(TypedDict, total=False):
    """Shared state of the review graph."""

    manuscript_path: str
    structure: dict  # from Manuscript.structure_summary()
    deterministic_report: str  # markdown from the lint node
    pending_categories: list[str]  # categories still to review
    category_reviews: list[dict]  # CategoryReview dumps, appended as we go
    report: str  # final markdown report


class DistillState(TypedDict, total=False):
    """Shared state of the distillation graph."""

    feedback_text: str
    manuscript_path: str  # optional context
    distillation: dict  # Distillation dump
    saved_paths: list[str]
    summary: str
