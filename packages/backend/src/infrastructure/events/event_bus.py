"""Event bus for domain event publishing and handling."""

from collections import defaultdict
from typing import Any, Callable, Coroutine, Dict, List, Type

from domain.events import DomainEvent


EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]


class EventBus:
    """In-memory event bus for publishing and handling domain events."""

    def __init__(self):
        """Initialize the event bus with empty handlers."""
        self._handlers: Dict[Type[DomainEvent], List[EventHandler]] = (
            defaultdict(list)
        )

    def subscribe(
        self, event_type: Type[DomainEvent], handler: EventHandler
    ) -> None:
        """
        Subscribe a handler to a specific event type.

        Args:
            event_type: The type of event to subscribe to
            handler: Async function to handle the event
        """
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all registered handlers.

        Args:
            event: The domain event to publish
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        # Execute all handlers asynchronously
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                # Log error but don't stop other handlers
                # In production, you'd want proper error logging here
                print(f"Error in event handler for {event_type.__name__}: {e}")

    def clear_handlers(
        self, event_type: Type[DomainEvent] | None = None
    ) -> None:
        """
        Clear handlers for a specific event type or all handlers.

        Args:
            event_type: Optional event type to clear handlers for.
                       If None, clears all handlers.
        """
        if event_type:
            self._handlers[event_type] = []
        else:
            self._handlers.clear()


# Global event bus instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return _event_bus
