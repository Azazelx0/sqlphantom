"""
SQLPhantom thread-safe publish/subscribe event bus.
"""

from collections import defaultdict
from collections.abc import Callable
import logging
import threading
from typing import TypeVar
from uuid import uuid4

from sqlphantom.domain.events import BaseEvent

logger = logging.getLogger(__name__)

E = TypeVar("E", bound=BaseEvent)


class EventBus:
    """
    Central in-memory, thread-safe publish-subscribe bus for domain events.
    Supports typed subscriptions, catch-all subscriptions, and resilient dispatch.
    """

    def __init__(self, async_dispatch: bool = False):
        self._async_dispatch = async_dispatch
        self._lock = threading.RLock()
        # Mapping from Event Type -> dict of {subscription_id: callback}
        self._subscribers: dict[type, dict[str, Callable[[Any], None]]] = defaultdict(dict)
        # Catch-all subscribers that receive all events
        self._all_subscribers: dict[str, Callable[[BaseEvent], None]] = {}

    def subscribe(self, event_type: type[E], callback: Callable[[E], None]) -> str:
        """
        Register a callback listener for a specific event type.
        Returns a unique subscription identifier.
        """
        sub_id = uuid4().hex
        with self._lock:
            self._subscribers[event_type][sub_id] = callback
        return sub_id

    def subscribe_all(self, callback: Callable[[BaseEvent], None]) -> str:
        """
        Register a callback listener for all event types.
        Returns a unique subscription identifier.
        """
        sub_id = uuid4().hex
        with self._lock:
            self._all_subscribers[sub_id] = callback
        return sub_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Remove a registered subscription by its identifier.
        """
        with self._lock:
            if subscription_id in self._all_subscribers:
                del self._all_subscribers[subscription_id]
                return True

            for type_subs in self._subscribers.values():
                if subscription_id in type_subs:
                    del type_subs[subscription_id]
                    return True
        return False

    def publish(self, event: BaseEvent) -> None:
        """
        Publish an event to all registered matching and catch-all subscribers.
        """
        with self._lock:
            # Collect matching callbacks for this event type and parent types
            targets: list[Callable[[BaseEvent], None]] = []

            for subscribed_type, subs in self._subscribers.items():
                if isinstance(event, subscribed_type):
                    targets.extend(subs.values())

            # Add catch-all subscribers
            targets.extend(self._all_subscribers.values())

        if not targets:
            return

        if self._async_dispatch:
            threading.Thread(
                target=self._dispatch_all,
                args=(targets, event),
                name=f"EventDispatch-{event.event_id}",
                daemon=True,
            ).start()
        else:
            self._dispatch_all(targets, event)

    def _dispatch_all(
        self, callbacks: list[Callable[[BaseEvent], None]], event: BaseEvent
    ) -> None:
        for cb in callbacks:
            try:
                cb(event)
            except Exception as exc:
                logger.error(
                    "Error executing event subscriber for %s: %s",
                    type(event).__name__,
                    exc,
                    exc_info=True,
                )

    def clear(self) -> None:
        """Clear all active subscriptions."""
        with self._lock:
            self._subscribers.clear()
            self._all_subscribers.clear()
