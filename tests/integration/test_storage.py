"""
Integration tests for SQLPhantom persistence layer (SQLite DatabaseManager and Repositories).
"""

from sqlphantom.domain.enums import Confidence, FindingType, Severity
from sqlphantom.domain.models import (
    AssessmentConfig,
    Finding,
    Project,
    ScopeRule,
    Session,
    Target,
)
from sqlphantom.storage.database import DatabaseManager
from sqlphantom.storage.repositories import (
    FindingRepository,
    ProjectRepository,
    SessionRepository,
)


def test_project_repository_crud(tmp_path):
    db_file = tmp_path / "test_sqlphantom.db"
    db = DatabaseManager(db_file)
    repo = ProjectRepository(db)

    # Create project
    target = Target(url="http://example.com/search")
    project = Project(name="Primary Web Audit", description="Test", targets=[target])
    repo.save(project)

    # Read project
    loaded = repo.get_by_id(project.id)
    assert loaded is not None
    assert loaded.name == "Primary Web Audit"
    assert len(loaded.targets) == 1
    assert loaded.targets[0].url == "http://example.com/search"

    # Update project
    loaded.name = "Renamed Audit"
    repo.save(loaded)
    reloaded = repo.get_by_id(project.id)
    assert reloaded.name == "Renamed Audit"

    # List all
    all_projects = repo.list_all()
    assert len(all_projects) == 1

    # Delete
    deleted = repo.delete(project.id)
    assert deleted is True
    assert repo.get_by_id(project.id) is None


def test_finding_repository(tmp_path):
    db = DatabaseManager(tmp_path / "test_findings.db")
    repo = FindingRepository(db)

    finding = Finding(
        finding_type=FindingType.ERROR_BASED,
        severity=Severity.HIGH,
        confidence=Confidence.CONFIRMED,
        parameter="user_id",
        payload="1' OR 1=1 --",
        url="http://example.com/profile?user_id=1",
        title="SQL Injection in user_id",
        evidence="MySQL Syntax error",
        dbms="MySQL",
    )
    repo.save(finding, job_id="job-999")

    loaded = repo.get_by_id(finding.id)
    assert loaded is not None
    assert loaded.title == "SQL Injection in user_id"
    assert loaded.parameter == "user_id"

    job_findings = repo.list_by_job("job-999")
    assert len(job_findings) == 1
    assert job_findings[0].id == finding.id


def test_session_repository(tmp_path):
    db = DatabaseManager(tmp_path / "test_sessions.db")
    proj_repo = ProjectRepository(db)
    sess_repo = SessionRepository(db)

    project = Project(name="Project with Session")
    proj_repo.save(project)

    target = Target(url="http://example.com/app")
    scope = ScopeRule(allowed_domains=["example.com"])
    config = AssessmentConfig(target=target, scope=scope)
    session = Session(project_id=project.id, config=config, notes="Baseline test")

    sess_repo.save(session)

    loaded = sess_repo.get_by_id(session.id)
    assert loaded is not None
    assert loaded.project_id == project.id
    assert loaded.notes == "Baseline test"
    assert loaded.config.target.url == "http://example.com/app"
