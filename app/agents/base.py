"""
Abstract base agent — defines the interface for all AI agents.

All concrete agents inherit from BaseAgent and implement the
execute() method for their specific domain.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod

from app.core.exceptions import AgentExecutionError
from app.core.logging import get_logger
from app.models.common import AgentResult
from app.services.llm.base import LLMProvider, LLMRequest, LLMResponse

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base agent for all AI agents.

    Provides:
    - LLM provider integration
    - Execution timing
    - Structured error handling
    - Result formatting

    Subclasses implement ``_process()`` with domain-specific logic.
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider
        self._execution_count = 0

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Unique name identifying this agent."""
        ...

    @property
    @abstractmethod
    def agent_description(self) -> str:
        """Human-readable description of what this agent does."""
        ...

    async def execute(self, input_data: dict) -> AgentResult:
        """
        Execute the agent with the given input data.

        Handles timing, error wrapping, and result formatting.

        Args:
            input_data: Domain-specific input dictionary.

        Returns:
            AgentResult with execution metadata.

        Raises:
            AgentExecutionError: If the agent fails during execution.
        """
        start_time = time.perf_counter()
        self._execution_count += 1

        try:
            self._validate_input(input_data)
            result = await self._process(input_data)
            execution_time_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "Agent execution completed",
                agent=self.agent_name,
                execution_time_ms=round(execution_time_ms, 2),
                execution_count=self._execution_count,
            )

            return AgentResult(
                agent_name=self.agent_name,
                execution_time_ms=round(execution_time_ms, 2),
                success=True,
                result=result,
            )

        except AgentExecutionError:
            raise
        except Exception as exc:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "Agent execution failed",
                agent=self.agent_name,
                error=str(exc),
                execution_time_ms=round(execution_time_ms, 2),
            )
            raise AgentExecutionError(
                f"Agent '{self.agent_name}' failed: {exc}",
                agent_name=self.agent_name,
                details={"error": str(exc)},
            ) from exc

    @abstractmethod
    async def _process(self, input_data: dict) -> dict:
        """
        Domain-specific processing logic. Implemented by subclasses.

        Args:
            input_data: Validated input data.

        Returns:
            Result dictionary with agent-specific output.
        """
        ...

    def _validate_input(self, input_data: dict) -> None:
        """
        Validate input data before processing. Override for custom validation.

        Raises:
            AgentExecutionError: If validation fails.
        """
        if not input_data:
            raise AgentExecutionError(
                "Empty input data", agent_name=self.agent_name
            )

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Helper to call the LLM provider with structured prompts."""
        request = LLMRequest(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )
        return await self._llm.generate(request)
