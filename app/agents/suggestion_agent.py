"""
Suggestion Generator Agent — produces optimized/refactored code.
"""

from __future__ import annotations

import json

from app.agents.base import BaseAgent
from app.core.exceptions import AgentExecutionError
from app.core.logging import get_logger
from app.prompts.suggestion_prompts import SUGGESTION_TEMPLATE
from app.services.llm.base import LLMProvider

logger = get_logger(__name__)


class SuggestionAgent(BaseAgent):
    """
    Generates optimized and refactored code suggestions.

    Capabilities:
    - Refactor code for readability and maintainability
    - Optimize for performance
    - Apply language-specific best practices
    - Explain each improvement with reasoning
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        super().__init__(llm_provider)

    @property
    def agent_name(self) -> str:
        return "suggestion_agent"

    @property
    def agent_description(self) -> str:
        return "Generates optimized and refactored code with explanations"

    def _validate_input(self, input_data: dict) -> None:
        super()._validate_input(input_data)
        if "code" not in input_data:
            raise AgentExecutionError(
                "Missing 'code' field in input data",
                agent_name=self.agent_name,
            )

    async def _process(self, input_data: dict) -> dict:
        """Execute the code suggestion generation."""
        code = input_data["code"]
        language = input_data.get("language", "python")
        instruction = input_data.get("instruction")
        focus_areas = input_data.get("focus_areas", [])

        # Build optional sections
        instruction_section = ""
        if instruction:
            instruction_section = f"**Specific Instruction:** {instruction}\n\n"

        focus_section = ""
        if focus_areas:
            focus_section = f"**Focus Areas:** {', '.join(focus_areas)}\n\n"

        # Render prompt
        system_prompt, user_prompt = SUGGESTION_TEMPLATE.render(
            language=language,
            code=code,
            instruction_section=instruction_section,
            focus_section=focus_section,
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
                "original_code": code[:2000],
                "suggested_code": response.content[:2000],
                "explanation": "See the suggested code above for improvements.",
                "improvements": [],
            }

        # Ensure original_code is present
        if "original_code" not in result:
            result["original_code"] = code[:2000]

        # Enrich with metadata
        result["language"] = language
        result["llm_model"] = response.model
        result["llm_latency_ms"] = response.latency_ms

        return result
