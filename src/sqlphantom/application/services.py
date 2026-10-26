"""
SQLPhantom unified application services facade used by both GUI and TUI interfaces.
"""

from datetime import datetime, timezone
import json
from uuid import uuid4

from sqlphantom.application.job_manager import JobManager
from sqlphantom.domain.enums import ReportFormat
from sqlphantom.domain.models import (
    AssessmentConfig,
    Finding,
    JobResult,
    Project,
    Target,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProjectService:
    """
    Manages project containers and their associated targets.
    Supports in-memory tracking with optional repository delegation.
    """

    def __init__(self, repository=None):
        self.repository = repository
        self._in_memory: dict[str, Project] = {}

    def create_project(self, name: str, description: str = "") -> Project:
        project = Project(
            id=uuid4().hex,
            name=name,
            description=description,
            targets=[],
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )
        if self.repository:
            self.repository.save(project)
        else:
            self._in_memory[project.id] = project
        return project

    def get_project(self, project_id: str) -> Project | None:
        if self.repository:
            return self.repository.get_by_id(project_id)
        return self._in_memory.get(project_id)

    def list_projects(self) -> list[Project]:
        if self.repository:
            return self.repository.list_all()
        return list(self._in_memory.values())

    def delete_project(self, project_id: str) -> bool:
        if self.repository:
            return self.repository.delete(project_id)
        if project_id in self._in_memory:
            del self._in_memory[project_id]
            return True
        return False

    def add_target(self, project_id: str, target: Target) -> Project:
        project = self.get_project(project_id)
        if not project:
            raise KeyError(f"Project '{project_id}' not found")

        project.targets.append(target)
        project.updated_at = _utc_now()

        if self.repository:
            self.repository.save(project)
        else:
            self._in_memory[project.id] = project
        return project


class AssessmentService:
    """
    Manages assessment jobs, starting, monitoring, and cancelling runs
    through the central JobManager.
    """

    def __init__(self, job_manager: JobManager):
        self.job_manager = job_manager

    def create_assessment(self, config: AssessmentConfig) -> str:
        """Create and queue a new assessment job."""
        return self.job_manager.create_job(config)

    def start_assessment(self, job_id: str) -> None:
        """Begin execution of a created assessment job."""
        self.job_manager.start_job(job_id)

    def cancel_assessment(self, job_id: str) -> bool:
        """Cancel an actively executing assessment job."""
        return self.job_manager.cancel_job(job_id)

    def get_status(self, job_id: str) -> JobResult:
        """Retrieve current execution status and progress."""
        return self.job_manager.get_status(job_id)

    def get_findings(self, job_id: str) -> list[Finding]:
        """Retrieve all vulnerabilities detected for the given job."""
        return self.job_manager.get_status(job_id).findings


class ReportService:
    """
    Generates assessment reports in multiple export formats.
    """

    def generate_report(
        self,
        findings: list[Finding],
        title: str = "SQLPhantom Assessment Report",
        fmt: ReportFormat = ReportFormat.MARKDOWN,
    ) -> str:
        """Format findings into a structured report string."""
        if fmt == ReportFormat.JSON:
            return json.dumps(
                {
                    "title": title,
                    "generated_at": _utc_now().isoformat(),
                    "findings_count": len(findings),
                    "findings": [f.model_dump(mode="json") for f in findings],
                },
                indent=2,
            )

        elif fmt == ReportFormat.MARKDOWN:
            lines = [
                f"# {title}",
                f"**Generated:** {_utc_now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                f"**Total Findings:** {len(findings)}",
                "",
                "---",
                "",
            ]
            if not findings:
                lines.append("No security vulnerabilities were identified.")
            else:
                for idx, finding in enumerate(findings, 1):
                    lines.extend(
                        [
                            f"## {idx}. {finding.title}",
                            f"- **Type:** `{finding.finding_type}`",
                            f"- **Severity:** **{finding.severity}**",
                            f"- **Confidence:** {finding.confidence}",
                            f"- **Target URL:** `{finding.url}`",
                            f"- **Vulnerable Parameter:** `{finding.parameter}`",
                            "",
                            "### Description",
                            finding.description,
                            "",
                            "### Technical Evidence",
                            f"```text\n{finding.evidence}\n```",
                            "",
                            "### Remediation Guidance",
                            finding.remediation or "Ensure rigorous parameterization.",
                            "",
                            "---",
                            "",
                        ]
                    )
            return "\n".join(lines)

        elif fmt == ReportFormat.HTML:
            html_rows = ""
            for finding in findings:
                html_rows += f"""
                <div class="finding-card">
                    <h3>{finding.title}</h3>
                    <p><strong>Type:</strong> {finding.finding_type} | <strong>Severity:</strong> {finding.severity}</p>
                    <p><strong>URL:</strong> <code>{finding.url}</code> (Param: <code>{finding.parameter}</code>)</p>
                    <pre><code>{finding.evidence}</code></pre>
                    <p><strong>Remediation:</strong> {finding.remediation}</p>
                </div>
                """
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; }}
        h1 {{ color: #a855f7; }}
        .finding-card {{ background: #1e293b; border-left: 4px solid #a855f7; padding: 1rem; margin-bottom: 1rem; border-radius: 4px; }}
        pre {{ background: #0f172a; padding: 0.75rem; border-radius: 4px; overflow-x: auto; }}
        code {{ color: #38bdf8; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>Generated: {_utc_now().isoformat()} | Findings: {len(findings)}</p>
    {html_rows if findings else "<p>No vulnerabilities identified.</p>"}
</body>
</html>"""

        raise ValueError(f"Unsupported report format: {fmt}")
