"""
Event definitions for the Observer Pattern monitoring system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class EventType(StrEnum):
    """Types of observable events in the system."""

    REQUEST_STARTED = "request_started"
    REQUEST_COMPLETED = "request_completed"
    REQUEST_FAILED = "request_failed"
    AGENT_EXECUTION_STARTED = "agent_execution_started"
    AGENT_EXECUTION_COMPLETED = "agent_execution_completed"
    AGENT_EXECUTION_FAILED = "agent_execution_failed"
    LLM_CALL_STARTED = "llm_call_started"
    LLM_CALL_COMPLETED = "llm_call_completed"
    LLM_CALL_FAILED = "llm_call_failed"
    HEALTH_CHECK = "health_check"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class Event:
    """Base event for the observer system."""

    event_type: EventType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)


@dataclass
class RequestEvent(Event):
    """Event emitted for API request lifecycle."""

    request_id: str = ""
    endpoint: str = ""
    method: str = ""
    status_code: int = 0
    latency_ms: float = 0.0


@dataclass
class AgentEvent(Event):
    """Event emitted for agent execution lifecycle."""

    agent_name: str = ""
    execution_time_ms: float = 0.0
    success: bool = True
    error_message: str = ""


@dataclass
class ErrorEvent(Event):
    """Event emitted when errors occur."""

    error_code: str = ""
    error_message: str = ""
    endpoint: str = ""
    stack_trace: str = ""
