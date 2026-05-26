"""
Global error handler middleware — catches all exceptions and returns structured JSON.
"""

from __future__ import annotations

import traceback

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AgentPlatformError
from app.core.logging import get_logger
from app.models.responses import APIErrorResponse
from app.monitoring.event_bus import EventBus
from app.monitoring.events import ErrorEvent, EventType

logger = get_logger(__name__)


async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Handle all uncaught exceptions and return structured JSON errors.

    Platform exceptions carry their own status code and error code.
    Unknown exceptions default to 500.
    """
    request_id = getattr(request.state, "request_id", "unknown")

    if isinstance(exc, AgentPlatformError):
        status_code = exc.status_code
        error_response = APIErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            request_id=request_id,
        )
    else:
        status_code = 500
        error_response = APIErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            details={"type": type(exc).__name__},
            request_id=request_id,
        )

    # Emit error event
    event_bus = EventBus.get_instance()
    await event_bus.publish(
        ErrorEvent(
            event_type=EventType.ERROR_OCCURRED,
            error_code=error_response.error_code,
            error_message=str(exc),
            endpoint=str(request.url.path),
            stack_trace=traceback.format_exc()[:1000],
        )
    )

    logger.error(
        "Exception handled",
        error_code=error_response.error_code,
        status_code=status_code,
        error=str(exc),
        endpoint=str(request.url.path),
    )

    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(mode="json"),
    )
