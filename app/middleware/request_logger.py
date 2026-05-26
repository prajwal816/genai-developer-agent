"""
Request logging middleware — logs every HTTP request with correlation IDs.
"""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

import structlog

from app.core.logging import get_logger
from app.monitoring.event_bus import EventBus
from app.monitoring.events import EventType, RequestEvent

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that:
    - Assigns a unique correlation ID to every request
    - Logs request start/completion with method, path, status, and latency
    - Emits events to the EventBus for the Observer Pattern
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        # Bind correlation ID to structlog context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # Store request_id for downstream access
        request.state.request_id = request_id

        endpoint = f"{request.method} {request.url.path}"
        event_bus = EventBus.get_instance()

        # Emit request started event
        await event_bus.publish(
            RequestEvent(
                event_type=EventType.REQUEST_STARTED,
                request_id=request_id,
                endpoint=request.url.path,
                method=request.method,
            )
        )

        try:
            response = await call_next(request)
            latency_ms = (time.perf_counter() - start_time) * 1000

            # Add correlation headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Latency-Ms"] = f"{latency_ms:.2f}"

            # Emit request completed event
            await event_bus.publish(
                RequestEvent(
                    event_type=EventType.REQUEST_COMPLETED,
                    request_id=request_id,
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    latency_ms=round(latency_ms, 2),
                )
            )

            logger.info(
                "Request completed",
                endpoint=endpoint,
                status_code=response.status_code,
                latency_ms=round(latency_ms, 2),
            )

            return response

        except Exception as exc:
            latency_ms = (time.perf_counter() - start_time) * 1000

            await event_bus.publish(
                RequestEvent(
                    event_type=EventType.REQUEST_FAILED,
                    request_id=request_id,
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=500,
                    latency_ms=round(latency_ms, 2),
                )
            )

            logger.error(
                "Request failed",
                endpoint=endpoint,
                error=str(exc),
                latency_ms=round(latency_ms, 2),
            )
            raise
