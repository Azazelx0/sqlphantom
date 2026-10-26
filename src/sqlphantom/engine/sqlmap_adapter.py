"""
SQLPhantom real sqlmap engine adapter orchestrating scans via sqlmapapi.
"""

from datetime import datetime, timezone
import logging
import threading
from typing import Any
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
from sqlphantom.engine.client import SqlmapApiClient
from sqlphantom.engine.process import SqlmapProcessSupervisor

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SqlmapEngineAdapter(EngineAdapter):
    """
    Production EngineAdapter implementation integrating directly with the
    upstream sqlmap REST API daemon.
    """

    def __init__(
        self,
        supervisor: SqlmapProcessSupervisor | None = None,
        client: SqlmapApiClient | None = None,
    ):
        self.supervisor = supervisor
        self.client = client
        self._job_to_task: dict[str, str] = {}
        self._job_results: dict[str, JobResult] = {}
        self._lock = threading.RLock()

    def _ensure_connected(self) -> None:
        if self.supervisor and not self.supervisor.is_port_listening():
            self.supervisor.start()
        if not self.client:
            base_url = self.supervisor.base_url if self.supervisor else "http://127.0.0.1:8775"
            self.client = SqlmapApiClient(base_url=base_url)

    def start_scan(self, job_id: str, config: AssessmentConfig) -> None:
        self._ensure_connected()
        assert self.client is not None

        task_id = self.client.new_task()
        with self._lock:
            self._job_to_task[job_id] = task_id
            self._job_results[job_id] = JobResult(
                job_id=job_id,
                status=JobStatus.RUNNING,
                stage=AssessmentStage.INITIALIZATION,
                started_at=_utc_now(),
            )

        options = self._translate_config(config)
        success = self.client.start_scan(task_id, options)
        if not success:
            with self._lock:
                self._job_results[job_id].status = JobStatus.FAILED
                self._job_results[job_id].error_message = "sqlmapapi failed to start scan task"
            raise RuntimeError(f"sqlmapapi failed to start scan for task {task_id}")

    def get_status(self, job_id: str) -> JobResult:
        with self._lock:
            cached = self._job_results.get(job_id)
            task_id = self._job_to_task.get(job_id)

        if not cached or not task_id:
            return JobResult(job_id=job_id, status=JobStatus.FAILED, error_message="Unknown job")

        if not self.client:
            return cached

        try:
            status_data = self.client.get_status(task_id)
            api_status = status_data.get("status")

            # Collect log entries
            logs = self.client.get_log(task_id)
            log_messages = [e.get("message", "") for e in logs if "message" in e]

            # Ingest findings
            findings_data = self.client.get_data(task_id)
            parsed_findings = self._parse_findings(findings_data, cached.job_id)

            with self._lock:
                cached.log_entries = log_messages
                cached.findings = parsed_findings

                if api_status == "running":
                    cached.status = JobStatus.RUNNING
                    cached.stage = AssessmentStage.DETECTION
                    cached.progress = 60.0
                elif api_status == "terminated":
                    cached.status = JobStatus.COMPLETED
                    cached.stage = AssessmentStage.FINISHED
                    cached.progress = 100.0
                    cached.completed_at = _utc_now()
                elif api_status == "not running":
                    if cached.status == JobStatus.RUNNING:
                        cached.status = JobStatus.COMPLETED
                        cached.stage = AssessmentStage.FINISHED
                        cached.progress = 100.0
                        cached.completed_at = _utc_now()

            return cached
        except Exception as exc:
            logger.error("Error polling sqlmap status for job %s: %s", job_id, exc)
            return cached

    def get_findings(self, job_id: str) -> list[Finding]:
        return self.get_status(job_id).findings

    def cancel_scan(self, job_id: str) -> bool:
        with self._lock:
            task_id = self._job_to_task.get(job_id)
            cached = self._job_results.get(job_id)

        if not task_id or not self.client:
            return False

        stopped = self.client.stop_scan(task_id)
        if not stopped:
            self.client.kill_scan(task_id)

        with self._lock:
            if cached:
                cached.status = JobStatus.CANCELLED
                cached.completed_at = _utc_now()
        return True

    def is_running(self, job_id: str) -> bool:
        return self.get_status(job_id).status in (JobStatus.RUNNING, JobStatus.CANCELLING)

    def _translate_config(self, config: AssessmentConfig) -> dict[str, Any]:
        """Convert domain AssessmentConfig into sqlmap option dictionary."""
        opts: dict[str, Any] = {
            "url": config.target.url,
            "method": str(config.target.method),
            "level": config.level,
            "risk": config.risk,
            "threads": config.threads,
            "timeout": config.timeout,
        }

        if config.target.data:
            opts["data"] = config.target.data

        if config.target.cookies:
            opts["cookie"] = "; ".join(f"{k}={v}" for k, v in config.target.cookies.items())

        if config.target.headers:
            opts["headers"] = "\n".join(f"{k}: {v}" for k, v in config.target.headers.items())

        if config.dbms:
            opts["dbms"] = config.dbms

        if config.tamper_scripts:
            opts["tamper"] = ",".join(config.tamper_scripts)

        if config.techniques:
            opts["tech"] = "".join(config.techniques)

        if config.proxy:
            opts["proxy"] = config.proxy

        if config.delay > 0:
            opts["delay"] = config.delay

        opts.update(config.extra_options)
        return opts

    def _parse_findings(self, data_entries: list[dict[str, Any]], job_id: str) -> list[Finding]:
        findings: list[Finding] = []
        for entry in data_entries:
            # sqlmap data entry structure inspection
            status_code = entry.get("status")
            entry_type = entry.get("type")
            value = entry.get("value", {})

            if isinstance(value, dict) and "data" in value:
                for param, tech_dict in value.get("data", {}).items():
                    if isinstance(tech_dict, dict):
                        f = Finding(
                            id=uuid4().hex,
                            finding_type=FindingType.SQL_INJECTION,
                            severity=Severity.HIGH,
                            confidence=Confidence.CONFIRMED,
                            parameter=str(param),
                            payload=str(tech_dict.get("title", "")),
                            url="",
                            title=f"SQL Injection in parameter '{param}'",
                            description=str(tech_dict.get("title", "")),
                        )
                        findings.append(f)
        return findings
