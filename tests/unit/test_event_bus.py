"""
Unit tests for the thread-safe EventBus.
"""

from sqlphantom.application.event_bus import EventBus
from sqlphantom.domain.events import BaseEvent, JobCreated, JobStarted


def test_typed_subscription():
    bus = EventBus(async_dispatch=False)
    received = []

    def on_job_started(event: JobStarted):
        received.append(event)

    bus.subscribe(JobStarted, on_job_started)

    # Publish an unrelated event
    bus.publish(JobCreated(job_id="j-1", config={}))
    assert len(received) == 0

    # Publish targeted event
    e_start = JobStarted(job_id="j-1")
    bus.publish(e_start)
    assert len(received) == 1
    assert received[0].job_id == "j-1"


def test_catch_all_subscription():
    bus = EventBus(async_dispatch=False)
    events = []

    bus.subscribe_all(lambda ev: events.append(ev))

    bus.publish(JobCreated(job_id="j-1", config={}))
    bus.publish(JobStarted(job_id="j-1"))

    assert len(events) == 2


def test_unsubscribe():
    bus = EventBus(async_dispatch=False)
    items = []

    sub_id = bus.subscribe(JobStarted, lambda ev: items.append(ev))
    bus.publish(JobStarted(job_id="j-1"))
    assert len(items) == 1

    removed = bus.unsubscribe(sub_id)
    assert removed is True

    bus.publish(JobStarted(job_id="j-2"))
    assert len(items) == 1


def test_subscriber_exception_resilience():
    bus = EventBus(async_dispatch=False)
    success_tracker = []

    def failing_cb(ev):
        raise RuntimeError("Unexpected failure in subscriber")

    def successful_cb(ev):
        success_tracker.append(ev)

    bus.subscribe_all(failing_cb)
    bus.subscribe_all(successful_cb)

    # Should not raise exception
    bus.publish(JobStarted(job_id="j-safe"))
    assert len(success_tracker) == 1
