"""
Automated unit and integration testing for SQLPhantom PySide6 Desktop GUI.
Runs headlessly using pytest-qt and offscreen platform.
"""

import os
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from sqlphantom.gui.main_window import MainWindow

# Ensure Qt uses offscreen platform in headless CI/test environments
os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture
def app_window(qtbot):
    """Fixture providing an initialized MainWindow instance."""
    app = QApplication.instance() or QApplication([])
    window = MainWindow(db_path=":memory:", stage_duration=0.05)
    qtbot.addWidget(window)
    window.show()
    return window


def test_main_window_initialization(app_window):
    """Verify window title, initial screen, and sidebar setup."""
    assert app_window.windowTitle() == "SQLPhantom — sqlmap Enhanced"
    assert "dashboard" in app_window.screens
    assert app_window.stack.currentWidget() == app_window.screens["dashboard"]


def test_sidebar_navigation(app_window):
    """Verify navigating through each sidebar item switches the active screen."""
    # Navigate to Wizard
    app_window.navigate_to("wizard")
    assert app_window.stack.currentWidget() == app_window.screens["wizard"]

    # Navigate to Request Editor
    app_window.navigate_to("request")
    assert app_window.stack.currentWidget() == app_window.screens["request"]

    # Navigate to Live Monitor
    app_window.navigate_to("monitor")
    assert app_window.stack.currentWidget() == app_window.screens["monitor"]

    # Navigate to Findings
    app_window.navigate_to("findings")
    assert app_window.stack.currentWidget() == app_window.screens["findings"]

    # Return to Dashboard
    app_window.navigate_to("dashboard")
    assert app_window.stack.currentWidget() == app_window.screens["dashboard"]


def test_quick_scan_execution(app_window, qtbot):
    """Verify launching a test assessment switches to monitor and observes progress."""
    app_window.launch_quick_scan()
    assert app_window.active_job_id is not None
    assert app_window.stack.currentWidget() == app_window.screens["monitor"]

    monitor_screen = app_window.screens["monitor"]

    # Wait for simulation to run through stages and finish
    qtbot.wait(600)

    status = app_window.assessment_service.get_status(app_window.active_job_id)
    assert status.progress >= 50.0

    # Switch to findings screen and verify findings were populated
    app_window.navigate_to("findings")
    findings_screen = app_window.screens["findings"]
    assert findings_screen.table.rowCount() >= 2


def test_request_editor_parsing(app_window):
    """Verify the raw HTTP request editor parses headers, method, and URL properly."""
    editor_screen = app_window.screens["request"]
    target = editor_screen.parse_request()
    assert target is not None
    assert str(target.method) == "POST"
    assert "testphp.vulnweb.com" in target.url
    assert "Content-Type" in target.headers
