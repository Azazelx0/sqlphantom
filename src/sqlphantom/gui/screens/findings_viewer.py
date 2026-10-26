"""
SQLPhantom PySide6 Findings and Evidence triage screen.
"""

from pathlib import Path
from typing import Any
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from sqlphantom.domain.enums import ReportFormat
from sqlphantom.domain.models import Finding
from sqlphantom.domain.aggregation import aggregate_findings
from sqlphantom.reporting.remediation import RemediationAssistant


class FindingsViewerScreen(QWidget):
    """
    Master-detail triage interface for inspecting confirmed vulnerabilities,
    technical payloads, extracted evidence, defensive remediation guidance,
    and exporting formal reports.
    """

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window
        self._findings_map: dict[str, Finding] = {}
        self._current_finding: Finding | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header with export buttons
        top_bar = QHBoxLayout()
        title_lbl = QLabel("Confirmed Findings & Evidence Triage")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC;")
        top_bar.addWidget(title_lbl)
        top_bar.addStretch()

        self.btn_export_md = QPushButton("Export Markdown")
        self.btn_export_md.setProperty("class", "secondary")
        self.btn_export_json = QPushButton("Export JSON")
        self.btn_export_json.setProperty("class", "secondary")
        self.btn_export_html = QPushButton("Export HTML")
        self.btn_export_html.setProperty("class", "secondary")

        self.btn_export_md.clicked.connect(lambda: self.export_report(ReportFormat.MARKDOWN))
        self.btn_export_json.clicked.connect(lambda: self.export_report(ReportFormat.JSON))
        self.btn_export_html.clicked.connect(lambda: self.export_report(ReportFormat.HTML))

        top_bar.addWidget(self.btn_export_md)
        top_bar.addWidget(self.btn_export_json)
        top_bar.addWidget(self.btn_export_html)
        layout.addLayout(top_bar)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #38BDF8; font-weight: bold;")
        layout.addWidget(self.lbl_status)

        # Master-Detail Splitter
        splitter = QSplitter()

        # Left Pane: Table
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("Discovered Vulnerabilities:"))

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Severity", "Type", "Param", "Title"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self._on_row_selected)
        left_layout.addWidget(self.table)
        splitter.addWidget(left_widget)

        # Right Pane: Tabbed Detail
        right_frame = QFrame()
        right_frame.setProperty("class", "card-frame")
        right_layout = QVBoxLayout(right_frame)

        self.lbl_detail_title = QLabel("Select a finding to inspect verification evidence.")
        self.lbl_detail_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #A855F7;")
        self.lbl_detail_param = QLabel("")
        self.lbl_detail_param.setStyleSheet("color: #94A3B8;")

        right_layout.addWidget(self.lbl_detail_title)
        right_layout.addWidget(self.lbl_detail_param)

        self.tabs = QTabWidget()

        # Tab 1: Evidence
        tab_evidence = QWidget()
        ev_layout = QVBoxLayout(tab_evidence)
        ev_layout.addWidget(QLabel("Observed Payload Pattern:"))
        self.txt_payload = QPlainTextEdit()
        self.txt_payload.setReadOnly(True)
        self.txt_payload.setMaximumHeight(80)
        self.txt_payload.setStyleSheet("background-color: #050811; color: #FBBF24; font-family: monospace;")
        ev_layout.addWidget(self.txt_payload)

        ev_layout.addWidget(QLabel("Raw Technical Evidence / Diagnostic Reflection:"))
        self.txt_evidence = QPlainTextEdit()
        self.txt_evidence.setReadOnly(True)
        self.txt_evidence.setStyleSheet("background-color: #050811; color: #34D399; font-family: monospace;")
        ev_layout.addWidget(self.txt_evidence)
        self.tabs.addTab(tab_evidence, "Evidence & Telemetry")

        # Tab 2: Defensive Remediation Assistant
        tab_remediation = QWidget()
        rem_layout = QVBoxLayout(tab_remediation)
        
        cwe_info = RemediationAssistant.get_cwe_details()
        lbl_cwe = QLabel(f"<b>CWE:</b> {cwe_info['cwe_id']} - {cwe_info['cwe_title']} | <b>OWASP:</b> {cwe_info['owasp_top_10']}")
        lbl_cwe.setStyleSheet("color: #CBD5E1; font-size: 12px;")
        rem_layout.addWidget(lbl_cwe)

        self.rem_subtabs = QTabWidget()
        
        self.txt_rem_py_sqlalchemy = QPlainTextEdit()
        self.txt_rem_py_sqlalchemy.setReadOnly(True)
        self.txt_rem_py_sqlalchemy.setStyleSheet("background-color: #050811; color: #E2E8F0; font-family: monospace;")
        self.rem_subtabs.addTab(self.txt_rem_py_sqlalchemy, "Python (SQLAlchemy)")

        self.txt_rem_py_psycopg = QPlainTextEdit()
        self.txt_rem_py_psycopg.setReadOnly(True)
        self.txt_rem_py_psycopg.setStyleSheet("background-color: #050811; color: #E2E8F0; font-family: monospace;")
        self.rem_subtabs.addTab(self.txt_rem_py_psycopg, "Python (psycopg)")

        self.txt_rem_node = QPlainTextEdit()
        self.txt_rem_node.setReadOnly(True)
        self.txt_rem_node.setStyleSheet("background-color: #050811; color: #E2E8F0; font-family: monospace;")
        self.rem_subtabs.addTab(self.txt_rem_node, "Node.js (pg)")

        self.txt_rem_java = QPlainTextEdit()
        self.txt_rem_java.setReadOnly(True)
        self.txt_rem_java.setStyleSheet("background-color: #050811; color: #E2E8F0; font-family: monospace;")
        self.rem_subtabs.addTab(self.txt_rem_java, "Java (JDBC)")

        self.txt_rem_php = QPlainTextEdit()
        self.txt_rem_php.setReadOnly(True)
        self.txt_rem_php.setStyleSheet("background-color: #050811; color: #E2E8F0; font-family: monospace;")
        self.rem_subtabs.addTab(self.txt_rem_php, "PHP (PDO)")

        rem_layout.addWidget(self.rem_subtabs)

        btn_copy_rem = QPushButton("Copy Code Snippet")
        btn_copy_rem.setProperty("class", "secondary")
        btn_copy_rem.clicked.connect(self._copy_current_remediation)
        rem_layout.addWidget(btn_copy_rem)

        self.tabs.addTab(tab_remediation, "Defensive Remediation")

        # Tab 3: Aggregated Findings Summary
        tab_agg = QWidget()
        agg_layout = QVBoxLayout(tab_agg)
        self.txt_aggregation = QPlainTextEdit()
        self.txt_aggregation.setReadOnly(True)
        self.txt_aggregation.setStyleSheet("background-color: #050811; color: #38BDF8; font-family: monospace;")
        agg_layout.addWidget(self.txt_aggregation)
        self.tabs.addTab(tab_agg, "Aggregated Summary")

        right_layout.addWidget(self.tabs)
        splitter.addWidget(right_frame)

        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        self.refresh_findings()

    def refresh_findings(self) -> None:
        self.table.setRowCount(0)
        self._findings_map.clear()

        findings: list[Finding] = []

        # From active job
        job_id = getattr(self.main_window, "active_job_id", None)
        if job_id and hasattr(self.main_window, "assessment_service"):
            findings.extend(self.main_window.assessment_service.get_findings(job_id))

        # From repository
        if hasattr(self.main_window, "finding_repo") and self.main_window.finding_repo:
            repo_findings = self.main_window.finding_repo.list_all()
            for rf in repo_findings:
                if rf.id not in [f.id for f in findings]:
                    findings.append(rf)

        for f in findings:
            self._findings_map[f.id] = f
            row = self.table.rowCount()
            self.table.insertRow(row)

            item_sev = QTableWidgetItem(str(f.severity))
            item_type = QTableWidgetItem(str(f.finding_type))
            item_param = QTableWidgetItem(f.parameter)
            item_title = QTableWidgetItem(f.title)

            # Store ID in title item user data
            item_title.setData(1000, f.id)

            self.table.setItem(row, 0, item_sev)
            self.table.setItem(row, 1, item_type)
            self.table.setItem(row, 2, item_param)
            self.table.setItem(row, 3, item_title)

        # Update Aggregated View
        if findings:
            agg_list = aggregate_findings(findings)
            agg_text_lines = ["=== Consolidated Target Vulnerability Surface ===", ""]
            for a in agg_list:
                agg_text_lines.append(f"• Target Endpoint: {a.target_url}")
                agg_text_lines.append(f"  Vulnerable Param: {a.parameter}")
                agg_text_lines.append(f"  Severity: [{a.highest_severity}]")
                agg_text_lines.append(f"  Detected Techniques: {a.technique_summary}")
                agg_text_lines.append(f"  Underlying Finding Count: {len(a.findings)}")
                agg_text_lines.append("")
            self.txt_aggregation.setPlainText("\n".join(agg_text_lines))

            self.display_finding(findings[0])
            self.lbl_status.setText(f"Showing {len(findings)} confirmed security finding(s) across {len(agg_list)} parameter(s).")
        else:
            self.txt_aggregation.setPlainText("No findings available to aggregate.")
            self.lbl_status.setText("No findings yet. Run an assessment to populate vulnerabilities.")

    def _on_row_selected(self) -> None:
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        title_item = self.table.item(row, 3)
        if title_item:
            finding_id = title_item.data(1000)
            if finding_id and finding_id in self._findings_map:
                self.display_finding(self._findings_map[finding_id])

    def display_finding(self, finding: Finding) -> None:
        self._current_finding = finding
        self.lbl_detail_title.setText(f"[{finding.severity}] {finding.title}")
        self.lbl_detail_param.setText(
            f"Endpoint: {finding.url}  |  Parameter: {finding.parameter}  |  Confidence: {finding.confidence}"
        )
        self.txt_payload.setPlainText(finding.payload)
        self.txt_evidence.setPlainText(finding.evidence or "Payload yielded differential response.")

        # Populate defensive snippets
        snippets = RemediationAssistant.generate_snippets(finding)
        self.txt_rem_py_sqlalchemy.setPlainText(snippets.get("python_sqlalchemy", ""))
        self.txt_rem_py_psycopg.setPlainText(snippets.get("python_psycopg", ""))
        self.txt_rem_node.setPlainText(snippets.get("nodejs_pg", ""))
        self.txt_rem_java.setPlainText(snippets.get("java_jdbc", ""))
        self.txt_rem_php.setPlainText(snippets.get("php_pdo", ""))

    def _copy_current_remediation(self) -> None:
        current_widget = self.rem_subtabs.currentWidget()
        if isinstance(current_widget, QPlainTextEdit):
            text = current_widget.toPlainText()
            QApplication.clipboard().setText(text)
            self.lbl_status.setText("Remediation code snippet copied to clipboard!")

    def export_report(self, fmt: ReportFormat) -> None:
        findings = list(self._findings_map.values())
        if not findings:
            self.lbl_status.setText("Cannot export: no findings available")
            return

        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)

        ext = fmt.value.lower()
        content = self.main_window.report_service.generate_report(findings, fmt=fmt)
        out_file = report_dir / f"assessment_report.{ext}"
        out_file.write_text(content, encoding="utf-8")
        self.lbl_status.setText(f"Exported {fmt.value} report to {out_file.absolute()}")
