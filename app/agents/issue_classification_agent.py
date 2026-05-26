"""
Issue Classification Agent — categorizes issues with priority estimation.
"""

from __future__ import annotations

import json

from app.agents.base import BaseAgent
from app.core.exceptions import AgentExecutionError
from app.core.logging import get_logger
from app.prompts.classification_prompts import CLASSIFICATION_TEMPLATE
from app.services.llm.base import LLMProvider

logger = get_logger(__name__)


class IssueClassificationAgent(BaseAgent):
    """
    Classifies developer issues/tickets into categories with priority estimation.

    Capabilities:
    - Categorize issues (bug, feature, enhancement, etc.)
    - Estimate priority (critical, high, medium, low)
    - Provide confidence scores and reasoning
    - Suggest relevant labels
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        super().__init__(llm_provider)

    @property
    def agent_name(self) -> str:
        return "issue_classification_agent"

    @property
    def agent_description(self) -> str:
        return "Classifies developer issues into categories with priority estimation"

    def _validate_input(self, input_data: dict) -> None:
        super()._validate_input(input_data)
        if "title" not in input_data or "description" not in input_data:
            raise AgentExecutionError(
                "Missing 'title' or 'description' field in input data",
                agent_name=self.agent_name,
            )

    async def _process(self, input_data: dict) -> dict:
        """Execute the issue classification."""
        title = input_data["title"]
        description = input_data["description"]
        labels = input_data.get("labels", [])

        # Build labels section
        labels_section = ""
        if labels:
            labels_section = f"**Existing Labels:** {', '.join(labels)}\n\n"

        # Render prompt
        system_prompt, user_prompt = CLASSIFICATION_TEMPLATE.render(
            title=title,
            description=description,
            labels_section=labels_section,
        )

        # Call LLM
        response = await self._call_llm(system_prompt, user_prompt)

        # Parse response
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning(
                "Failed to parse LLM response as JSON",
                agent=self.agent_name,
            )
            result = {
                "category": "enhancement",
                "priority": "medium",
                "confidence": 0.5,
                "reasoning": response.content[:500],
                "suggested_labels": [],
            }

        # Enrich with metadata
        result["llm_model"] = response.model
        result["llm_latency_ms"] = response.latency_ms

        return result
