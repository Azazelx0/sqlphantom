"""
SQLPhantom engine adapter interface contract.
"""

from abc import ABC, abstractmethod

from sqlphantom.domain.models import AssessmentConfig, Finding, JobResult


class EngineAdapter(ABC):
    """
    Abstract contract defining engine orchestration capabilities.
    All engine backends (e.g. sqlmap REST API, mock engine, worker subprocess)
    must implement this interface.
    """

    @abstractmethod
    def start_scan(self, job_id: str, config: AssessmentConfig) -> None:
        """Initiate an assessment scan for the given job identifier."""
        pass

    @abstractmethod
    def get_status(self, job_id: str) -> JobResult:
        """Query current execution progress and status of a job."""
        pass

    @abstractmethod
    def get_findings(self, job_id: str) -> list[Finding]:
        """Retrieve all vulnerabilities discovered so far for a job."""
        pass

    @abstractmethod
    def cancel_scan(self, job_id: str) -> bool:
        """Request immediate cancellation of a running assessment."""
        pass

    @abstractmethod
    def is_running(self, job_id: str) -> bool:
        """Check if the given job is actively executing."""
        pass
