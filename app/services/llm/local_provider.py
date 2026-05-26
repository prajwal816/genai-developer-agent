"""
Local simulation LLM provider — concrete Strategy implementation.

Returns realistic mock responses without requiring any external API.
This is the default provider, enabling the project to run out-of-the-box.
"""

from __future__ import annotations

import asyncio
import json
import random
import time

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.llm.base import LLMProvider, LLMRequest, LLMResponse

logger = get_logger(__name__)


class LocalSimulationProvider(LLMProvider):
    """
    Local simulation provider (Strategy Pattern — concrete strategy).

    Generates deterministic, realistic responses for each agent type
    by parsing the prompt context and producing structured JSON output.
    Simulates latency to mimic real LLM behavior.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._config = settings.llm.local
        self._request_count = 0

    @property
    def provider_name(self) -> str:
        return "local"

    @property
    def model_name(self) -> str:
        return self._config.model_name

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a simulated response based on the prompt content."""
        start_time = time.perf_counter()
        self._request_count += 1

        # Simulate LLM processing latency
        latency_s = self._config.simulated_latency_ms / 1000.0
        jitter = random.uniform(0.8, 1.2)
        await asyncio.sleep(latency_s * jitter)

        # Route to the appropriate simulation handler
        content = self._route_simulation(request)

        latency_ms = (time.perf_counter() - start_time) * 1000
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return LLMResponse(
            content=content,
            model=self._config.model_name,
            provider=self.provider_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=latency_ms,
            metadata={"simulated": True, "request_number": self._request_count},
        )

    def _route_simulation(self, request: LLMRequest) -> str:
        """Route to the correct simulation based on system prompt keywords."""
        system = request.system_prompt.lower()
        prompt = request.prompt.lower()

        if "code review" in system or "review" in system:
            return self._simulate_code_review(request.prompt)
        elif "classif" in system or "categoriz" in system:
            return self._simulate_classification(request.prompt)
        elif "suggest" in system or "refactor" in system or "improve" in system:
            return self._simulate_suggestion(request.prompt)
        else:
            return self._simulate_generic(request.prompt)

    def _simulate_code_review(self, prompt: str) -> str:
        """Generate a realistic code review response."""
        code_lines = prompt.count("\n") + 1
        issues = []

        # Detect common patterns and generate relevant issues
        if "eval(" in prompt or "exec(" in prompt:
            issues.append({
                "severity": "critical",
                "line": None,
                "message": "Use of eval()/exec() detected — potential code injection vulnerability",
                "category": "security",
                "suggestion": "Replace with ast.literal_eval() or a safer alternative"
            })

        if "except:" in prompt or "except Exception:" in prompt:
            issues.append({
                "severity": "medium",
                "line": None,
                "message": "Bare except clause catches all exceptions including SystemExit and KeyboardInterrupt",
                "category": "error-handling",
                "suggestion": "Catch specific exception types instead of using bare except"
            })

        if "import *" in prompt:
            issues.append({
                "severity": "medium",
                "line": None,
                "message": "Wildcard import pollutes the namespace and makes code harder to understand",
                "category": "style",
                "suggestion": "Import specific names explicitly"
            })

        if "password" in prompt.lower() and ("=" in prompt):
            issues.append({
                "severity": "critical",
                "line": None,
                "message": "Potential hardcoded credential detected",
                "category": "security",
                "suggestion": "Use environment variables or a secrets manager"
            })

        if "global " in prompt:
            issues.append({
                "severity": "medium",
                "line": None,
                "message": "Global variable usage reduces code testability and maintainability",
                "category": "design",
                "suggestion": "Use dependency injection or class attributes instead"
            })

        if "time.sleep" in prompt:
            issues.append({
                "severity": "low",
                "line": None,
                "message": "Blocking sleep call in potentially async context",
                "category": "performance",
                "suggestion": "Use asyncio.sleep() in async code"
            })

        # Always add at least one general suggestion
        if not issues:
            issues.append({
                "severity": "info",
                "line": None,
                "message": "Consider adding type hints for better code documentation and IDE support",
                "category": "style",
                "suggestion": "Add type annotations to function parameters and return types"
            })
            issues.append({
                "severity": "low",
                "line": None,
                "message": "Missing docstrings on public functions",
                "category": "documentation",
                "suggestion": "Add docstrings following PEP 257 conventions"
            })

        score = max(2.0, 10.0 - len(issues) * 1.2)
        score = round(min(score, 9.8), 1)

        result = {
            "issues": issues,
            "summary": f"Analyzed {code_lines} lines of code. Found {len(issues)} issue(s) across security, style, and design categories.",
            "score": score,
            "suggestions": [
                "Add comprehensive error handling with specific exception types",
                "Include unit tests for critical business logic",
                "Consider using a linter (ruff/pylint) for automated style checks",
            ],
        }
        return json.dumps(result)

    def _simulate_classification(self, prompt: str) -> str:
        """Generate a realistic issue classification response."""
        prompt_lower = prompt.lower()

        # Determine category based on keywords
        category_map = {
            "crash": ("bug", "critical", 0.95),
            "error": ("bug", "high", 0.91),
            "broken": ("bug", "high", 0.89),
            "fail": ("bug", "high", 0.88),
            "slow": ("performance", "medium", 0.87),
            "timeout": ("performance", "high", 0.90),
            "add": ("feature", "medium", 0.85),
            "new feature": ("feature", "medium", 0.93),
            "implement": ("feature", "medium", 0.88),
            "update": ("enhancement", "low", 0.82),
            "improve": ("enhancement", "medium", 0.86),
            "refactor": ("refactoring", "medium", 0.91),
            "cleanup": ("refactoring", "low", 0.84),
            "document": ("documentation", "low", 0.90),
            "readme": ("documentation", "low", 0.92),
            "test": ("testing", "medium", 0.88),
            "vulnerability": ("security", "critical", 0.94),
            "inject": ("security", "critical", 0.93),
            "auth": ("security", "high", 0.89),
        }

        category, priority, confidence = "enhancement", "medium", 0.80
        for keyword, (cat, pri, conf) in category_map.items():
            if keyword in prompt_lower:
                category, priority, confidence = cat, pri, conf
                break

        result = {
            "category": category,
            "priority": priority,
            "confidence": round(confidence + random.uniform(-0.05, 0.05), 2),
            "reasoning": f"The issue description indicates a {category} concern. Key indicators suggest {priority} priority based on potential impact and urgency.",
            "suggested_labels": [category, priority, "needs-triage"],
        }
        return json.dumps(result)

    def _simulate_suggestion(self, prompt: str) -> str:
        """Generate a realistic code suggestion response."""
        # Extract the code from the prompt (between markers if present)
        code = prompt
        if "```" in prompt:
            parts = prompt.split("```")
            if len(parts) >= 3:
                code = parts[1].strip()
                if code.startswith(("python", "javascript", "java", "go")):
                    code = code.split("\n", 1)[-1] if "\n" in code else code

        # Generate improved version
        improved = code

        # Apply common improvements
        replacements = [
            ("for i in range(len(", "for i, item in enumerate("),
            ("== None", "is None"),
            ("!= None", "is not None"),
            ("== True", "is True"),
            ("== False", "is False"),
            ("print(", "logger.info("),
            ("except:", "except Exception as e:"),
            ("dict()", "{}"),
            ("list()", "[]"),
        ]

        improvements = []
        for old, new in replacements:
            if old in improved:
                improved = improved.replace(old, new, 1)
                improvements.append(f"Replaced '{old}' with '{new}' for better Python idioms")

        if not improvements:
            improvements = [
                "Added type hints to function signatures",
                "Improved variable naming for clarity",
                "Extracted magic numbers into named constants",
            ]
            improved = f"# Improved version with type hints and better naming\n{code}"

        result = {
            "original_code": code[:2000],
            "suggested_code": improved[:2000],
            "explanation": f"Applied {len(improvements)} improvement(s) focusing on Python best practices, readability, and maintainability.",
            "improvements": improvements,
        }
        return json.dumps(result)

    def _simulate_generic(self, prompt: str) -> str:
        """Fallback generic response."""
        return json.dumps({
            "response": "Analysis complete. The provided input has been processed successfully.",
            "confidence": 0.85,
        })

    async def health_check(self) -> bool:
        """Local provider is always healthy."""
        return True
