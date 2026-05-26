"""
API response schemas with structured output models.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.models.common import CodeIssue


class ReviewResponse(BaseModel):
    """Response from the code review agent."""

    issues: list[CodeIssue] = Field(default_factory=list)
    summary: str
    score: float = Field(ge=0.0, le=10.0, description="Code quality score 0-10")
    suggestions: list[str] = Field(default_factory=list)
    language: str
    lines_analyzed: int = 0
    execution_time_ms: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ClassifyResponse(BaseModel):
    """Response from the issue classification agent."""

    category: str
    priority: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    suggested_labels: list[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SuggestResponse(BaseModel):
    """Response from the suggestion generator agent."""

    original_code: str
    suggested_code: str
    explanation: str
    improvements: list[str] = Field(default_factory=list)
    language: str
    execution_time_ms: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str
    uptime_seconds: float
    llm_provider: str
    llm_status: str
    agents_loaded: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MetricsResponse(BaseModel):
    """Application metrics response."""

    total_requests: int = 0
    requests_per_endpoint: dict[str, int] = Field(default_factory=dict)
    average_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_count: int = 0
    error_rate: float = 0.0
    agent_execution_times: dict[str, float] = Field(default_factory=dict)
    uptime_seconds: float = 0.0
    active_requests: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class APIErrorResponse(BaseModel):
    """Standard error response format."""

    error_code: str
    message: str
    details: dict = Field(default_factory=dict)
    request_id: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
