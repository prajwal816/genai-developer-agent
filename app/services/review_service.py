"""
Code Review Service — business logic layer for code review operations.
"""

from __future__ import annotations

from app.agents.factory import AgentFactory
from app.core.logging import get_logger
from app.models.common import CodeIssue
from app.models.requests import ReviewRequest
from app.models.responses import ReviewResponse
from app.monitoring.event_bus import EventBus
from app.monitoring.events import AgentEvent, EventType

logger = get_logger(__name__)


class ReviewService:
    """
    Service layer for code review operations.

    Orchestrates the CodeReviewAgent, emits monitoring events,
    and transforms agent results into API response models.
    """

    def __init__(self, agent_factory: AgentFactory) -> None:
        self._agent_factory = agent_factory
        self._event_bus = EventBus.get_instance()

    async def review_code(self, request: ReviewRequest) -> ReviewResponse:
        """
        Perform a code review on the submitted code.

        Args:
            request: Validated review request.

        Returns:
            Structured review response with issues and score.
        """
        agent = self._agent_factory.get_review_agent()

        # Emit agent start event
        await self._event_bus.publish(
            AgentEvent(
                event_type=EventType.AGENT_EXECUTION_STARTED,
                agent_name=agent.agent_name,
            )
        )

        # Execute agent
        result = await agent.execute({
            "code": request.code,
            "language": request.language,
            "context": request.context,
            "strict_mode": request.strict_mode,
        })

        # Emit agent completion event
        await self._event_bus.publish(
            AgentEvent(
                event_type=EventType.AGENT_EXECUTION_COMPLETED,
                agent_name=agent.agent_name,
                execution_time_ms=result.execution_time_ms,
                success=result.success,
            )
        )

        # Transform to response model
        data = result.result
        issues = [
            CodeIssue(**issue) for issue in data.get("issues", [])
        ]

        return ReviewResponse(
            issues=issues,
            summary=data.get("summary", "Review completed."),
            score=data.get("score", 5.0),
            suggestions=data.get("suggestions", []),
            language=request.language,
            lines_analyzed=data.get("lines_analyzed", request.code.count("\n") + 1),
            execution_time_ms=result.execution_time_ms,
        )
