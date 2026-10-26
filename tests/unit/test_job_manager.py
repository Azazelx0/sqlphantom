"""
Unit tests for JobManager orchestration and lifecycle events.
"""

import time
import pytest

from sqlphantom.application.event_bus import EventBus
from sqlphantom.application.job_manager import JobManager
from sqlphantom.domain.enums import JobStatus
from sqlphantom.domain.events import JobCancelled, JobCreated, JobStarted
from sqlphantom.domain.models import AssessmentConfig, ScopeRule, Target
from sqlphantom.engine.mock_adapter import MockEngineAdapter


def test_create_job_in_scope():
    bus = EventBus(async_dispatch=False)
    engine = MockEngineAdapter(stage_duration=0.05)
    manager = JobManager(event_bus=bus, engine=engine)

    target = Target(url="http://vulnweb.com/test.php?id=1")
    scope = ScopeRule(allowed_domains=["vulnweb.com"], block_private_ips=False)
    config = AssessmentConfig(target=target, scope=scope)

    created_events = []
    bus.subscribe(JobCreated, lambda ev: created_events.append(ev))

    job_id = manager.create_job(config)
    assert job_id is not None
    assert len(created_events) == 1
    assert created_events[0].job_id == job_id


def test_create_job_out_of_scope_raises():
    bus = EventBus()
    engine = MockEngineAdapter()
    manager = JobManager(event_bus=bus, engine=engine)

    target = Target(url="http://evil.com/test.php?id=1")
    scope = ScopeRule(allowed_domains=["authorized.com"], block_private_ips=True)
    config = AssessmentConfig(target=target, scope=scope)

    with pytest.raises(ValueError, match="Target validation rejected"):
        manager.create_job(config)


def test_job_start_and_cancellation():
    bus = EventBus(async_dispatch=False)
    # Give enough duration to catch it during cancellation
    engine = MockEngineAdapter(stage_duration=0.5)
    manager = JobManager(event_bus=bus, engine=engine, poll_interval=0.02)

    target = Target(url="http://authorized.com/test.php?id=1")
    scope = ScopeRule(allowed_domains=["authorized.com"], block_private_ips=False)
    config = AssessmentConfig(target=target, scope=scope)

    job_id = manager.create_job(config)

    cancelled_events = []
    bus.subscribe(JobCancelled, lambda ev: cancelled_events.append(ev))

    manager.start_job(job_id)
    time.sleep(0.05)

    cancelled = manager.cancel_job(job_id)
    assert cancelled is True
    assert len(cancelled_events) == 1
    assert cancelled_events[0].job_id == job_id

    # Give engine worker a moment to finalize cancellation
    time.sleep(0.1)
    status = manager.get_status(job_id)
    assert status.status in (JobStatus.CANCELLED, JobStatus.CANCELLING)
