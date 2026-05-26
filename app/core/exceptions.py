"""
Custom exception hierarchy for the GenAI Agent platform.

All application exceptions inherit from ``AgentPlatformError`` to enable
uniform error handling at the middleware layer.
"""

from __future__ import annotations


class AgentPlatformError(Exception):
    """Base exception for all platform errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        *,
        status_code: int = 500,
        error_code: str = "PLATFORM_ERROR",
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class LLMProviderError(AgentPlatformError):
    """Raised when the LLM provider fails to generate a response."""

    def __init__(
        self,
        message: str = "LLM provider encountered an error",
        *,
        provider: str = "unknown",
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code=502,
            error_code="LLM_PROVIDER_ERROR",
            details={"provider": provider, **(details or {})},
        )
        self.provider = provider


class AgentExecutionError(AgentPlatformError):
    """Raised when an AI agent fails during execution."""

    def __init__(
        self,
        message: str = "Agent execution failed",
        *,
        agent_name: str = "unknown",
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code=500,
            error_code="AGENT_EXECUTION_ERROR",
            details={"agent": agent_name, **(details or {})},
        )
        self.agent_name = agent_name


class AgentNotFoundError(AgentPlatformError):
    """Raised when a requested agent type is not registered."""

    def __init__(self, agent_type: str) -> None:
        super().__init__(
            f"Agent type '{agent_type}' is not registered",
            status_code=404,
            error_code="AGENT_NOT_FOUND",
            details={"agent_type": agent_type},
        )


class ValidationError(AgentPlatformError):
    """Raised for input validation failures."""

    def __init__(
        self, message: str = "Validation error", *, details: dict | None = None
    ) -> None:
        super().__init__(
            message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class TimeoutError(AgentPlatformError):
    """Raised when an operation exceeds its timeout."""

    def __init__(
        self,
        message: str = "Operation timed out",
        *,
        timeout_seconds: float = 0,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code=504,
            error_code="TIMEOUT_ERROR",
            details={"timeout_seconds": timeout_seconds, **(details or {})},
        )


class RateLimitError(AgentPlatformError):
    """Raised when rate limits are exceeded."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(
            message, status_code=429, error_code="RATE_LIMIT_ERROR"
        )
