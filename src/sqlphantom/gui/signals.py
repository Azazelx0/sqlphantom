"""
PySide6 Signal Bridge connecting domain EventBus to Qt GUI thread.
"""

from PySide6.QtCore import QObject, Signal

from sqlphantom.application.event_bus import EventBus
from sqlphantom.domain.events import (
    FindingDiscovered,
    JobCancelled,
    JobCompleted,
    JobFailed,
    ProgressUpdated,
    StageChanged,
)


class EventSignalBridge(QObject):
    """
    Bridges asynchronous background domain events from EventBus into
    thread-safe PySide6 Qt signals.
    """

    stage_changed = Signal(str, str)  # (stage, previous_stage)
    progress_updated = Signal(float, str)  # (progress, message)
    finding_discovered = Signal(str, str, str, str, str)  # (finding_id, type, severity, param, title)
    job_completed = Signal(int, float)  # (findings_count, duration)
    job_cancelled = Signal(str)  # (reason)
    job_failed = Signal(str)  # (error)

    def __init__(self, event_bus: EventBus):
        super().__init__()
        self.event_bus = event_bus
        self._subscribe()

    def _subscribe(self) -> None:
        self.event_bus.subscribe(StageChanged, lambda e: self.stage_changed.emit(e.stage, e.previous_stage or ""))
        self.event_bus.subscribe(ProgressUpdated, lambda e: self.progress_updated.emit(e.progress, e.message))
        self.event_bus.subscribe(
            FindingDiscovered,
            lambda e: self.finding_discovered.emit(
                e.finding_id, e.finding_type, e.severity, e.parameter, e.title
            ),
        )
        self.event_bus.subscribe(JobCompleted, lambda e: self.job_completed.emit(e.findings_count, e.duration_seconds))
        self.event_bus.subscribe(JobCancelled, lambda e: self.job_cancelled.emit(e.reason))
        self.event_bus.subscribe(JobFailed, lambda e: self.job_failed.emit(e.error))
