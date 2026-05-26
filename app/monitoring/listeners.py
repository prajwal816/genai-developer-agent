"""
Event listeners — Observers in the Observer Pattern.

- MetricsListener: Aggregates Prometheus-style metrics.
- LoggingListener: Structured log output for all events.
- AlertListener: Triggers alerts on error thresholds.
"""

from __future__ import annotations

import time
from collections import defaultdict

from app.core.logging import get_logger
from app.monitoring.events import (
    AgentEvent,
    ErrorEvent,
    Event,
    EventType,
    RequestEvent,
)

logger = get_logger(__name__)


class MetricsListener:
    """
    Observer that aggregates application metrics.

    Tracks request counts, latency percentiles, error rates,
    and agent execution timings.
    """

    def __init__(self) -> None:
        self.total_requests: int = 0
        self.requests_per_endpoint: dict[str, int] = defaultdict(int)
        self.latencies: list[float] = []
        self.error_count: int = 0
        self.agent_execution_times: dict[str, list[float]] = defaultdict(list)
        self.active_requests: int = 0
        self._start_time = time.time()

    async def handle_event(self, event: Event) -> None:
        """Process an event and update metrics."""
        if isinstance(event, RequestEvent):
            await self._handle_request_event(event)
        elif isinstance(event, AgentEvent):
            await self._handle_agent_event(event)
        elif isinstance(event, ErrorEvent):
            self.error_count += 1

    async def _handle_request_event(self, event: RequestEvent) -> None:
        """Update request metrics."""
        if event.event_type == EventType.REQUEST_STARTED:
            self.active_requests += 1
        elif event.event_type == EventType.REQUEST_COMPLETED:
            self.total_requests += 1
            self.active_requests = max(0, self.active_requests - 1)
            self.requests_per_endpoint[event.endpoint] = (
                self.requests_per_endpoint.get(event.endpoint, 0) + 1
            )
            if event.latency_ms > 0:
                self.latencies.append(event.latency_ms)
        elif event.event_type == EventType.REQUEST_FAILED:
            self.active_requests = max(0, self.active_requests - 1)
            self.error_count += 1

    async def _handle_agent_event(self, event: AgentEvent) -> None:
        """Update agent execution metrics."""
        if event.event_type == EventType.AGENT_EXECUTION_COMPLETED:
            self.agent_execution_times[event.agent_name].append(
                event.execution_time_ms
            )

    def get_average_latency(self) -> float:
        """Return average request latency in ms."""
        if not self.latencies:
            return 0.0
        return round(sum(self.latencies) / len(self.latencies), 2)

    def get_percentile_latency(self, percentile: float) -> float:
        """Return the Nth percentile latency."""
        if not self.latencies:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        index = int(len(sorted_latencies) * percentile / 100)
        index = min(index, len(sorted_latencies) - 1)
        return round(sorted_latencies[index], 2)

    def get_error_rate(self) -> float:
        """Return error rate as a percentage."""
        if self.total_requests == 0:
            return 0.0
        return round(self.error_count / self.total_requests * 100, 2)

    def get_uptime_seconds(self) -> float:
        """Return uptime in seconds."""
        return round(time.time() - self._start_time, 2)

    def get_agent_avg_times(self) -> dict[str, float]:
        """Return average execution time per agent."""
        result = {}
        for agent, times in self.agent_execution_times.items():
            if times:
                result[agent] = round(sum(times) / len(times), 2)
        return result

    def to_dict(self) -> dict:
        """Export all metrics as a dictionary."""
        return {
            "total_requests": self.total_requests,
            "requests_per_endpoint": dict(self.requests_per_endpoint),
            "average_latency_ms": self.get_average_latency(),
            "p95_latency_ms": self.get_percentile_latency(95),
            "p99_latency_ms": self.get_percentile_latency(99),
            "error_count": self.error_count,
            "error_rate": self.get_error_rate(),
            "agent_execution_times": self.get_agent_avg_times(),
            "uptime_seconds": self.get_uptime_seconds(),
            "active_requests": self.active_requests,
        }


class LoggingListener:
    """
    Observer that emits structured log entries for every event.
    """

    async def handle_event(self, event: Event) -> None:
        """Log the event with structured context."""
        log_data = {
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
        }

        if isinstance(event, RequestEvent):
            log_data.update({
                "request_id": event.request_id,
                "endpoint": event.endpoint,
                "method": event.method,
                "status_code": event.status_code,
                "latency_ms": event.latency_ms,
            })
        elif isinstance(event, AgentEvent):
            log_data.update({
                "agent_name": event.agent_name,
                "execution_time_ms": event.execution_time_ms,
                "success": event.success,
            })
            if event.error_message:
                log_data["error_message"] = event.error_message
        elif isinstance(event, ErrorEvent):
            log_data.update({
                "error_code": event.error_code,
                "error_message": event.error_message,
                "endpoint": event.endpoint,
            })

        if event.event_type in (
            EventType.REQUEST_FAILED,
            EventType.AGENT_EXECUTION_FAILED,
            EventType.ERROR_OCCURRED,
        ):
            logger.error("Event occurred", **log_data)
        else:
            logger.info("Event occurred", **log_data)


class AlertListener:
    """
    Observer that triggers alerts when error thresholds are exceeded.
    """

    def __init__(
        self,
        error_threshold: int = 10,
        latency_threshold_ms: float = 5000.0,
    ) -> None:
        self._error_threshold = error_threshold
        self._latency_threshold_ms = latency_threshold_ms
        self._error_window: list[float] = []
        self._alert_count = 0

    async def handle_event(self, event: Event) -> None:
        """Check if the event triggers an alert condition."""
        if isinstance(event, ErrorEvent):
            self._error_window.append(event.timestamp.timestamp())
            # Keep only last 60 seconds of errors
            cutoff = time.time() - 60
            self._error_window = [t for t in self._error_window if t > cutoff]

            if len(self._error_window) >= self._error_threshold:
                self._alert_count += 1
                logger.warning(
                    "ALERT: Error threshold exceeded",
                    errors_in_window=len(self._error_window),
                    threshold=self._error_threshold,
                    alert_number=self._alert_count,
                )

        elif isinstance(event, RequestEvent):
            if (
                event.latency_ms > self._latency_threshold_ms
                and event.event_type == EventType.REQUEST_COMPLETED
            ):
                self._alert_count += 1
                logger.warning(
                    "ALERT: High latency detected",
                    endpoint=event.endpoint,
                    latency_ms=event.latency_ms,
                    threshold_ms=self._latency_threshold_ms,
                    alert_number=self._alert_count,
                )
