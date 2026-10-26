"""
SQLPhantom PySide6 Dashboard screen.
"""

from typing import Any

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sqlphantom.gui.widgets.kpi_card import KPICard


class DashboardScreen(QWidget):
    """
    Main workstation dashboard presenting quick-start actions,
    system telemetry, and recent assessment targets.
    """

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header Title
        header_lbl = QLabel("Penetration Testing Workstation")
        header_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC;")
        sub_lbl = QLabel("sqlmap Enhanced · Core Security Operations & Telemetry")
        sub_lbl.setStyleSheet("font-size: 13px; color: #94A3B8;")
        main_layout.addWidget(header_lbl)
        main_layout.addWidget(sub_lbl)

        # KPI Metrics Row
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        self.kpi_projects = KPICard("Projects", "1", "Active Workspaces")
        self.kpi_workers = KPICard("Active Workers", "0", "Ready for Dispatch")
        self.kpi_findings = KPICard("Findings", "0", "Vulnerabilities")
        self.kpi_engine = KPICard("Engine State", "IDLE", "sqlmap API Online")

        kpi_row.addWidget(self.kpi_projects)
        kpi_row.addWidget(self.kpi_workers)
        kpi_row.addWidget(self.kpi_findings)
        kpi_row.addWidget(self.kpi_engine)
        main_layout.addLayout(kpi_row)

        # Action Buttons Launchpad
        action_card = QFrame()
        action_card.setProperty("class", "card-frame")
        action_layout = QHBoxLayout(action_card)
        action_layout.setContentsMargins(12, 10, 12, 10)

        self.btn_wizard = QPushButton("Launch Assessment Wizard")
        self.btn_fast_scan = QPushButton("Run Fast Test Scan")
        self.btn_fast_scan.setProperty("class", "secondary")
        self.btn_view_findings = QPushButton("View Confirmed Findings")
        self.btn_view_findings.setProperty("class", "secondary")

        self.btn_wizard.clicked.connect(lambda: self.main_window.navigate_to("wizard"))
        self.btn_fast_scan.clicked.connect(self.main_window.launch_quick_scan)
        self.btn_view_findings.clicked.connect(lambda: self.main_window.navigate_to("findings"))

        action_layout.addWidget(self.btn_wizard)
        action_layout.addWidget(self.btn_fast_scan)
        action_layout.addWidget(self.btn_view_findings)
        action_layout.addStretch()
        main_layout.addWidget(action_card)

        # Recent Targets Table
        targets_card = QFrame()
        targets_card.setProperty("class", "card-frame")
        targets_layout = QVBoxLayout(targets_card)

        tbl_title = QLabel("Registered Projects & Targets")
        tbl_title.setProperty("class", "card-title")
        targets_layout.addWidget(tbl_title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Project", "Target URL", "Method", "Scope Domain", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        targets_layout.addWidget(self.table)

        main_layout.addWidget(targets_card)
        self.refresh_data()

    def refresh_data(self) -> None:
        self.table.setRowCount(0)
        app_services = self.main_window.project_service

        if app_services:
            projects = app_services.list_projects()
            self.kpi_projects.update_value(str(len(projects)))

            total_findings = 0
            if self.main_window.finding_repo:
                total_findings = len(self.main_window.finding_repo.list_all())
            self.kpi_findings.update_value(str(total_findings))

            for proj in projects:
                if not proj.targets:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(proj.name))
                    self.table.setItem(row, 1, QTableWidgetItem("(No targets configured)"))
                    self.table.setItem(row, 2, QTableWidgetItem("-"))
                    self.table.setItem(row, 3, QTableWidgetItem("-"))
                    self.table.setItem(row, 4, QTableWidgetItem("Ready"))
                else:
                    for target in proj.targets:
                        row = self.table.rowCount()
                        self.table.insertRow(row)
                        self.table.setItem(row, 0, QTableWidgetItem(proj.name))
                        self.table.setItem(row, 1, QTableWidgetItem(target.url))
                        self.table.setItem(row, 2, QTableWidgetItem(str(target.method)))
                        self.table.setItem(row, 3, QTableWidgetItem("In-Scope"))
                        self.table.setItem(row, 4, QTableWidgetItem("Configured"))
