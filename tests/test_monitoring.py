"""
Tests for the monitoring/observability system (Observer Pattern).
"""

from __future__ import annotations

import pytest

from app.monitoring.event_bus import EventBus
from app.monitoring.events import (
    AgentEvent,
    ErrorEvent,
    EventType,
    RequestEvent,
)
from app.monitoring.listeners import AlertListener, LoggingListener, MetricsListener


@pytest.mark.asyncio
class TestEventBus:
    """Tests for the EventBus (Subject in Observer Pattern)."""

    async def test_publish_to_subscriber(self):
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe(EventType.REQUEST_COMPLETED, handler)
        event = RequestEvent(event_type=EventType.REQUEST_COMPLETED, endpoint="/test")
        await bus.publish(event)

        assert len(received) == 1
        assert received[0].endpoint == "/test"

    async def test_global_subscriber_receives_all(self):
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe(None, handler)
        await bus.publish(RequestEvent(event_type=EventType.REQUEST_STARTED))
        await bus.publish(AgentEvent(event_type=EventType.AGENT_EXECUTION_COMPLETED))

        assert len(received) == 2

    async def test_subscriber_isolation(self):
        bus = EventBus()
        received = []

        async def good_handler(event):
            received.append(event)

        async def bad_handler(event):
            raise RuntimeError("Listener error")

        bus.subscribe(EventType.REQUEST_COMPLETED, bad_handler)
        bus.subscribe(EventType.REQUEST_COMPLETED, good_handler)

        await bus.publish(RequestEvent(event_type=EventType.REQUEST_COMPLETED))
        assert len(received) == 1  # Good handler still fires

    async def test_singleton_pattern(self):
        bus1 = EventBus.get_instance()
        bus2 = EventBus.get_instance()
        assert bus1 is bus2

    async def test_listener_count(self):
        bus = EventBus()

        async def handler(event):
            pass

        bus.subscribe(EventType.REQUEST_STARTED, handler)
        bus.subscribe(EventType.REQUEST_STARTED, handler)
        assert bus.listener_count(EventType.REQUEST_STARTED) == 2
        assert bus.listener_count(EventType.ERROR_OCCURRED) == 0


@pytest.mark.asyncio
class TestMetricsListener:
    """Tests for the MetricsListener."""

    async def test_request_counting(self):
        listener = MetricsListener()
        event = RequestEvent(
            event_type=EventType.REQUEST_COMPLETED,
            endpoint="/review",
            latency_ms=150.0,
        )
        await listener.handle_event(event)
        assert listener.total_requests == 1
        assert listener.requests_per_endpoint["/review"] == 1

    async def test_latency_tracking(self):
        listener = MetricsListener()
        for latency in [100, 200, 300]:
            await listener.handle_event(
                RequestEvent(
                    event_type=EventType.REQUEST_COMPLETED,
                    latency_ms=latency,
                )
            )
        assert listener.get_average_latency() == 200.0

    async def test_error_counting(self):
        listener = MetricsListener()
        await listener.handle_event(
            RequestEvent(event_type=EventType.REQUEST_FAILED)
        )
        assert listener.error_count == 1

    async def test_agent_timing(self):
        listener = MetricsListener()
        await listener.handle_event(
            AgentEvent(
                event_type=EventType.AGENT_EXECUTION_COMPLETED,
                agent_name="test_agent",
                execution_time_ms=250.0,
            )
        )
        avg_times = listener.get_agent_avg_times()
        assert avg_times["test_agent"] == 250.0

    async def test_to_dict(self):
        listener = MetricsListener()
        data = listener.to_dict()
        assert "total_requests" in data
        assert "average_latency_ms" in data
        assert "error_rate" in data
        assert "uptime_seconds" in data


@pytest.mark.asyncio
class TestLoggingListener:
    """Tests for the LoggingListener."""

    async def test_handles_request_event(self):
        listener = LoggingListener()
        # Should not raise
        await listener.handle_event(
            RequestEvent(
                event_type=EventType.REQUEST_COMPLETED,
                endpoint="/test",
                latency_ms=100,
            )
        )

    async def test_handles_error_event(self):
        listener = LoggingListener()
        await listener.handle_event(
            ErrorEvent(
                event_type=EventType.ERROR_OCCURRED,
                error_code="TEST_ERROR",
                error_message="Test error",
            )
        )


@pytest.mark.asyncio
class TestAlertListener:
    """Tests for the AlertListener."""

    async def test_no_alert_below_threshold(self):
        listener = AlertListener(error_threshold=5)
        for _ in range(4):
            await listener.handle_event(
                ErrorEvent(
                    event_type=EventType.ERROR_OCCURRED,
                    error_code="TEST",
                    error_message="error",
                )
            )
        assert listener._alert_count == 0

    async def test_alert_at_threshold(self):
        listener = AlertListener(error_threshold=3)
        for _ in range(3):
            await listener.handle_event(
                ErrorEvent(
                    event_type=EventType.ERROR_OCCURRED,
                    error_code="TEST",
                    error_message="error",
                )
            )
        assert listener._alert_count == 1

    async def test_latency_alert(self):
        listener = AlertListener(latency_threshold_ms=100)
        await listener.handle_event(
            RequestEvent(
                event_type=EventType.REQUEST_COMPLETED,
                latency_ms=200,
            )
        )
        assert listener._alert_count == 1
