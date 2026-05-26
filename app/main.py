"""
FastAPI application entry point.

Configures the application with:
- Lifespan events (startup/shutdown)
- Middleware (request logging, CORS)
- Exception handlers
- Router inclusion
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import shutdown_dependencies
from app.api.routes import router
from app.core.config import get_settings
from app.core.exceptions import AgentPlatformError
from app.core.logging import setup_logging, get_logger
from app.middleware.error_handler import global_exception_handler
from app.middleware.request_logger import RequestLoggingMiddleware
from app.monitoring.metrics import setup_monitoring

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan manager.

    Handles startup initialization and graceful shutdown.
    """
    # ── Startup ──
    setup_logging()
    setup_monitoring()

    settings = get_settings()
    logger.info(
        "Application starting",
        app_name=settings.app_name,
        version=settings.app_version,
        llm_provider=settings.llm.provider,
        debug=settings.app_debug,
    )

    yield

    # ── Shutdown ──
    logger.info("Application shutting down")
    await shutdown_dependencies()


def create_app() -> FastAPI:
    """
    Application factory — creates and configures the FastAPI app.

    Returns:
        Configured FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Production-grade AI-powered developer assistant backend. "
            "Performs code review, issue classification, and intelligent "
            "suggestion generation using modular LLM agent workflows."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ──
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception Handlers ──
    app.add_exception_handler(AgentPlatformError, global_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    # ── Routes ──
    app.include_router(router, prefix="/api/v1")

    # Also mount at root for convenience
    app.include_router(router)

    return app


# Create the application instance
app = create_app()
