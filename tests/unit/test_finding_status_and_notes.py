"""
Unit tests for FindingStatus, analyst notes, and SQLite persistence.
"""

from sqlphantom.domain.enums import FindingStatus, FindingType, Severity, Confidence
from sqlphantom.domain.models import Finding
from sqlphantom.storage.database import DatabaseManager
from sqlphantom.storage.repositories import FindingRepository


def test_finding_status_and_notes_persistence(tmp_path):
    db_file = tmp_path / "test_notes.db"
    db = DatabaseManager(db_file)
    repo = FindingRepository(db)

    finding = Finding(
        finding_type=FindingType.ERROR_BASED,
        severity=Severity.HIGH,
        confidence=Confidence.CONFIRMED,
        status=FindingStatus.ACTIVE,
        parameter="user_id",
        payload="1' OR 1=1 --",
        url="https://target.local/vuln.php",
        title="Error-based SQL Injection",
        analyst_notes="Initial discovery by automated triage.",
    )

    repo.save(finding, job_id="job-101")

    # Fetch back
    fetched = repo.get_by_id(finding.id)
    assert fetched is not None
    assert fetched.status == FindingStatus.ACTIVE
    assert fetched.analyst_notes == "Initial discovery by automated triage."

    # Update status to FALSE_POSITIVE with updated notes
    finding.status = FindingStatus.FALSE_POSITIVE
    finding.analyst_notes = "Verified as honeypot / benign reflection. Marking false positive."
    repo.save(finding, job_id="job-101")

    refetched = repo.get_by_id(finding.id)
    assert refetched is not None
    assert refetched.status == FindingStatus.FALSE_POSITIVE
    assert "honeypot" in refetched.analyst_notes
