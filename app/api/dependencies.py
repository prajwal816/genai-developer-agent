"""
FastAPI dependency injection — provides service instances to route handlers.
"""

from __future__ import annotations

from functools import lru_cache

from app.agents.factory import AgentFactory
from app.core.config import get_settings
from app.services.llm.base import LLMProvider
from app.services.llm.factory import LLMProviderFactory
from app.services.review_service import ReviewService
from app.services.classification_service import ClassificationService
from app.services.suggestion_service import SuggestionService

# --- Singletons ---

_llm_provider: LLMProvider | None = None
_agent_factory: AgentFactory | None = None
_review_service: ReviewService | None = None
_classification_service: ClassificationService | None = None
_suggestion_service: SuggestionService | None = None


def get_llm_provider() -> LLMProvider:
    """Return the singleton LLM provider."""
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = LLMProviderFactory.create()
    return _llm_provider


def get_agent_factory() -> AgentFactory:
    """Return the singleton AgentFactory."""
    global _agent_factory
    if _agent_factory is None:
        _agent_factory = AgentFactory(get_llm_provider())
    return _agent_factory


def get_review_service() -> ReviewService:
    """Return the singleton ReviewService."""
    global _review_service
    if _review_service is None:
        _review_service = ReviewService(get_agent_factory())
    return _review_service


def get_classification_service() -> ClassificationService:
    """Return the singleton ClassificationService."""
    global _classification_service
    if _classification_service is None:
        _classification_service = ClassificationService(get_agent_factory())
    return _classification_service


def get_suggestion_service() -> SuggestionService:
    """Return the singleton SuggestionService."""
    global _suggestion_service
    if _suggestion_service is None:
        _suggestion_service = SuggestionService(get_agent_factory())
    return _suggestion_service


async def shutdown_dependencies() -> None:
    """Clean up all dependencies on shutdown."""
    global _llm_provider
    if _llm_provider is not None:
        await _llm_provider.shutdown()
        _llm_provider = None
