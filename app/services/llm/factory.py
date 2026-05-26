"""
LLM Provider Factory — creates provider instances based on configuration.

Design Pattern: **Factory Pattern** applied to LLM provider creation.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.core.exceptions import LLMProviderError
from app.core.logging import get_logger
from app.services.llm.base import LLMProvider
from app.services.llm.local_provider import LocalSimulationProvider
from app.services.llm.openai_provider import OpenAIProvider

logger = get_logger(__name__)

# Registry of available providers
_PROVIDER_REGISTRY: dict[str, type[LLMProvider]] = {
    "openai": OpenAIProvider,
    "local": LocalSimulationProvider,
}


class LLMProviderFactory:
    """
    Factory for creating LLM provider instances.

    Supports dynamic registration of new providers without modifying
    existing code (Open/Closed Principle).
    """

    @staticmethod
    def create(provider_name: str | None = None) -> LLMProvider:
        """
        Create an LLM provider instance.

        Args:
            provider_name: Provider key. If None, uses config default.

        Returns:
            Configured LLMProvider instance.

        Raises:
            LLMProviderError: If the provider type is unknown.
        """
        if provider_name is None:
            provider_name = get_settings().llm.provider

        provider_cls = _PROVIDER_REGISTRY.get(provider_name)
        if provider_cls is None:
            available = ", ".join(_PROVIDER_REGISTRY.keys())
            raise LLMProviderError(
                f"Unknown LLM provider: '{provider_name}'. Available: {available}",
                provider=provider_name,
            )

        logger.info("Creating LLM provider", provider=provider_name)
        return provider_cls()

    @staticmethod
    def register(name: str, provider_cls: type[LLMProvider]) -> None:
        """Register a new provider type dynamically."""
        _PROVIDER_REGISTRY[name] = provider_cls
        logger.info("Registered LLM provider", provider=name)

    @staticmethod
    def available_providers() -> list[str]:
        """Return list of registered provider names."""
        return list(_PROVIDER_REGISTRY.keys())
