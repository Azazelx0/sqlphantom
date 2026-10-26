"""
Automated testing for SQLPhantom Textual Terminal User Interface.
"""

import pytest
from sqlphantom.tui.app import SQLPhantomApp


@pytest.mark.asyncio
async def test_tui_app_startup_and_navigation():
    """Verify application boots, mounts the default dashboard, and transitions between screens."""
    app = SQLPhantomApp(db_path=":memory:", stage_duration=0.05)
    async with app.run_test() as pilot:
        assert app.is_running
        assert app.query_one("#screen-dashboard") is not None

        # Test navigation to Wizard
        await pilot.press("n")
        assert app.query_one("#screen-wizard") is not None

        # Test navigation to Findings
        await pilot.press("f")
        assert app.query_one("#screen-findings") is not None

        # Test navigation to Help
        await pilot.press("question_mark")
        assert app.query_one("#screen-help") is not None

        # Return to Dashboard
        await pilot.press("d")
        assert app.query_one("#screen-dashboard") is not None


@pytest.mark.asyncio
async def test_tui_quick_scan_workflow():
    """Verify triggering an assessment via TUI executes through stages and renders findings."""
    app = SQLPhantomApp(db_path=":memory:", stage_duration=0.05)
    async with app.run_test() as pilot:
        # Trigger quick scan with key 'r'
        await pilot.press("r")
        assert app.query_one("#screen-monitor") is not None
        assert app.active_job_id is not None

        # Allow mock scan simulation to run through stages
        await pilot.pause(0.6)

        # Inspect findings screen
        await pilot.press("f")
        findings_screen = app.query_one("#screen-findings")
        assert findings_screen is not None

        # Verify findings were discovered and displayed
        findings = app.assessment_service.get_findings(app.active_job_id)
        assert len(findings) >= 2
