"""
SQLPhantom core domain models defined using Pydantic v2.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from sqlphantom.domain.enums import (
    AssessmentStage,
    Confidence,
    FindingType,
    HttpMethod,
    JobStatus,
    Severity,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Target(BaseModel):
    """Target endpoint definition for an assessment."""
    model_config = ConfigDict(use_enum_values=True)

    url: str
    method: HttpMethod = HttpMethod.GET
    headers: dict[str, str] = Field(default_factory=dict)
    cookies: dict[str, str] = Field(default_factory=dict)
    data: str | None = None
    notes: str = ""


class ScopeRule(BaseModel):
    """Boundary rules governing assessment targets."""
    model_config = ConfigDict(use_enum_values=True)

    allowed_domains: list[str] = Field(default_factory=list)
    allowed_url_patterns: list[str] = Field(default_factory=list)
    block_private_ips: bool = True


class AssessmentConfig(BaseModel):
    """Configuration options supplied to an assessment run."""
    model_config = ConfigDict(use_enum_values=True)

    target: Target
    scope: ScopeRule
    techniques: list[str] = Field(default_factory=lambda: ["BEUSTQ"])
    level: int = Field(default=1, ge=1, le=5)
    risk: int = Field(default=1, ge=1, le=3)
    threads: int = Field(default=1, ge=1, le=10)
    timeout: int = Field(default=30, ge=1)
    tamper_scripts: list[str] = Field(default_factory=list)
    custom_injection_points: list[str] = Field(default_factory=list)
    dbms: str | None = None
    prefix: str | None = None
    suffix: str | None = None
    extra_options: dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    """Structured assessment finding representing a detected issue."""
    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(default_factory=lambda: uuid4().hex)
    finding_type: FindingType
    severity: Severity = Severity.HIGH
    confidence: Confidence = Confidence.CONFIRMED
    parameter: str
    payload: str
    url: str
    title: str
    description: str = ""
    evidence: str = ""
    remediation: str = ""
    dbms: str | None = None
    discovered_at: datetime = Field(default_factory=_utc_now)


class JobResult(BaseModel):
    """Comprehensive execution summary and findings for a job."""
    model_config = ConfigDict(use_enum_values=True)

    job_id: str
    status: JobStatus = JobStatus.CREATED
    findings: list[Finding] = Field(default_factory=list)
    stage: AssessmentStage = AssessmentStage.INITIALIZATION
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    log_entries: list[str] = Field(default_factory=list)


class Project(BaseModel):
    """Container grouping assessment targets and sessions."""
    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str
    description: str = ""
    targets: list[Target] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)


class Session(BaseModel):
    """Historical or active assessment session within a project."""
    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(default_factory=lambda: uuid4().hex)
    project_id: str
    config: AssessmentConfig
    result: JobResult | None = None
    created_at: datetime = Field(default_factory=_utc_now)
    notes: str = ""
