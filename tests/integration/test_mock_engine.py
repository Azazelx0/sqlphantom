"""
End-to-end integration test of the Phase 1 Foundation milestone:
Target -> Scope Enforcement -> JobManager -> MockEngineAdapter -> EventBus -> Findings.
"""

import time

from sqlphantom.application.event_bus import EventBus
from sqlphantom.application.job_manager import JobManager
from sqlphantom.application.services import AssessmentService, ProjectService, ReportService
from sqlphantom.domain.enums import FindingType, JobStatus, ReportFormat
from sqlphantom.domain.events import (
    FindingDiscovered,
    JobCompleted,
    JobCreated,
    JobStarted,
    ProgressUpdated,
    StageChanged,
)
from sqlphantom.domain.models import AssessmentConfig, ScopeRule, Target
from sqlphantom.engine.mock_adapter import MockEngineAdapter
from sqlphantom.storage.database import DatabaseManager
from sqlphantom.storage.repositories import FindingRepository, ProjectRepository


def test_complete_assessment_workflow(tmp_path):
    # Set up database and repositories
    db = DatabaseManager(tmp_path / "integration_audit.db")
    proj_repo = ProjectRepository(db)
    finding_repo = FindingRepository(db)

    # Set up services
    proj_service = ProjectService(repository=proj_repo)
    project = proj_service.create_project("E2E Integration Test Project")

    # Set up target and scope
    target = Target(url="http://testphp.vulnweb.com/listproducts.php?cat=1")
    scope = ScopeRule(allowed_domains=["vulnweb.com"], block_private_ips=True)
    proj_service.add_target(project.id, target)

    # Set up fast mock engine (0.05s per stage = ~0.3s total)
    event_bus = EventBus(async_dispatch=False)
    engine = MockEngineAdapter(stage_duration=0.05)
    job_manager = JobManager(event_bus=event_bus, engine=engine, poll_interval=0.01)
    assessment_service = AssessmentService(job_manager=job_manager)

    # Capture all dispatched events
    captured_events = []
    event_bus.subscribe_all(lambda ev: captured_events.append(ev))

    # Create assessment
    config = AssessmentConfig(target=target, scope=scope, level=2, risk=1)
    job_id = assessment_service.create_assessment(config)
    assert job_id is not None

    # Start assessment
    assessment_service.start_assessment(job_id)

    # Wait for completion and event dispatch (simulation completes in ~0.3-0.4s)
    max_wait = 3.0
    start_wait = time.time()
    while time.time() - start_wait < max_wait:
        if any(isinstance(e, JobCompleted) for e in captured_events):
            break
        time.sleep(0.02)

    final_status = assessment_service.get_status(job_id)
    assert final_status.status == JobStatus.COMPLETED
    assert final_status.progress == 100.0

    # Verify findings were discovered
    findings = assessment_service.get_findings(job_id)
    assert len(findings) >= 2

    # Persist findings to repository
    for f in findings:
        finding_repo.save(f, job_id=job_id)

    stored_findings = finding_repo.list_by_job(job_id)
    assert len(stored_findings) == len(findings)

    # Verify event stream
    event_types = [type(e) for e in captured_events]
    assert JobCreated in event_types
    assert JobStarted in event_types
    assert StageChanged in event_types
    assert ProgressUpdated in event_types
    assert FindingDiscovered in event_types
    assert JobCompleted in event_types

    # Generate reports
    report_service = ReportService()
    md_report = report_service.generate_report(findings, fmt=ReportFormat.MARKDOWN)
    assert "SQLPhantom Assessment Report" in md_report
    assert "Boolean-based blind" in md_report

    json_report = report_service.generate_report(findings, fmt=ReportFormat.JSON)
    assert '"findings_count": 2' in json_report
