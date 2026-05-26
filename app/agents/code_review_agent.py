"""
Code Review Agent — analyzes code for bugs, anti-patterns, and improvements.
"""

from __future__ import annotations

import json

from app.agents.base import BaseAgent
from app.core.exceptions import AgentExecutionError
from app.core.logging import get_logger
from app.prompts.review_prompts import CODE_REVIEW_STRICT_TEMPLATE, CODE_REVIEW_TEMPLATE
from app.services.llm.base import LLMProvider

logger = get_logger(__name__)


class CodeReviewAgent(BaseAgent):
    """
    Analyzes source code and produces structured review feedback.

    Capabilities:
    - Detect anti-patterns and code smells
    - Identify security vulnerabilities
    - Suggest improvements with actionable guidance
    - Score code quality on a 0-10 scale
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        super().__init__(llm_provider)

    @property
    def agent_name(self) -> str:
        return "code_review_agent"

    @property
    def agent_description(self) -> str:
        return "Analyzes code for bugs, anti-patterns, security issues, and suggests improvements"

    def _validate_input(self, input_data: dict) -> None:
        super()._validate_input(input_data)
        if "code" not in input_data:
            raise AgentExecutionError(
                "Missing 'code' field in input data",
                agent_name=self.agent_name,
            )

    async def _process(self, input_data: dict) -> dict:
        """Execute the code review analysis."""
        code = input_data["code"]
        language = input_data.get("language", "python")
        context = input_data.get("context")
        strict_mode = input_data.get("strict_mode", False)

        # Select prompt template
        template = CODE_REVIEW_STRICT_TEMPLATE if strict_mode else CODE_REVIEW_TEMPLATE

        # Build context section
        context_section = ""
        if context:
            context_section = f"**Context:** {context}\n\n"

        # Render prompt
        system_prompt, user_prompt = template.render(
            language=language,
            code=code,
            context_section=context_section,
        )

        # Call LLM
        response = await self._call_llm(system_prompt, user_prompt)

        # Parse response
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning(
                "Failed to parse LLM response as JSON, wrapping in default structure",
                agent=self.agent_name,
            )
            result = {
                "issues": [],
                "summary": response.content[:500],
                "score": 5.0,
                "suggestions": [],
            }

        # Enrich with metadata
        result["language"] = language
        result["lines_analyzed"] = code.count("\n") + 1
        result["llm_model"] = response.model
        result["llm_latency_ms"] = response.latency_ms

        return result
