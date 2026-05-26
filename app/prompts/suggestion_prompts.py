"""
Prompt templates for the Suggestion Generator Agent.
"""

from app.prompts.base import PromptTemplate

SUGGESTION_TEMPLATE = PromptTemplate(
    name="code_suggestion",
    description="Generates optimized/refactored code with explanations",
    system_prompt=(
        "You are an expert software engineer specializing in code optimization and refactoring.\n\n"
        "Given source code, generate an improved version that is:\n"
        "- More readable and maintainable\n"
        "- Following language-specific best practices and idioms\n"
        "- Better structured with clear naming conventions\n"
        "- More performant where possible\n"
        "- Properly documented\n\n"
        "Return a JSON object:\n"
        "{\n"
        '  "original_code": "the input code",\n'
        '  "suggested_code": "the improved code",\n'
        '  "explanation": "What was changed and why",\n'
        '  "improvements": ["improvement 1", "improvement 2"]\n'
        "}\n\n"
        "Preserve the original functionality while improving code quality."
    ),
    user_prompt_template=(
        "Improve the following {language} code:\n\n"
        "```{language}\n{code}\n```\n\n"
        "{instruction_section}"
        "{focus_section}"
        "Provide the improved code in the specified JSON format."
    ),
    required_variables=["language", "code", "instruction_section", "focus_section"],
)
