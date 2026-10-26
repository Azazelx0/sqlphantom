"""
SQLPhantom structured lifecycle events.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class BaseEvent:
    """Base class for all domain events."""
    job_id: str
    event_id: str = field(default_factory=lambda: uuid4().hex)
    timestamp: datetime = field(default_factory=_utc_now)


@dataclass(frozen=True)
class JobCreated(BaseEvent):
    """Fired when an assessment job has been created and configured."""
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class JobStarted(BaseEvent):
    """Fired when an assessment worker begins execution."""
    pass


@dataclass(frozen=True)
class StageChanged(BaseEvent):
    """Fired when the assessment transitions to another execution stage."""
    stage: str = ""
    previous_stage: str | None = None


@dataclass(frozen=True)
class ProgressUpdated(BaseEvent):
    """Fired when progress percentage or execution status message updates."""
    progress: float = 0.0
    message: str = ""


@dataclass(frozen=True)
class FindingDiscovered(BaseEvent):
    """Fired when a new vulnerability finding is detected and verified."""
    finding_id: str = ""
    finding_type: str = ""
    severity: str = ""
    parameter: str = ""
    url: str = ""
    title: str = ""


@dataclass(frozen=True)
class JobCancelled(BaseEvent):
    """Fired when an active job is stopped due to user cancellation."""
    reason: str = "User requested cancellation"


@dataclass(frozen=True)
class JobFailed(BaseEvent):
    """Fired when an unrecoverable error terminates job execution."""
    error: str = ""
    traceback: str | None = None


@dataclass(frozen=True)
class JobCompleted(BaseEvent):
    """Fired when an assessment finishes all stages cleanly."""
    findings_count: int = 0
    duration_seconds: float = 0.0
