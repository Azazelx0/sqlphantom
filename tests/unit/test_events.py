"""
Unit tests for SQLPhantom domain events.
"""

from sqlphantom.domain.events import (
    BaseEvent,
    FindingDiscovered,
    JobCancelled,
    JobCompleted,
    JobCreated,
    JobFailed,
    JobStarted,
    ProgressUpdated,
    StageChanged,
)


def test_base_event_fields():
    event = BaseEvent(job_id="job-123")
    assert event.job_id == "job-123"
    assert event.event_id is not None
    assert event.timestamp is not None


def test_job_lifecycle_events():
    created = JobCreated(job_id="job-1", config={"threads": 2})
    assert created.config["threads"] == 2

    started = JobStarted(job_id="job-1")
    assert started.job_id == "job-1"

    stage = StageChanged(job_id="job-1", stage="DETECTION", previous_stage="FINGERPRINTING")
    assert stage.stage == "DETECTION"
    assert stage.previous_stage == "FINGERPRINTING"

    progress = ProgressUpdated(job_id="job-1", progress=50.0, message="Testing parameter 'id'")
    assert progress.progress == 50.0

    finding = FindingDiscovered(
        job_id="job-1",
        finding_id="f-1",
        finding_type="UNION_BASED",
        severity="CRITICAL",
        parameter="user",
        url="http://example.com/user",
        title="Union injection discovered",
    )
    assert finding.finding_id == "f-1"

    cancelled = JobCancelled(job_id="job-1", reason="Timeout reached")
    assert cancelled.reason == "Timeout reached"

    failed = JobFailed(job_id="job-1", error="Connection refused")
    assert failed.error == "Connection refused"

    completed = JobCompleted(job_id="job-1", findings_count=3, duration_seconds=12.4)
    assert completed.findings_count == 3
    assert completed.duration_seconds == 12.4
