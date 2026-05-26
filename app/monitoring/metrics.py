"""
Prometheus-compatible metrics definitions and collector.
"""

from __future__ import annotations

from app.monitoring.event_bus import EventBus
from app.monitoring.events import EventType
from app.monitoring.listeners import AlertListener, LoggingListener, MetricsListener
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Singleton metrics listener accessible for /metrics endpoint
_metrics_listener: MetricsListener | None = None


def get_metrics_listener() -> MetricsListener:
    """Return the singleton MetricsListener."""
    global _metrics_listener
    if _metrics_listener is None:
        _metrics_listener = MetricsListener()
    return _metrics_listener


def setup_monitoring() -> None:
    """
    Initialize the monitoring subsystem.

    Registers all listeners with the EventBus for the Observer Pattern.
    """
    settings = get_settings()
    event_bus = EventBus.get_instance()

    # --- MetricsListener (global — listens to all events) ---
    metrics = get_metrics_listener()
    event_bus.subscribe(None, metrics.handle_event)

    # --- LoggingListener (global) ---
    logging_listener = LoggingListener()
    event_bus.subscribe(None, logging_listener.handle_event)

    # --- AlertListener (errors and request completions) ---
    alert_listener = AlertListener(
        error_threshold=settings.monitoring.alert_error_threshold,
        latency_threshold_ms=settings.monitoring.alert_latency_threshold_ms,
    )
    event_bus.subscribe(EventType.ERROR_OCCURRED, alert_listener.handle_event)
    event_bus.subscribe(EventType.REQUEST_COMPLETED, alert_listener.handle_event)
    event_bus.subscribe(EventType.REQUEST_FAILED, alert_listener.handle_event)

    logger.info(
        "Monitoring subsystem initialized",
        total_listeners=event_bus.listener_count(),
    )
