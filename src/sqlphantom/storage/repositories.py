"""
SQLPhantom data access repositories for Projects, Findings, and Sessions.
"""

from datetime import datetime, timezone
import json
import sqlite3

from sqlphantom.domain.enums import Confidence, FindingStatus, FindingType, Severity
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

    def _row_to_project(self, row: sqlite3.Row) -> Project:
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
            id, job_id, finding_type, severity, confidence, status,
            parameter, payload, url, title, description,
            evidence, remediation, analyst_notes, dbms, discovered_at
        ) VALUES (
            :id, :job_id, :finding_type, :severity, :confidence, :status,
            :parameter, :payload, :url, :title, :description,
            :evidence, :remediation, :analyst_notes, :dbms, :discovered_at
        ) ON CONFLICT(id) DO UPDATE SET
            severity=excluded.severity,
            confidence=excluded.confidence,
            status=excluded.status,
            payload=excluded.payload,
            evidence=excluded.evidence,
            remediation=excluded.remediation,
            analyst_notes=excluded.analyst_notes;
        """
        status_val = finding.status.value if hasattr(finding.status, "value") else str(finding.status)
        sev_val = finding.severity.value if hasattr(finding.severity, "value") else str(finding.severity)
        conf_val = finding.confidence.value if hasattr(finding.confidence, "value") else str(finding.confidence)
        type_val = finding.finding_type.value if hasattr(finding.finding_type, "value") else str(finding.finding_type)

        self.db.execute(
            query,
            {
                "id": finding.id,
                "job_id": job_id,
                "finding_type": type_val,
                "severity": sev_val,
                "confidence": conf_val,
                "status": status_val,
                "parameter": finding.parameter,
                "payload": finding.payload,
                "url": finding.url,
                "title": finding.title,
                "description": finding.description,
                "evidence": finding.evidence,
                "remediation": finding.remediation,
                "analyst_notes": finding.analyst_notes,
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

    def _row_to_finding(self, row: sqlite3.Row) -> Finding:
        raw_status = row["status"] if "status" in row.keys() and row["status"] else "ACTIVE"
        clean_status = str(raw_status).replace("FindingStatus.", "").upper()
        try:
            status_enum = FindingStatus(clean_status)
        except ValueError:
            status_enum = FindingStatus.ACTIVE

        raw_sev = str(row["severity"]).replace("Severity.", "").upper()
        raw_conf = str(row["confidence"]).replace("Confidence.", "").upper()
        raw_type = str(row["finding_type"]).replace("FindingType.", "").upper()

        analyst_notes_val = row["analyst_notes"] if "analyst_notes" in row.keys() and row["analyst_notes"] else ""
        return Finding(
            id=row["id"],
            finding_type=FindingType(raw_type) if raw_type in FindingType.__members__ else FindingType.SQL_INJECTION,
            severity=Severity(raw_sev) if raw_sev in Severity.__members__ else Severity.HIGH,
            confidence=Confidence(raw_conf) if raw_conf in Confidence.__members__ else Confidence.CONFIRMED,
            status=status_enum,
            parameter=row["parameter"],
            payload=row["payload"],
            url=row["url"],
            title=row["title"],
            description=row["description"],
            evidence=row["evidence"],
            remediation=row["remediation"],
            analyst_notes=analyst_notes_val,
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

    def list_all(self) -> list[Session]:
        rows = self.db.fetchall("SELECT * FROM sessions ORDER BY created_at DESC")
        return [self._row_to_session(r) for r in rows]

    def delete(self, session_id: str) -> bool:
        cur = self.db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        return cur.rowcount > 0

    def _row_to_session(self, row: sqlite3.Row) -> Session:
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
