"""
FastAPI route definitions — all REST API endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_classification_service,
    get_llm_provider,
    get_review_service,
    get_suggestion_service,
)
from app.agents.factory import AgentFactory
from app.api.dependencies import get_agent_factory
from app.core.config import get_settings
from app.models.requests import ClassifyRequest, ReviewRequest, SuggestRequest
from app.models.responses import (
    ClassifyResponse,
    HealthResponse,
    MetricsResponse,
    ReviewResponse,
    SuggestResponse,
)
from app.monitoring.metrics import get_metrics_listener
from app.services.classification_service import ClassificationService
from app.services.review_service import ReviewService
from app.services.suggestion_service import SuggestionService

router = APIRouter()


# ── Health & Metrics ─────────────────────────────────────────────


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
    description="Returns the health status of the API, LLM provider, and loaded agents.",
)
async def health_check() -> HealthResponse:
    """Check system health including LLM provider status."""
    settings = get_settings()
    llm = get_llm_provider()
    metrics = get_metrics_listener()

    llm_healthy = await llm.health_check()

    return HealthResponse(
        status="healthy" if llm_healthy else "degraded",
        version=settings.app_version,
        uptime_seconds=metrics.get_uptime_seconds(),
        llm_provider=llm.provider_name,
        llm_status="connected" if llm_healthy else "disconnected",
        agents_loaded=AgentFactory.available_agents(),
    )


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    tags=["System"],
    summary="Application metrics",
    description="Returns request throughput, latency percentiles, error rates, and agent timings.",
)
async def get_metrics() -> MetricsResponse:
    """Return aggregated application metrics."""
    metrics = get_metrics_listener()
    data = metrics.to_dict()
    return MetricsResponse(**data)


# ── Agent Endpoints ──────────────────────────────────────────────


@router.post(
    "/review",
    response_model=ReviewResponse,
    tags=["Agents"],
    summary="Code review",
    description="Analyze code for bugs, anti-patterns, security issues, and style violations.",
)
async def review_code(
    request: ReviewRequest,
    service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    """Submit code for AI-powered review."""
    return await service.review_code(request)


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    tags=["Agents"],
    summary="Issue classification",
    description="Classify a developer issue/ticket into categories with priority estimation.",
)
async def classify_issue(
    request: ClassifyRequest,
    service: ClassificationService = Depends(get_classification_service),
) -> ClassifyResponse:
    """Submit an issue for AI-powered classification."""
    return await service.classify_issue(request)


@router.post(
    "/suggest",
    response_model=SuggestResponse,
    tags=["Agents"],
    summary="Code suggestions",
    description="Generate optimized/refactored code with improvement explanations.",
)
async def suggest_improvements(
    request: SuggestRequest,
    service: SuggestionService = Depends(get_suggestion_service),
) -> SuggestResponse:
    """Submit code for AI-powered improvement suggestions."""
    return await service.generate_suggestion(request)
