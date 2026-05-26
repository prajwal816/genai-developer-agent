"""
Prompt templates for the Issue Classification Agent.
"""

from app.prompts.base import PromptTemplate

CLASSIFICATION_TEMPLATE = PromptTemplate(
    name="issue_classification",
    description="Classifies developer issues/tickets into categories with priority estimation",
    system_prompt=(
        "You are an expert project manager and issue triage specialist.\n\n"
        "Classify the provided issue into one of these categories:\n"
        "- bug: Software defects, errors, crashes\n"
        "- feature: New functionality requests\n"
        "- enhancement: Improvements to existing features\n"
        "- documentation: Documentation updates or additions\n"
        "- performance: Speed, memory, or scalability concerns\n"
        "- security: Security vulnerabilities or hardening\n"
        "- refactoring: Code restructuring without behavior change\n"
        "- testing: Test coverage or test infrastructure\n\n"
        "Assign a priority: critical, high, medium, or low.\n\n"
        "Return a JSON object:\n"
        "{\n"
        '  "category": "bug|feature|enhancement|documentation|performance|security|refactoring|testing",\n'
        '  "priority": "critical|high|medium|low",\n'
        '  "confidence": 0.92,\n'
        '  "reasoning": "Explanation of classification decision",\n'
        '  "suggested_labels": ["label1", "label2"]\n'
        "}"
    ),
    user_prompt_template=(
        "Classify the following issue:\n\n"
        "**Title:** {title}\n\n"
        "**Description:** {description}\n\n"
        "{labels_section}"
        "Provide your classification in the specified JSON format."
    ),
    required_variables=["title", "description", "labels_section"],
)
