"""
API request schemas validated with Pydantic v2.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    """Request payload for the code review endpoint."""

    code: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Source code to review",
        examples=['def add(a, b):\n    return a + b'],
    )
    language: str = Field(
        default="python",
        description="Programming language of the code",
        examples=["python", "javascript", "java", "go"],
    )
    context: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional context about the code (e.g. purpose, module)",
    )
    strict_mode: bool = Field(
        default=False,
        description="Enable strict analysis with more detailed checks",
    )


class ClassifyRequest(BaseModel):
    """Request payload for the issue classification endpoint."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Issue or ticket title",
        examples=["Login page crashes on mobile devices"],
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Detailed issue description",
        examples=["When accessing the login page on iOS Safari, the page crashes..."],
    )
    labels: list[str] = Field(
        default_factory=list,
        description="Existing labels/tags on the issue",
    )


class SuggestRequest(BaseModel):
    """Request payload for the code suggestion endpoint."""

    code: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Source code to improve",
        examples=['for i in range(len(lst)):\n    print(lst[i])'],
    )
    language: str = Field(
        default="python",
        description="Programming language of the code",
    )
    instruction: str | None = Field(
        default=None,
        max_length=2000,
        description="Specific improvement instruction (e.g. 'optimize for performance')",
    )
    focus_areas: list[str] = Field(
        default_factory=list,
        description="Areas to focus on: readability, performance, security, etc.",
    )
