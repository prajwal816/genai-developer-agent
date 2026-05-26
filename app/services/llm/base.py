"""
Abstract LLM provider interface — Strategy Pattern.

All concrete LLM providers must implement this interface, allowing
the agent system to swap providers at runtime without code changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class LLMRequest:
    """Encapsulates a request to the LLM provider."""

    prompt: str
    system_prompt: str = ""
    max_tokens: int = 4096
    temperature: float = 0.3
    stop_sequences: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Encapsulates a response from the LLM provider."""

    content: str
    model: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    metadata: dict = field(default_factory=dict)


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers (Strategy interface).

    Design Pattern: **Strategy Pattern**
    - Each concrete provider (OpenAI, Local) is a strategy.
    - Agents hold a reference to an LLMProvider and call generate().
    - The provider can be swapped at runtime via configuration.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier."""
        ...

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a completion from the LLM.

        Args:
            request: The LLM request containing prompt and parameters.

        Returns:
            LLMResponse with the generated content and metadata.

        Raises:
            LLMProviderError: If the provider fails to generate.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verify that the provider is available and operational.

        Returns:
            True if the provider is healthy, False otherwise.
        """
        ...

    async def shutdown(self) -> None:
        """Clean up provider resources. Override if needed."""
        pass
