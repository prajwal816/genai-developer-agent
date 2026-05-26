"""
Prompt template engine with variable interpolation and validation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class PromptTemplate:
    """
    Reusable prompt template with variable interpolation.

    Variables are denoted by ``{variable_name}`` in the template string.
    All declared variables must be provided at render time.
    """

    name: str
    system_prompt: str
    user_prompt_template: str
    required_variables: list[str] = field(default_factory=list)
    description: str = ""

    def __post_init__(self) -> None:
        if not self.required_variables:
            # Auto-detect variables from template
            self.required_variables = re.findall(
                r"\{(\w+)\}", self.user_prompt_template
            )

    def render(self, **variables: str) -> tuple[str, str]:
        """
        Render the template with the given variables.

        Args:
            **variables: Key-value pairs matching template variables.

        Returns:
            Tuple of (system_prompt, rendered_user_prompt).

        Raises:
            ValueError: If required variables are missing.
        """
        missing = set(self.required_variables) - set(variables.keys())
        if missing:
            raise ValueError(
                f"Missing required variables for template '{self.name}': {missing}"
            )

        rendered = self.user_prompt_template.format(**variables)
        return self.system_prompt, rendered

    def render_system(self) -> str:
        """Return the system prompt as-is."""
        return self.system_prompt
