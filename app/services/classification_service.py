"""
Classification Service — business logic for issue classification.
"""

from __future__ import annotations

from app.agents.factory import AgentFactory
from app.core.logging import get_logger
from app.models.requests import ClassifyRequest
from app.models.responses import ClassifyResponse
from app.monitoring.event_bus import EventBus
from app.monitoring.events import AgentEvent, EventType

logger = get_logger(__name__)


class ClassificationService:
    """
    Service layer for issue classification.

    Orchestrates the IssueClassificationAgent, emits monitoring events,
    and transforms agent results into API response models.
    """

    def __init__(self, agent_factory: AgentFactory) -> None:
        self._agent_factory = agent_factory
        self._event_bus = EventBus.get_instance()

    async def classify_issue(self, request: ClassifyRequest) -> ClassifyResponse:
        """
        Classify a developer issue/ticket.

        Args:
            request: Validated classification request.

        Returns:
            Structured classification with category, priority, and confidence.
        """
        agent = self._agent_factory.get_classification_agent()

        await self._event_bus.publish(
            AgentEvent(
                event_type=EventType.AGENT_EXECUTION_STARTED,
                agent_name=agent.agent_name,
            )
        )

        result = await agent.execute({
            "title": request.title,
            "description": request.description,
            "labels": request.labels,
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
        return ClassifyResponse(
            category=data.get("category", "enhancement"),
            priority=data.get("priority", "medium"),
            confidence=data.get("confidence", 0.5),
            reasoning=data.get("reasoning", "Classification completed."),
            suggested_labels=data.get("suggested_labels", []),
            execution_time_ms=result.execution_time_ms,
        )
