"""
EventBus — the Subject in the Observer Pattern.

Provides publish/subscribe functionality for decoupled monitoring.
Listeners register for specific event types and are notified asynchronously.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Callable, Coroutine, Any

from app.core.logging import get_logger
from app.monitoring.events import Event, EventType

logger = get_logger(__name__)

# Listener type: async callable accepting an Event
EventListener = Callable[[Event], Coroutine[Any, Any, None]]


class EventBus:
    """
    Central event bus implementing the Observer Pattern.

    Design Pattern: **Observer Pattern**
    - EventBus is the Subject.
    - Listeners (MetricsListener, LoggingListener, AlertListener) are Observers.
    - Services emit events; listeners react independently.
    - Supports async listeners for non-blocking processing.

    This is a singleton — use ``EventBus.get_instance()`` to access.
    """

    _instance: EventBus | None = None

    def __init__(self) -> None:
        self._listeners: dict[EventType, list[EventListener]] = defaultdict(list)
        self._global_listeners: list[EventListener] = []

    @classmethod
    def get_instance(cls) -> EventBus:
        """Return the singleton EventBus instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (primarily for testing)."""
        cls._instance = None

    def subscribe(
        self,
        event_type: EventType | None,
        listener: EventListener,
    ) -> None:
        """
        Subscribe a listener to events.

        Args:
            event_type: Specific event type to listen for, or None for all events.
            listener: Async callable that processes the event.
        """
        if event_type is None:
            self._global_listeners.append(listener)
            logger.debug("Registered global event listener", listener=listener.__qualname__)
        else:
            self._listeners[event_type].append(listener)
            logger.debug(
                "Registered event listener",
                event_type=event_type.value,
                listener=listener.__qualname__,
            )

    async def publish(self, event: Event) -> None:
        """
        Publish an event to all registered listeners.

        Listeners are called asynchronously. Errors in individual
        listeners are caught and logged — they do not prevent other
        listeners from being notified.

        Args:
            event: The event to publish.
        """
        listeners = [
            *self._global_listeners,
            *self._listeners.get(event.event_type, []),
        ]

        if not listeners:
            return

        tasks = [self._safe_notify(listener, event) for listener in listeners]
        await asyncio.gather(*tasks)

    async def _safe_notify(self, listener: EventListener, event: Event) -> None:
        """Notify a listener with error isolation."""
        try:
            await listener(event)
        except Exception as exc:
            logger.error(
                "Event listener error",
                listener=listener.__qualname__,
                event_type=event.event_type.value,
                error=str(exc),
            )

    def listener_count(self, event_type: EventType | None = None) -> int:
        """Return the number of listeners for a given event type."""
        if event_type is None:
            return len(self._global_listeners) + sum(
                len(v) for v in self._listeners.values()
            )
        return len(self._listeners.get(event_type, []))
