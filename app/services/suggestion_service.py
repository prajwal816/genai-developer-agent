"""
Suggestion Service — business logic for code suggestion generation.
"""

from __future__ import annotations

from app.agents.factory import AgentFactory
from app.core.logging import get_logger
from app.models.requests import SuggestRequest
from app.models.responses import SuggestResponse
from app.monitoring.event_bus import EventBus
from app.monitoring.events import AgentEvent, EventType

logger = get_logger(__name__)


class SuggestionService:
    """
    Service layer for code suggestion generation.

    Orchestrates the SuggestionAgent, emits monitoring events,
    and transforms agent results into API response models.
    """

    def __init__(self, agent_factory: AgentFactory) -> None:
        self._agent_factory = agent_factory
        self._event_bus = EventBus.get_instance()

    async def generate_suggestion(self, request: SuggestRequest) -> SuggestResponse:
        """
        Generate code improvement suggestions.

        Args:
            request: Validated suggestion request.

        Returns:
            Structured suggestion with original/improved code and explanations.
        """
        agent = self._agent_factory.get_suggestion_agent()

        await self._event_bus.publish(
            AgentEvent(
                event_type=EventType.AGENT_EXECUTION_STARTED,
                agent_name=agent.agent_name,
            )
        )

        result = await agent.execute({
            "code": request.code,
            "language": request.language,
            "instruction": request.instruction,
            "focus_areas": request.focus_areas,
        })

        await self._event_bus.publish(
            AgentEvent(
                event_type=EventType.AGENT_EXECUTION_COMPLETED,
                agent_name=agent.agent_name,
                execution_time_ms=result.execution_time_ms,
                success=result.success,
            )
        )

        data = result.result
        return SuggestResponse(
            original_code=data.get("original_code", request.code[:2000]),
            suggested_code=data.get("suggested_code", ""),
            explanation=data.get("explanation", "Suggestion generated."),
            improvements=data.get("improvements", []),
            language=request.language,
            execution_time_ms=result.execution_time_ms,
        )
