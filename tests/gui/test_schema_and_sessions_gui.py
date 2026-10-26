"""
Headless automated tests for SchemaViewerScreen and SessionsScreen.
"""

import pytest
from PySide6.QtCore import Qt
from sqlphantom.domain.enums import FindingType, Severity, Confidence, JobStatus
from sqlphantom.domain.models import AssessmentConfig, Finding, JobResult, ScopeRule, Session, Target
from sqlphantom.domain.schema import ColumnSchema, DatabaseSchema, TableDump, TableSchema
from sqlphantom.gui.main_window import MainWindow
from sqlphantom.gui.screens.schema_viewer import SchemaViewerScreen
from sqlphantom.gui.screens.sessions_view import SessionsScreen


def test_schema_viewer_screen(qtbot, tmp_path):
    window = MainWindow(db_path=":memory:")
    qtbot.addWidget(window)

    window.navigate_to("schema")
    assert isinstance(window.stack.currentWidget(), SchemaViewerScreen)

    screen: SchemaViewerScreen = window.stack.currentWidget()
    assert screen.tree.topLevelItemCount() >= 1

    # Test custom schema setting
    col = ColumnSchema(name="token", data_type="VARCHAR(256)")
    tbl = TableSchema(name="auth_tokens", database="custom_db", columns=[col], estimated_row_count=10)
    db = DatabaseSchema(name="custom_db", dbms="MySQL", tables=[tbl])
    screen.set_schemas([db])

    assert screen.tree.topLevelItemCount() == 1
    assert "custom_db" in screen.tree.topLevelItem(0).text(0)

    # Test table dump rendering and CSV export
    dump = TableDump(
        database="custom_db",
        table="auth_tokens",
        columns=["id", "token"],
        rows=[[1, "xyz123"], [2, "abc456"]],
        total_rows=2,
    )
    screen.set_table_dump(dump)
    assert screen.table_grid.rowCount() == 2
    assert screen.table_grid.columnCount() == 2

    # Click export CSV
    screen._export_csv()
    assert "Exported CSV dump" in screen.lbl_status.text()


def test_sessions_screen_and_comparison(qtbot, tmp_path):
    window = MainWindow(db_path=":memory:")
    qtbot.addWidget(window)

    # Seed 2 sessions in session_repo
    target = Target(url="http://test.local/index.php?id=1")
    scope = ScopeRule(allowed_domains=["test.local"])
    config = AssessmentConfig(target=target, scope=scope)

    f1 = Finding(
        finding_type=FindingType.BOOLEAN_BASED_BLIND,
        severity=Severity.HIGH,
        confidence=Confidence.CONFIRMED,
        parameter="id",
        payload="1' AND 1=1",
        url="http://test.local/index.php",
        title="Boolean injection",
    )
    f2 = Finding(
        finding_type=FindingType.ERROR_BASED,
        severity=Severity.CRITICAL,
        confidence=Confidence.CONFIRMED,
        parameter="id",
        payload="1' AND 1=0",
        url="http://test.local/index.php",
        title="Error injection",
    )

    res1 = JobResult(job_id="job-1", status=JobStatus.COMPLETED, findings=[f1])
    res2 = JobResult(job_id="job-2", status=JobStatus.COMPLETED, findings=[f1, f2])
    # Use existing project from workspace seed
    projects = window.project_service.list_projects()
    project_id = projects[0].id if projects else "p1"

    s1 = Session(project_id=project_id, config=config, result=res1)
    s2 = Session(project_id=project_id, config=config, result=res2)

    window.session_repo.save(s1)
    window.session_repo.save(s2)

    window.navigate_to("sessions")
    assert isinstance(window.stack.currentWidget(), SessionsScreen)

    screen: SessionsScreen = window.stack.currentWidget()
    screen.refresh_sessions()
    assert screen.table.rowCount() == 2

    # Select both sessions and click compare
    screen.table.selectAll()
    screen._compare_sessions()
    assert "Vulnerability Drift Comparison" in screen.txt_diff.toPlainText()
    assert "New Findings" in screen.txt_diff.toPlainText()
