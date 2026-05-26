"""
Agent Factory — creates agent instances using the Factory Pattern.

Supports dynamic registration of new agent types without modifying
existing code (Open/Closed Principle).
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.agents.code_review_agent import CodeReviewAgent
from app.agents.issue_classification_agent import IssueClassificationAgent
from app.agents.suggestion_agent import SuggestionAgent
from app.core.exceptions import AgentNotFoundError
from app.core.logging import get_logger
from app.services.llm.base import LLMProvider

logger = get_logger(__name__)

# Type alias for agent class registry
AgentClass = type[BaseAgent]

# Default agent registry
_AGENT_REGISTRY: dict[str, AgentClass] = {
    "code_review": CodeReviewAgent,
    "issue_classification": IssueClassificationAgent,
    "suggestion": SuggestionAgent,
}


class AgentFactory:
    """
    Factory for creating AI agent instances.

    Design Pattern: **Factory Pattern**
    - Decouples agent creation from the service layer.
    - New agent types can be registered dynamically at runtime.
    - Each agent receives a shared LLM provider via dependency injection.
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm_provider = llm_provider
        self._instances: dict[str, BaseAgent] = {}

    def create(self, agent_type: str) -> BaseAgent:
        """
        Create or return a cached agent instance.

        Args:
            agent_type: Registered agent type key.

        Returns:
            Configured BaseAgent instance.

        Raises:
            AgentNotFoundError: If agent_type is not registered.
        """
        # Return cached instance if available
        if agent_type in self._instances:
            return self._instances[agent_type]

        agent_cls = _AGENT_REGISTRY.get(agent_type)
        if agent_cls is None:
            raise AgentNotFoundError(agent_type)

        agent = agent_cls(self._llm_provider)
        self._instances[agent_type] = agent

        logger.info(
            "Created agent instance",
            agent_type=agent_type,
            agent_name=agent.agent_name,
        )
        return agent

    def get_review_agent(self) -> CodeReviewAgent:
        """Convenience method for the code review agent."""
        return self.create("code_review")  # type: ignore[return-value]

    def get_classification_agent(self) -> IssueClassificationAgent:
        """Convenience method for the classification agent."""
        return self.create("issue_classification")  # type: ignore[return-value]

    def get_suggestion_agent(self) -> SuggestionAgent:
        """Convenience method for the suggestion agent."""
        return self.create("suggestion")  # type: ignore[return-value]

    @staticmethod
    def register(name: str, agent_cls: AgentClass) -> None:
        """Register a new agent type dynamically."""
        _AGENT_REGISTRY[name] = agent_cls
        logger.info("Registered agent type", agent_type=name)

    @staticmethod
    def available_agents() -> list[str]:
        """Return list of registered agent type names."""
        return list(_AGENT_REGISTRY.keys())
