"""
Common domain models shared across the application.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class Severity(StrEnum):
    """Issue severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Priority(StrEnum):
    """Issue priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueCategory(StrEnum):
    """Issue classification categories."""

    BUG = "bug"
    FEATURE = "feature"
    ENHANCEMENT = "enhancement"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    REFACTORING = "refactoring"
    TESTING = "testing"


class CodeIssue(BaseModel):
    """A single issue found during code review."""

    severity: Severity
    line: int | None = None
    message: str
    category: str
    suggestion: str = ""


class AgentResult(BaseModel):
    """Wrapper for agent execution results with metadata."""

    agent_name: str
    execution_time_ms: float
    success: bool = True
    result: dict
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ErrorDetail(BaseModel):
    """Structured error information for API responses."""

    error_code: str
    message: str
    details: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
