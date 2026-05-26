"""
Unit tests for LLM providers.
"""

from __future__ import annotations

import pytest

from app.core.exceptions import LLMProviderError
from app.services.llm.base import LLMProvider, LLMRequest, LLMResponse
from app.services.llm.factory import LLMProviderFactory
from app.services.llm.local_provider import LocalSimulationProvider


@pytest.mark.asyncio
class TestLocalSimulationProvider:
    """Tests for the LocalSimulationProvider."""

    async def test_generate_returns_response(self):
        provider = LocalSimulationProvider()
        request = LLMRequest(
            prompt="Review this code: def foo(): pass",
            system_prompt="You are a code reviewer.",
        )
        response = await provider.generate(request)
        assert isinstance(response, LLMResponse)
        assert response.content
        assert response.provider == "local"
        assert response.latency_ms > 0

    async def test_code_review_simulation(self):
        provider = LocalSimulationProvider()
        request = LLMRequest(
            prompt="eval(user_input)",
            system_prompt="You are a code review expert.",
        )
        response = await provider.generate(request)
        assert "issues" in response.content or "eval" in response.content.lower()

    async def test_classification_simulation(self):
        provider = LocalSimulationProvider()
        request = LLMRequest(
            prompt="The application crashes on startup",
            system_prompt="You are an issue classification expert.",
        )
        response = await provider.generate(request)
        assert "category" in response.content

    async def test_suggestion_simulation(self):
        provider = LocalSimulationProvider()
        request = LLMRequest(
            prompt="for i in range(len(lst)): print(lst[i])",
            system_prompt="You are a code suggestion expert. Improve this code.",
        )
        response = await provider.generate(request)
        assert response.content

    async def test_health_check(self):
        provider = LocalSimulationProvider()
        assert await provider.health_check() is True

    async def test_provider_name(self):
        provider = LocalSimulationProvider()
        assert provider.provider_name == "local"

    async def test_model_name(self):
        provider = LocalSimulationProvider()
        assert "local" in provider.model_name.lower() or "simulation" in provider.model_name.lower()

    async def test_token_counts(self):
        provider = LocalSimulationProvider()
        request = LLMRequest(prompt="test prompt", system_prompt="system")
        response = await provider.generate(request)
        assert response.prompt_tokens > 0
        assert response.completion_tokens > 0
        assert response.total_tokens == response.prompt_tokens + response.completion_tokens


class TestLLMProviderFactory:
    """Tests for the LLMProviderFactory."""

    def test_create_local_provider(self):
        provider = LLMProviderFactory.create("local")
        assert isinstance(provider, LocalSimulationProvider)

    def test_create_default_provider(self):
        provider = LLMProviderFactory.create()
        assert isinstance(provider, LLMProvider)

    def test_unknown_provider_raises_error(self):
        with pytest.raises(LLMProviderError):
            LLMProviderFactory.create("nonexistent")

    def test_available_providers(self):
        providers = LLMProviderFactory.available_providers()
        assert "local" in providers
        assert "openai" in providers

    def test_register_custom_provider(self):
        class CustomProvider(LocalSimulationProvider):
            @property
            def provider_name(self) -> str:
                return "custom"

        LLMProviderFactory.register("custom", CustomProvider)
        assert "custom" in LLMProviderFactory.available_providers()
        provider = LLMProviderFactory.create("custom")
        assert provider.provider_name == "custom"
