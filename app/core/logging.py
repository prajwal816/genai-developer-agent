"""
Structured logging configuration using ``structlog``.

Produces JSON-formatted log lines with request correlation IDs,
timestamps, and contextual metadata for production observability.
"""

from __future__ import annotations

import logging
import sys
import uuid

import structlog

from app.core.config import get_settings


def _generate_correlation_id() -> str:
    """Generate a unique correlation ID for request tracing."""
    return str(uuid.uuid4())


def setup_logging() -> None:
    """
    Configure structlog and stdlib logging for the application.

    - JSON rendering in production, colored console in debug mode.
    - Adds timestamps, log level, and caller information.
    """
    settings = get_settings()
    log_level = getattr(logging, settings.monitoring.log_level.upper(), logging.INFO)
    is_debug = settings.app_debug

    # Shared processors
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if is_debug:
        # Human-readable output for development
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        # JSON output for production log aggregation
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Suppress noisy third-party loggers
    for name in ("uvicorn.access", "httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structured logger bound with the given name."""
    return structlog.get_logger(name or __name__)
