"""
SQLPhantom data access repositories for Projects, Findings, and Sessions.
"""

from datetime import datetime, timezone
import json

from sqlphantom.domain.enums import Confidence, FindingType, Severity
from sqlphantom.domain.models import (
    AssessmentConfig,
    Finding,
    JobResult,
    Project,
    Session,
    Target,
)
from sqlphantom.storage.database import DatabaseManager


class ProjectRepository:
    """Repository handling persistence of Project aggregates."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def save(self, project: Project) -> None:
        targets_json = json.dumps([t.model_dump(mode="json") for t in project.targets])
        query = """
        INSERT INTO projects (id, name, description, targets_json, created_at, updated_at)
        VALUES (:id, :name, :description, :targets_json, :created_at, :updated_at)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            description=excluded.description,
            targets_json=excluded.targets_json,
            updated_at=excluded.updated_at;
        """
        self.db.execute(
            query,
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "targets_json": targets_json,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
            },
        )

    def get_by_id(self, project_id: str) -> Project | None:
        row = self.db.fetchone("SELECT * FROM projects WHERE id = ?", (project_id,))
        if not row:
            return None
        return self._row_to_project(row)

    def list_all(self) -> list[Project]:
        rows = self.db.fetchall("SELECT * FROM projects ORDER BY updated_at DESC")
        return [self._row_to_project(r) for r in rows]

    def delete(self, project_id: str) -> bool:
        cur = self.db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        return cur.rowcount > 0

    def _row_to_project(self, row) -> Project:
        raw_targets = json.loads(row["targets_json"] or "[]")
        targets = [Target(**t) for t in raw_targets]
        return Project(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            targets=targets,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


class FindingRepository:
    """Repository handling persistence of vulnerability Findings."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def save(self, finding: Finding, job_id: str | None = None) -> None:
        query = """
        INSERT INTO findings (
            id, job_id, finding_type, severity, confidence,
            parameter, payload, url, title, description,
            evidence, remediation, dbms, discovered_at
        ) VALUES (
            :id, :job_id, :finding_type, :severity, :confidence,
            :parameter, :payload, :url, :title, :description,
            :evidence, :remediation, :dbms, :discovered_at
        ) ON CONFLICT(id) DO UPDATE SET
            severity=excluded.severity,
            confidence=excluded.confidence,
            payload=excluded.payload,
            evidence=excluded.evidence,
            remediation=excluded.remediation;
        """
        self.db.execute(
            query,
            {
                "id": finding.id,
                "job_id": job_id,
                "finding_type": str(finding.finding_type),
                "severity": str(finding.severity),
                "confidence": str(finding.confidence),
                "parameter": finding.parameter,
                "payload": finding.payload,
                "url": finding.url,
                "title": finding.title,
                "description": finding.description,
                "evidence": finding.evidence,
                "remediation": finding.remediation,
                "dbms": finding.dbms,
                "discovered_at": finding.discovered_at.isoformat(),
            },
        )

    def get_by_id(self, finding_id: str) -> Finding | None:
        row = self.db.fetchone("SELECT * FROM findings WHERE id = ?", (finding_id,))
        if not row:
            return None
        return self._row_to_finding(row)

    def list_by_job(self, job_id: str) -> list[Finding]:
        rows = self.db.fetchall(
            "SELECT * FROM findings WHERE job_id = ? ORDER BY discovered_at ASC",
            (job_id,),
        )
        return [self._row_to_finding(r) for r in rows]

    def list_all(self) -> list[Finding]:
        rows = self.db.fetchall("SELECT * FROM findings ORDER BY discovered_at DESC")
        return [self._row_to_finding(r) for r in rows]

    def _row_to_finding(self, row) -> Finding:
        return Finding(
            id=row["id"],
            finding_type=FindingType(row["finding_type"]),
            severity=Severity(row["severity"]),
            confidence=Confidence(row["confidence"]),
            parameter=row["parameter"],
            payload=row["payload"],
            url=row["url"],
            title=row["title"],
            description=row["description"],
            evidence=row["evidence"],
            remediation=row["remediation"],
            dbms=row["dbms"],
            discovered_at=datetime.fromisoformat(row["discovered_at"]),
        )


class SessionRepository:
    """Repository handling persistence of assessment Sessions."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def save(self, session: Session) -> None:
        config_json = json.dumps(session.config.model_dump(mode="json"))
        result_json = (
            json.dumps(session.result.model_dump(mode="json"))
            if session.result
            else None
        )
        query = """
        INSERT INTO sessions (id, project_id, config_json, result_json, created_at, notes)
        VALUES (:id, :project_id, :config_json, :result_json, :created_at, :notes)
        ON CONFLICT(id) DO UPDATE SET
            result_json=excluded.result_json,
            notes=excluded.notes;
        """
        self.db.execute(
            query,
            {
                "id": session.id,
                "project_id": session.project_id,
                "config_json": config_json,
                "result_json": result_json,
                "created_at": session.created_at.isoformat(),
                "notes": session.notes,
            },
        )

    def get_by_id(self, session_id: str) -> Session | None:
        row = self.db.fetchone("SELECT * FROM sessions WHERE id = ?", (session_id,))
        if not row:
            return None
        return self._row_to_session(row)

    def list_by_project(self, project_id: str) -> list[Session]:
        rows = self.db.fetchall(
            "SELECT * FROM sessions WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,),
        )
        return [self._row_to_session(r) for r in rows]

    def delete(self, session_id: str) -> bool:
        cur = self.db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        return cur.rowcount > 0

    def _row_to_session(self, row) -> Session:
        config = AssessmentConfig(**json.loads(row["config_json"]))
        result = (
            JobResult(**json.loads(row["result_json"]))
            if row["result_json"]
            else None
        )
        return Session(
            id=row["id"],
            project_id=row["project_id"],
            config=config,
            result=result,
            created_at=datetime.fromisoformat(row["created_at"]),
            notes=row["notes"],
        )
