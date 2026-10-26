"""
SQLPhantom mock engine adapter for deterministic testing and offline evaluation.
"""

from datetime import datetime, timezone
import threading
import time
from uuid import uuid4

from sqlphantom.domain.enums import (
    AssessmentStage,
    Confidence,
    FindingType,
    JobStatus,
    Severity,
)
from sqlphantom.domain.models import AssessmentConfig, Finding, JobResult
from sqlphantom.engine.adapter import EngineAdapter


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MockJobState:
    """Internal state tracker for a simulated job."""

    def __init__(self, job_id: str, config: AssessmentConfig, stage_duration: float):
        self.job_id = job_id
        self.config = config
        self.stage_duration = stage_duration
        self.status = JobStatus.CREATED
        self.stage = AssessmentStage.INITIALIZATION
        self.progress = 0.0
        self.findings: list[Finding] = []
        self.log_entries: list[str] = []
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None
        self.error_message: str | None = None
        self.cancel_requested = threading.Event()
        self.thread: threading.Thread | None = None
        self.lock = threading.Lock()


class MockEngineAdapter(EngineAdapter):
    """
    Mock engine implementation simulating assessment lifecycle without real network attacks.
    Ideal for unit tests, workflow validation, and UI development.
    """

    def __init__(self, stage_duration: float = 0.2):
        self.stage_duration = stage_duration
        self._jobs: dict[str, MockJobState] = {}
        self._lock = threading.Lock()

    def start_scan(self, job_id: str, config: AssessmentConfig) -> None:
        with self._lock:
            state = MockJobState(job_id, config, self.stage_duration)
            self._jobs[job_id] = state

        thread = threading.Thread(
            target=self._run_simulation,
            args=(state,),
            name=f"MockScanWorker-{job_id}",
            daemon=True,
        )
        state.thread = thread
        thread.start()

    def get_status(self, job_id: str) -> JobResult:
        with self._lock:
            state = self._jobs.get(job_id)
        if not state:
            return JobResult(
                job_id=job_id,
                status=JobStatus.FAILED,
                error_message=f"Job '{job_id}' not found in mock engine",
            )

        with state.lock:
            return JobResult(
                job_id=state.job_id,
                status=state.status,
                findings=list(state.findings),
                stage=state.stage,
                progress=state.progress,
                started_at=state.started_at,
                completed_at=state.completed_at,
                error_message=state.error_message,
                log_entries=list(state.log_entries),
            )

    def get_findings(self, job_id: str) -> list[Finding]:
        with self._lock:
            state = self._jobs.get(job_id)
        if not state:
            return []
        with state.lock:
            return list(state.findings)

    def cancel_scan(self, job_id: str) -> bool:
        with self._lock:
            state = self._jobs.get(job_id)
        if not state:
            return False

        with state.lock:
            if state.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                return False
            state.status = JobStatus.CANCELLING
            state.cancel_requested.set()
            state.log_entries.append("[*] Cancellation requested by operator")
            return True

    def is_running(self, job_id: str) -> bool:
        with self._lock:
            state = self._jobs.get(job_id)
        if not state:
            return False
        with state.lock:
            return state.status in (JobStatus.RUNNING, JobStatus.CANCELLING, JobStatus.QUEUED)

    def _run_simulation(self, state: MockJobState) -> None:
        with state.lock:
            state.status = JobStatus.RUNNING
            state.started_at = _utc_now()
            state.log_entries.append(f"[*] Starting assessment on {state.config.target.url}")

        stages = [
            (AssessmentStage.INITIALIZATION, 10.0, "[*] Initializing engine and verifying connection"),
            (AssessmentStage.TARGET_PROBE, 25.0, "[*] Testing connection to target URL"),
            (AssessmentStage.FINGERPRINTING, 45.0, "[*] Fingerprinting backend DBMS and web server"),
            (AssessmentStage.DETECTION, 75.0, "[*] Testing parameters for injection vulnerabilities"),
            (AssessmentStage.CLEANUP, 95.0, "[*] Finalizing tests and cleaning temporary state"),
            (AssessmentStage.FINISHED, 100.0, "[+] Assessment completed successfully"),
        ]

        for stage, target_progress, log_msg in stages:
            if state.cancel_requested.is_set():
                with state.lock:
                    state.status = JobStatus.CANCELLED
                    state.completed_at = _utc_now()
                    state.log_entries.append("[-] Assessment cancelled by operator")
                return

            with state.lock:
                state.stage = stage
                state.progress = target_progress
                state.log_entries.append(log_msg)

                # Inject realistic findings during detection stage
                if stage == AssessmentStage.DETECTION and not state.findings:
                    f1 = Finding(
                        id=uuid4().hex,
                        finding_type=FindingType.BOOLEAN_BASED_BLIND,
                        severity=Severity.HIGH,
                        confidence=Confidence.CONFIRMED,
                        parameter="id",
                        payload="id=1 AND 1=1 -- -",
                        url=state.config.target.url,
                        title="Boolean-based blind SQL injection detected on parameter 'id'",
                        description="Parameter 'id' is vulnerable to boolean-based blind SQL injection queries.",
                        evidence="Payload yielded consistent TRUE and FALSE response deviations.",
                        remediation="Use parameterized queries / prepared statements for parameter 'id'.",
                        dbms="PostgreSQL",
                    )
                    f2 = Finding(
                        id=uuid4().hex,
                        finding_type=FindingType.ERROR_BASED,
                        severity=Severity.CRITICAL,
                        confidence=Confidence.CONFIRMED,
                        parameter="cat",
                        payload="cat=1' OR 1=CAST((SELECT version()) AS int) --",
                        url=state.config.target.url,
                        title="Error-based SQL injection detected on parameter 'cat'",
                        description="Target DBMS leaked syntax errors containing requested query results.",
                        evidence="ERROR: invalid input syntax for integer: 'PostgreSQL 15.3'",
                        remediation="Ensure proper query parameterization and disable detailed database error output.",
                        dbms="PostgreSQL",
                    )
                    state.findings.extend([f1, f2])
                    state.log_entries.append("[+] Discovered 2 injection vulnerabilities")

            # Sleep in small increments to allow rapid cancellation response
            elapsed = 0.0
            step = 0.05
            while elapsed < state.stage_duration:
                if state.cancel_requested.is_set():
                    with state.lock:
                        state.status = JobStatus.CANCELLED
                        state.completed_at = _utc_now()
                        state.log_entries.append("[-] Assessment cancelled by operator")
                    return
                time.sleep(step)
                elapsed += step

        with state.lock:
            state.status = JobStatus.COMPLETED
            state.completed_at = _utc_now()
            state.progress = 100.0
