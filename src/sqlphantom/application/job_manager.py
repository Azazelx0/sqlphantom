"""
SQLPhantom job manager orchestrating assessment lifecycle and worker monitoring.
"""

from datetime import datetime, timezone
import logging
import threading
import time
from uuid import uuid4

from sqlphantom.application.event_bus import EventBus
from sqlphantom.domain.enums import AssessmentStage, JobStatus
from sqlphantom.domain.events import (
    FindingDiscovered,
    JobCancelled,
    JobCompleted,
    JobCreated,
    JobFailed,
    JobStarted,
    ProgressUpdated,
    StageChanged,
)
from sqlphantom.domain.models import AssessmentConfig, JobResult
from sqlphantom.domain.scope import validate_target_in_scope
from sqlphantom.engine.adapter import EngineAdapter

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobContext:
    """Internal tracking context for an active assessment job."""

    def __init__(self, job_id: str, config: AssessmentConfig):
        self.job_id = job_id
        self.config = config
        self.status = JobStatus.CREATED
        self.created_at = _utc_now()
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None
        self.last_stage = AssessmentStage.INITIALIZATION
        self.last_progress = 0.0
        self.known_finding_ids: set[str] = set()
        self.monitor_thread: threading.Thread | None = None
        self.stop_monitor = threading.Event()


class JobManager:
    """
    Central orchestration service managing job lifecycles, scope enforcement,
    engine interactions, and domain event dispatch.
    """

    def __init__(
        self,
        event_bus: EventBus,
        engine: EngineAdapter,
        poll_interval: float = 0.1,
    ):
        self.event_bus = event_bus
        self.engine = engine
        self.poll_interval = poll_interval
        self._jobs: dict[str, JobContext] = {}
        self._lock = threading.RLock()

    def create_job(self, config: AssessmentConfig) -> str:
        """
        Validate target against scope constraints, initialize job tracking context,
        and emit JobCreated event.
        """
        in_scope, reason = validate_target_in_scope(config.target, config.scope)
        if not in_scope:
            raise ValueError(f"Target validation rejected: {reason}")

        job_id = uuid4().hex
        context = JobContext(job_id=job_id, config=config)

        with self._lock:
            self._jobs[job_id] = context

        self.event_bus.publish(
            JobCreated(
                job_id=job_id,
                config=config.model_dump(mode="json"),
            )
        )
        return job_id

    def start_job(self, job_id: str) -> None:
        """
        Launch execution of an existing job via the configured engine adapter
        and initiate asynchronous lifecycle monitoring.
        """
        with self._lock:
            context = self._jobs.get(job_id)
            if not context:
                raise KeyError(f"Job '{job_id}' not found")
            if context.status != JobStatus.CREATED:
                raise ValueError(
                    f"Job '{job_id}' is in status '{context.status}', cannot start"
                )
            context.status = JobStatus.RUNNING
            context.started_at = _utc_now()

        # Delegate start to engine
        self.engine.start_scan(job_id, context.config)
        self.event_bus.publish(JobStarted(job_id=job_id))

        # Start supervisor thread to monitor engine state transitions
        monitor = threading.Thread(
            target=self._monitor_worker,
            args=(context,),
            name=f"JobMonitor-{job_id}",
            daemon=True,
        )
        context.monitor_thread = monitor
        monitor.start()

    def cancel_job(
        self, job_id: str, reason: str = "User requested cancellation"
    ) -> bool:
        """
        Request cancellation of a currently executing job.
        """
        with self._lock:
            context = self._jobs.get(job_id)
            if not context:
                return False
            context.status = JobStatus.CANCELLING

        cancelled = self.engine.cancel_scan(job_id)
        self.event_bus.publish(JobCancelled(job_id=job_id, reason=reason))
        return cancelled

    def get_status(self, job_id: str) -> JobResult:
        """
        Query current job status and findings directly from the engine adapter.
        """
        return self.engine.get_status(job_id)

    def list_jobs(self) -> list[str]:
        """Return a list of all managed job identifiers."""
        with self._lock:
            return list(self._jobs.keys())

    def get_context(self, job_id: str) -> JobContext | None:
        """Return the internal context for a job if available."""
        with self._lock:
            return self._jobs.get(job_id)

    def _monitor_worker(self, context: JobContext) -> None:
        """
        Background polling worker that observes engine status, detects changes,
        and fires appropriate domain events.
        """
        job_id = context.job_id
        start_time = time.time()

        while not context.stop_monitor.is_set():
            status_result = self.engine.get_status(job_id)

            # Detect stage transitions
            if status_result.stage != context.last_stage:
                self.event_bus.publish(
                    StageChanged(
                        job_id=job_id,
                        stage=str(status_result.stage),
                        previous_stage=str(context.last_stage),
                    )
                )
                context.last_stage = status_result.stage

            # Detect progress updates
            if abs(status_result.progress - context.last_progress) >= 0.5:
                self.event_bus.publish(
                    ProgressUpdated(
                        job_id=job_id,
                        progress=status_result.progress,
                        message=status_result.log_entries[-1]
                        if status_result.log_entries
                        else "",
                    )
                )
                context.last_progress = status_result.progress

            # Detect newly discovered findings
            for finding in status_result.findings:
                if finding.id not in context.known_finding_ids:
                    context.known_finding_ids.add(finding.id)
                    self.event_bus.publish(
                        FindingDiscovered(
                            job_id=job_id,
                            finding_id=finding.id,
                            finding_type=str(finding.finding_type),
                            severity=str(finding.severity),
                            parameter=finding.parameter,
                            url=finding.url,
                            title=finding.title,
                        )
                    )

            # Check for terminal status
            if status_result.status == JobStatus.COMPLETED:
                duration = time.time() - start_time
                context.status = JobStatus.COMPLETED
                self.event_bus.publish(
                    JobCompleted(
                        job_id=job_id,
                        findings_count=len(status_result.findings),
                        duration_seconds=duration,
                    )
                )
                break
            elif status_result.status == JobStatus.FAILED:
                context.status = JobStatus.FAILED
                self.event_bus.publish(
                    JobFailed(
                        job_id=job_id,
                        error=status_result.error_message or "Unknown engine error",
                    )
                )
                break
            elif status_result.status == JobStatus.CANCELLED:
                context.status = JobStatus.CANCELLED
                break

            time.sleep(self.poll_interval)
