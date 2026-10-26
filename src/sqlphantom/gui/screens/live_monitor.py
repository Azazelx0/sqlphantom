"""
SQLPhantom PySide6 Live Assessment Monitoring screen.
"""

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sqlphantom.gui.widgets.kpi_card import KPICard
from sqlphantom.gui.widgets.terminal_widget import TerminalWidget


class LiveMonitorScreen(QWidget):
    """
    Real-time assessment observation station showing telemetry,
    live execution stages, terminal event logs, and cancel controls.
    """

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header Info Card
        header_card = QFrame()
        header_card.setProperty("class", "card-frame")
        h_layout = QHBoxLayout(header_card)
        self.lbl_target = QLabel("Target: No active assessment")
        self.lbl_target.setStyleSheet("font-size: 14px; font-weight: bold; color: #F8FAFC;")
        self.lbl_status = QLabel("Status: IDLE")
        self.lbl_status.setStyleSheet("font-size: 13px; font-weight: bold; color: #A855F7;")
        h_layout.addWidget(self.lbl_target)
        h_layout.addStretch()
        h_layout.addWidget(self.lbl_status)
        layout.addWidget(header_card)

        # Stepper Progress Bar
        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(0)
        layout.addWidget(self.prog_bar)

        # KPI Telemetry Strip
        kpi_row = QHBoxLayout()
        self.kpi_stage = KPICard("Stage", "INITIALIZATION")
        self.kpi_progress = KPICard("Progress", "0.0%")
        self.kpi_findings = KPICard("Discovered", "0", "Vulnerabilities")
        self.kpi_dbms = KPICard("Target DBMS", "Scanning...")
        kpi_row.addWidget(self.kpi_stage)
        kpi_row.addWidget(self.kpi_progress)
        kpi_row.addWidget(self.kpi_findings)
        kpi_row.addWidget(self.kpi_dbms)
        layout.addLayout(kpi_row)

        # Terminal Console Log Stream
        layout.addWidget(QLabel("Live Payload & Heuristic Event Stream:"))
        self.terminal = TerminalWidget()
        layout.addWidget(self.terminal)

        # Control Buttons
        btn_bar = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel Assessment")
        self.btn_cancel.setProperty("class", "danger")
        self.btn_view_findings = QPushButton("View Confirmed Findings")
        self.btn_view_findings.setProperty("class", "secondary")

        self.btn_cancel.clicked.connect(self.cancel_current_scan)
        self.btn_view_findings.clicked.connect(lambda: self.main_window.navigate_to("findings"))

        btn_bar.addWidget(self.btn_cancel)
        btn_bar.addWidget(self.btn_view_findings)
        btn_bar.addStretch()
        layout.addLayout(btn_bar)

        self._connect_signals()

    def _connect_signals(self) -> None:
        bridge = self.main_window.signal_bridge
        if bridge:
            bridge.stage_changed.connect(self._on_stage_changed)
            bridge.progress_updated.connect(self._on_progress_updated)
            bridge.finding_discovered.connect(self._on_finding_discovered)
            bridge.job_completed.connect(self._on_job_completed)
            bridge.job_cancelled.connect(self._on_job_cancelled)
            bridge.job_failed.connect(self._on_job_failed)

    def refresh_state(self) -> None:
        job_id = getattr(self.main_window, "active_job_id", None)
        if not job_id:
            self.lbl_target.setText("Target: No active assessment")
            self.lbl_status.setText("Status: IDLE")
            self.terminal.append_info("Workstation ready. Launch an assessment to observe live payloads.")
            return

        status = self.main_window.assessment_service.get_status(job_id)
        context = self.main_window.job_manager.get_context(job_id)
        url = context.config.target.url if context else "Active Target"

        self.lbl_target.setText(f"Target: {url}")
        self.lbl_status.setText(f"Status: {status.status}")
        self.kpi_stage.update_value(str(status.stage))
        self.kpi_progress.update_value(f"{status.progress:.0f}%")
        self.prog_bar.setValue(int(status.progress))
        self.kpi_findings.update_value(str(len(status.findings)))
        self.terminal.append_info(f"Connected to live telemetry stream for job {job_id[:8]}.")

    def _on_stage_changed(self, stage: str, previous: str) -> None:
        self.kpi_stage.update_value(stage)
        self.terminal.append_stage(stage, previous)

    def _on_progress_updated(self, progress: float, message: str) -> None:
        self.prog_bar.setValue(int(progress))
        self.kpi_progress.update_value(f"{progress:.0f}%")
        if message:
            self.terminal.append_payload(message)

    def _on_finding_discovered(self, f_id: str, f_type: str, severity: str, param: str, title: str) -> None:
        self.terminal.append_vuln(title, param)
        job_id = getattr(self.main_window, "active_job_id", None)
        if job_id:
            count = len(self.main_window.assessment_service.get_findings(job_id))
            self.kpi_findings.update_value(str(count))
            self.kpi_dbms.update_value("PostgreSQL")

    def _on_job_completed(self, count: int, duration: float) -> None:
        self.lbl_status.setText("Status: COMPLETED")
        self.prog_bar.setValue(100)
        self.terminal.append_completed(count, duration)

    def _on_job_cancelled(self, reason: str) -> None:
        self.lbl_status.setText("Status: CANCELLED")
        self.terminal.append_cancel(reason)

    def _on_job_failed(self, error: str) -> None:
        self.lbl_status.setText("Status: FAILED")
        self.terminal.append_info(f"Failed: {error}")

    def cancel_current_scan(self) -> None:
        job_id = getattr(self.main_window, "active_job_id", None)
        if job_id:
            self.main_window.assessment_service.cancel_assessment(job_id)
