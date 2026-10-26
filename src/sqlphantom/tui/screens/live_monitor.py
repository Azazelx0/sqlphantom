"""
SQLPhantom TUI Live Assessment Monitoring screen.
"""

from typing import Any
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Label, ProgressBar, Static

from sqlphantom.domain.enums import JobStatus
from sqlphantom.domain.events import (
    FindingDiscovered,
    JobCancelled,
    JobCompleted,
    JobFailed,
    ProgressUpdated,
    StageChanged,
)
from sqlphantom.tui.widgets.kpi_card import KPICard
from sqlphantom.tui.widgets.log_stream import LogStream


class LiveMonitorScreen(Static):
    """
    Real-time assessment observation station showing telemetry,
    live execution stages, terminal event logs, and cancel controls.
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            # Target and status header
            with Horizontal(classes="card-box"):
                yield Label("Target: None", id="mon-target-label", classes="kpi-title")
                yield Label("Status: IDLE", id="mon-status-badge", classes="kpi-title")

            # Progress Stepper
            yield Label("Execution Progress:")
            yield ProgressBar(total=100, show_eta=False, id="mon-progress-bar")

            # Telemetry Metrics
            with Horizontal(classes="kpi-container"):
                yield KPICard("Stage", "INITIALIZATION", id="kpi-mon-stage")
                yield KPICard("Progress", "0.0%", id="kpi-mon-progress")
                yield KPICard("Discovered", "0", "Vulnerabilities", id="kpi-mon-findings")
                yield KPICard("DBMS", "Scanning...", id="kpi-mon-dbms")

            # Real-time Terminal Log Stream
            yield Label("Live Heuristic & Payload Event Stream:", classes="card-title")
            yield LogStream(id="mon-log-stream")

            # Controls
            with Horizontal(classes="card-box"):
                yield Button("Cancel Assessment", id="btn-cancel-scan", classes="btn-danger")
                yield Button("View Confirmed Findings", id="btn-view-findings", classes="btn-secondary")

    def on_mount(self) -> None:
        self.subscribe_to_events()
        self.refresh_state()

    def subscribe_to_events(self) -> None:
        if not hasattr(self.app, "event_bus") or not self.app.event_bus:
            return

        bus = self.app.event_bus
        bus.subscribe(StageChanged, self._on_stage_changed)
        bus.subscribe(ProgressUpdated, self._on_progress_updated)
        bus.subscribe(FindingDiscovered, self._on_finding_discovered)
        bus.subscribe(JobCompleted, self._on_job_completed)
        bus.subscribe(JobCancelled, self._on_job_cancelled)
        bus.subscribe(JobFailed, self._on_job_failed)

    def refresh_state(self) -> None:
        job_id = getattr(self.app, "active_job_id", None)
        log = self.query_one("#mon-log-stream", LogStream)

        if not job_id:
            self.query_one("#mon-target-label", Label).update("Target: No active assessment")
            self.query_one("#mon-status-badge", Label).update("Status: IDLE")
            log.log_info("Workstation ready. Launch an assessment to observe live payloads.")
            return

        app: Any = self.app
        status = app.assessment_service.get_status(job_id)
        context = app.job_manager.get_context(job_id)
        target_url = context.config.target.url if context else "Unknown Target"

        self.query_one("#mon-target-label", Label).update(f"Target: {target_url}")
        self.query_one("#mon-status-badge", Label).update(f"Status: {status.status}")
        self.query_one("#kpi-mon-stage", KPICard).update_value(str(status.stage))
        self.query_one("#kpi-mon-progress", KPICard).update_value(f"{status.progress:.0f}%")
        self.query_one("#mon-progress-bar", ProgressBar).progress = status.progress
        self.query_one("#kpi-mon-findings", KPICard).update_value(str(len(status.findings)))

        log.log_info(f"Connected to job {job_id[:8]} monitoring stream.")

    def _on_stage_changed(self, event: StageChanged) -> None:
        self.app.call_from_thread(self._handle_stage_changed, event)

    def _handle_stage_changed(self, event: StageChanged) -> None:
        self.query_one("#kpi-mon-stage", KPICard).update_value(event.stage)
        log = self.query_one("#mon-log-stream", LogStream)
        log.log_stage(event.stage, event.previous_stage)

    def _on_progress_updated(self, event: ProgressUpdated) -> None:
        self.app.call_from_thread(self._handle_progress_updated, event)

    def _handle_progress_updated(self, event: ProgressUpdated) -> None:
        self.query_one("#kpi-mon-progress", KPICard).update_value(f"{event.progress:.0f}%")
        self.query_one("#mon-progress-bar", ProgressBar).progress = event.progress
        if event.message:
            log = self.query_one("#mon-log-stream", LogStream)
            log.log_payload(event.message)

    def _on_finding_discovered(self, event: FindingDiscovered) -> None:
        self.app.call_from_thread(self._handle_finding_discovered, event)

    def _handle_finding_discovered(self, event: FindingDiscovered) -> None:
        log = self.query_one("#mon-log-stream", LogStream)
        log.log_vuln(event.title, event.parameter)

        # Update findings count
        app: Any = self.app
        job_id = getattr(app, "active_job_id", None)
        if job_id:
            count = len(app.assessment_service.get_findings(job_id))
            self.query_one("#kpi-mon-findings", KPICard).update_value(str(count))
            self.query_one("#kpi-mon-dbms", KPICard).update_value("PostgreSQL")

    def _on_job_completed(self, event: JobCompleted) -> None:
        self.app.call_from_thread(self._handle_job_completed, event)

    def _handle_job_completed(self, event: JobCompleted) -> None:
        self.query_one("#mon-status-badge", Label).update("Status: COMPLETED")
        self.query_one("#mon-progress-bar", ProgressBar).progress = 100.0
        log = self.query_one("#mon-log-stream", LogStream)
        log.log_completed(event.findings_count, event.duration_seconds)

    def _on_job_cancelled(self, event: JobCancelled) -> None:
        self.app.call_from_thread(self._handle_job_cancelled, event)

    def _handle_job_cancelled(self, event: JobCancelled) -> None:
        self.query_one("#mon-status-badge", Label).update("Status: CANCELLED")
        log = self.query_one("#mon-log-stream", LogStream)
        log.log_cancel(event.reason)

    def _on_job_failed(self, event: JobFailed) -> None:
        self.app.call_from_thread(self._handle_job_failed, event)

    def _handle_job_failed(self, event: JobFailed) -> None:
        self.query_one("#mon-status-badge", Label).update("Status: FAILED")
        log = self.query_one("#mon-log-stream", LogStream)
        log.log_info(f"[red]Job execution failed: {event.error}[/red]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        app: Any = self.app
        if event.button.id == "btn-cancel-scan":
            job_id = getattr(app, "active_job_id", None)
            if job_id:
                app.assessment_service.cancel_assessment(job_id)
        elif event.button.id == "btn-view-findings":
            app.switch_screen("findings")
