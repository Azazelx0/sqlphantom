"""
SQLPhantom PySide6 Findings and Evidence triage screen.
Faithfully reproduces Stitch findings_viewer.html:
- 6-Card Summary KPI Strip (Total Findings, Critical 9.8, High 8.5, Medium 5.3, Target DBMS, Exploitation State)
- Left Master List (Search, severity filter pills, vulnerability cards)
- Right Evidence & PoC View (Diagnostics explainer, payload box, DBMS reflection, proof matrix, schema tree, defensive remediation, packet inspection)
"""

from pathlib import Path
from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
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
        layout.setContentsMargins(18, 14, 18, 18)
        layout.setSpacing(12)

        # =========================================================================
        # 1. TOP HEADER & EXPORT REPORT BAR
        # =========================================================================
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        title_lbl = QLabel("Findings & Evidence Triage")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #F8FAFC; letter-spacing: -0.3px;")
        sub_lbl = QLabel("Target: http://testphp.vulnweb.com/listproducts.php?cat=1  ·  Authorized Scope")
        sub_lbl.setStyleSheet("font-size: 11px; color: #94A3B8; font-family: monospace;")
        title_box.addWidget(title_lbl)
        title_box.addWidget(sub_lbl)
        top_bar.addLayout(title_box)

        top_bar.addStretch()

        self.btn_export_md = QPushButton("Export Markdown")
        self.btn_export_md.setStyleSheet(
            "background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; font-size: 11px; font-weight: 600;"
        )
        self.btn_export_json = QPushButton("Export JSON")
        self.btn_export_json.setStyleSheet(
            "background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; font-size: 11px; font-weight: 600;"
        )
        self.btn_export_html = QPushButton("Export HTML Report")
        self.btn_export_html.setStyleSheet(
            "background-color: #7C3AED; color: #FFFFFF; font-weight: 700; border-radius: 6px; padding: 6px 14px; font-size: 11px;"
        )

        self.btn_export_md.clicked.connect(lambda: self.export_report(ReportFormat.MARKDOWN))
        self.btn_export_json.clicked.connect(lambda: self.export_report(ReportFormat.JSON))
        self.btn_export_html.clicked.connect(lambda: self.export_report(ReportFormat.HTML))

        top_bar.addWidget(self.btn_export_md)
        top_bar.addWidget(self.btn_export_json)
        top_bar.addWidget(self.btn_export_html)
        layout.addLayout(top_bar)

        # =========================================================================
        # 2. TOP SUMMARY KPI METRICS STRIP (6 Cards)
        # =========================================================================
        kpi_strip = QHBoxLayout()
        kpi_strip.setSpacing(10)

        # Card 1: Total Findings
        kpi1 = self._build_kpi_pill("Total Findings", "4", "confirmed", "#C084FC", "rgba(124, 58, 237, 0.15)")
        # Card 2: Critical
        kpi2 = self._build_kpi_pill("Critical Severity", "1", "CVSS 9.8", "#F87171", "rgba(239, 68, 68, 0.15)")
        # Card 3: High
        kpi3 = self._build_kpi_pill("High Severity", "2", "CVSS 8.5", "#FBBF24", "rgba(245, 158, 11, 0.15)")
        # Card 4: Medium
        kpi4 = self._build_kpi_pill("Medium Severity", "1", "CVSS 5.3", "#FACC15", "rgba(234, 179, 8, 0.15)")
        # Card 5: Target DBMS
        kpi5 = self._build_kpi_pill("Target DBMS", "PostgreSQL 15.3", "99.8% Conf", "#A855F7", "rgba(124, 58, 237, 0.15)")
        # Card 6: Exploitation State
        kpi6 = self._build_kpi_pill("Exploitation State", "Exploit Ready", "Schema Dumped", "#34D399", "rgba(16, 185, 129, 0.15)")

        kpi_strip.addWidget(kpi1)
        kpi_strip.addWidget(kpi2)
        kpi_strip.addWidget(kpi3)
        kpi_strip.addWidget(kpi4)
        kpi_strip.addWidget(kpi5)
        kpi_strip.addWidget(kpi6)
        layout.addLayout(kpi_strip)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #38BDF8; font-weight: bold; font-size: 11px;")
        layout.addWidget(self.lbl_status)

        # =========================================================================
        # 3. MASTER-DETAIL SPLITTER
        # =========================================================================
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- LEFT PANE: Master Findings Table with Filter Pills ---
        left_card = QFrame()
        left_card.setStyleSheet(
            "background-color: #111827; border: 1px solid #1E293B; border-radius: 10px; padding: 12px;"
        )
        left_layout = QVBoxLayout(left_card)
        left_layout.setSpacing(10)

        left_hdr = QHBoxLayout()
        lbl_left_title = QLabel("Confirmed Injection Vectors")
        lbl_left_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #F8FAFC;")
        lbl_sort = QLabel("Sorted by Severity")
        lbl_sort.setStyleSheet("font-size: 10px; color: #94A3B8; font-family: monospace;")
        left_hdr.addWidget(lbl_left_title)
        left_hdr.addStretch()
        left_hdr.addWidget(lbl_sort)
        left_layout.addLayout(left_hdr)

        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText("Filter findings, params, payloads...")
        self.txt_filter.setStyleSheet(
            "background-color: #050811; border: 1px solid #1E293B; border-radius: 6px; padding: 6px 10px; font-size: 11px; color: #F8FAFC;"
        )
        left_layout.addWidget(self.txt_filter)

        # Severity Filter Pills
        pills_row = QHBoxLayout()
        pills_row.setSpacing(6)
        pills = [
            ("All (4)", "#C084FC", "rgba(124, 58, 237, 0.2)"),
            ("Critical (1)", "#F87171", "rgba(239, 68, 68, 0.2)"),
            ("High (2)", "#FBBF24", "rgba(245, 158, 11, 0.2)"),
            ("Med (1)", "#FACC15", "rgba(234, 179, 8, 0.2)"),
            ("Low (0)", "#64748B", "#1E293B"),
        ]
        for p_label, text_c, bg_c in pills:
            btn_pill = QPushButton(p_label)
            btn_pill.setStyleSheet(
                f"background-color: {bg_c}; color: {text_c}; border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 2px 8px; font-size: 10px; font-weight: bold; font-family: monospace;"
            )
            pills_row.addWidget(btn_pill)
        pills_row.addStretch()
        left_layout.addLayout(pills_row)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Severity", "Type", "Param", "Title"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self._on_row_selected)
        left_layout.addWidget(self.table)
        splitter.addWidget(left_card)

        # --- RIGHT PANE: Evidence & Exploitation Detail View ---
        right_card = QFrame()
        right_card.setStyleSheet(
            "background-color: #111827; border: 1px solid #1E293B; border-radius: 10px; padding: 14px;"
        )
        right_layout = QVBoxLayout(right_card)
        right_layout.setSpacing(12)

        # Detail Header
        detail_top = QHBoxLayout()
        detail_header_box = QVBoxLayout()
        detail_header_box.setSpacing(3)

        self.lbl_detail_badge = QLabel("CRITICAL · CVSS 9.8 · CWE-89: SQL Injection")
        self.lbl_detail_badge.setStyleSheet(
            "background-color: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: bold; font-family: monospace;"
        )
        self.lbl_detail_title = QLabel("Select a finding to inspect verification evidence.")
        self.lbl_detail_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #F8FAFC;")
        self.lbl_detail_param = QLabel("")
        self.lbl_detail_param.setStyleSheet("color: #94A3B8; font-size: 11px; font-family: monospace;")

        detail_header_box.addWidget(self.lbl_detail_badge)
        detail_header_box.addWidget(self.lbl_detail_title)
        detail_header_box.addWidget(self.lbl_detail_param)
        detail_top.addLayout(detail_header_box)
        detail_top.addStretch()

        # Action Buttons Bar
        btn_act_box = QHBoxLayout()
        btn_act_box.setSpacing(6)

        btn_copy_exploit = QPushButton("Copy Exploit Payload")
        btn_copy_exploit.setStyleSheet(
            "background-color: #7C3AED; color: #FFFFFF; font-weight: bold; border-radius: 6px; padding: 6px 12px; font-size: 11px;"
        )
        btn_copy_exploit.clicked.connect(self._copy_exploit_payload)

        btn_reverify = QPushButton("↻ Re-verify")
        btn_reverify.setStyleSheet(
            "background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; font-size: 11px;"
        )

        btn_poc_curl = QPushButton("PoC cURL")
        btn_poc_curl.setStyleSheet(
            "background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; font-size: 11px;"
        )
        btn_poc_curl.clicked.connect(self._copy_poc_curl)

        btn_send_editor = QPushButton("Send to Editor →")
        btn_send_editor.setStyleSheet(
            "background-color: #1E293B; color: #C084FC; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; font-size: 11px;"
        )
        btn_send_editor.clicked.connect(lambda: self.main_window.navigate_to("request"))

        btn_act_box.addWidget(btn_copy_exploit)
        btn_act_box.addWidget(btn_reverify)
        btn_act_box.addWidget(btn_poc_curl)
        btn_act_box.addWidget(btn_send_editor)
        detail_top.addLayout(btn_act_box)
        right_layout.addLayout(detail_top)

        # Tabbed Details
        self.tabs = QTabWidget()

        # Tab 1: Evidence & PoC
        tab_evidence = QWidget()
        ev_layout = QVBoxLayout(tab_evidence)
        ev_layout.setContentsMargins(10, 10, 10, 10)
        ev_layout.setSpacing(10)

        # Explainer Box
        explainer_box = QFrame()
        explainer_box.setStyleSheet(
            "background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 10px;"
        )
        exp_l = QVBoxLayout(explainer_box)
        exp_l.setSpacing(4)
        lbl_exp_title = QLabel("🧠 Injection Mechanism & Vulnerability Diagnostics")
        lbl_exp_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #C084FC;")
        self.lbl_exp_desc = QLabel(
            "The target parameter is concatenated directly into a dynamic backend SQL query without parameterization or numeric sanitization. By supplying an explicit CAST(... AS integer) conversion, arbitrary string output (such as DB version, current schema, or user hashes) is forced into PostgreSQL's internal exception handler and reflected verbatim within the HTTP 500 error body."
        )
        self.lbl_exp_desc.setStyleSheet("font-size: 11px; color: #94A3B8; line-height: 1.4;")
        self.lbl_exp_desc.setWordWrap(True)
        exp_l.addWidget(lbl_exp_title)
        exp_l.addWidget(self.lbl_exp_desc)
        ev_layout.addWidget(explainer_box)

        # Active Exploit Payload Code Box
        ev_layout.addWidget(QLabel("Active Exploit Payload (Synthesized by sqlmap engine):"))
        self.txt_payload = QPlainTextEdit()
        self.txt_payload.setReadOnly(True)
        self.txt_payload.setMaximumHeight(65)
        self.txt_payload.setStyleSheet(
            "background-color: #050811; color: #FBBF24; font-family: monospace; font-size: 11px; border: 1px solid #1E293B; border-radius: 6px;"
        )
        ev_layout.addWidget(self.txt_payload)

        # Raw DBMS Error Reflection Box
        ev_layout.addWidget(QLabel("Raw DBMS Error Response Reflection (Exfiltrated Memory Output):"))
        self.txt_evidence = QPlainTextEdit()
        self.txt_evidence.setReadOnly(True)
        self.txt_evidence.setMaximumHeight(75)
        self.txt_evidence.setStyleSheet(
            "background-color: #050811; color: #34D399; font-family: monospace; font-size: 11px; border: 1px solid #1E293B; border-radius: 6px;"
        )
        ev_layout.addWidget(self.txt_evidence)

        # Proof Matrix Row (Current DB User, Active Database, Privilege Escalation)
        matrix_row = QHBoxLayout()
        matrix_row.setSpacing(8)
        m1 = self._build_matrix_card("Current DB User", "postgres", "superuser", "#34D399")
        m2 = self._build_matrix_card("Active Database", "acme_store_prod", "UTF8 encoding", "#C084FC")
        m3 = self._build_matrix_card("Privilege Escalation", "DBA: True", "COPY TO writeable", "#F87171")
        matrix_row.addWidget(m1)
        matrix_row.addWidget(m2)
        matrix_row.addWidget(m3)
        ev_layout.addLayout(matrix_row)

        self.tabs.addTab(tab_evidence, "Evidence & PoC")

        # Tab 2: HTTP Request / Response
        tab_traffic = QWidget()
        tr_layout = QVBoxLayout(tab_traffic)
        tr_layout.setContentsMargins(10, 10, 10, 10)
        tr_split = QHBoxLayout()
        tr_split.setSpacing(10)

        self.txt_raw_req = QPlainTextEdit()
        self.txt_raw_req.setReadOnly(True)
        self.txt_raw_req.setStyleSheet(
            "background-color: #050811; color: #CBD5E1; font-family: monospace; font-size: 10px; border: 1px solid #1E293B; border-radius: 6px;"
        )
        self.txt_raw_res = QPlainTextEdit()
        self.txt_raw_res.setReadOnly(True)
        self.txt_raw_res.setStyleSheet(
            "background-color: #050811; color: #34D399; font-family: monospace; font-size: 10px; border: 1px solid #1E293B; border-radius: 6px;"
        )
        tr_split.addWidget(self.txt_raw_req)
        tr_split.addWidget(self.txt_raw_res)
        tr_layout.addLayout(tr_split)
        self.tabs.addTab(tab_traffic, "HTTP Request / Response")

        # Tab 3: Extracted Schema Tree
        tab_schema = QWidget()
        sc_layout = QVBoxLayout(tab_schema)
        sc_layout.setContentsMargins(10, 10, 10, 10)
        self.txt_schema_preview = QPlainTextEdit()
        self.txt_schema_preview.setReadOnly(True)
        self.txt_schema_preview.setStyleSheet(
            "background-color: #050811; color: #C084FC; font-family: monospace; font-size: 11px; border: 1px solid #1E293B; border-radius: 6px;"
        )
        self.txt_schema_preview.setPlainText(
            "📁 Database: acme_store_prod (PostgreSQL 15.3)\n"
            "   ├── 📊 Table: users (1,420 rows) [P1 Sensitive]\n"
            "   │   ├── id [int4, PRIMARY KEY]\n"
            "   │   ├── username [varchar(64)]\n"
            "   │   ├── password_hash [varchar(128)]\n"
            "   │   └── role [varchar(32)]\n"
            "   ├── 📊 Table: products (84 rows)\n"
            "   │   ├── id [int4, PRIMARY KEY]\n"
            "   │   ├── cat_id [int4]\n"
            "   │   ├── name [varchar(128)]\n"
            "   │   └── price [numeric(10,2)]\n"
            "   └── 📊 Table: orders (9,310 rows)\n"
            "       ├── id [int4, PRIMARY KEY]\n"
            "       ├── user_id [int4]\n"
            "       └── order_total [numeric(10,2)]"
        )
        sc_layout.addWidget(self.txt_schema_preview)
        btn_dump_rows = QPushButton("📥 Dump Table Rows (CSV)")
        btn_dump_rows.setStyleSheet(
            "background-color: #7C3AED; color: #FFFFFF; font-weight: bold; border-radius: 6px; padding: 6px 14px; font-size: 11px;"
        )
        btn_dump_rows.clicked.connect(lambda: self.main_window.navigate_to("schema"))
        sc_layout.addWidget(btn_dump_rows)
        self.tabs.addTab(tab_schema, "Extracted Schema Tree (3 tables)")

        # Tab 4: Defensive Remediation Assistant
        tab_remediation = QWidget()
        rem_layout = QVBoxLayout(tab_remediation)
        rem_layout.setContentsMargins(10, 10, 10, 10)

        cwe_info = RemediationAssistant.get_cwe_details()
        lbl_cwe = QLabel(f"<b>CWE:</b> {cwe_info['cwe_id']} - {cwe_info['cwe_title']} | <b>OWASP:</b> {cwe_info['owasp_top_10']}")
        lbl_cwe.setStyleSheet("color: #CBD5E1; font-size: 11px;")
        rem_layout.addWidget(lbl_cwe)

        self.rem_subtabs = QTabWidget()

        self.txt_rem_py_sqlalchemy = QPlainTextEdit()
        self.txt_rem_py_sqlalchemy.setReadOnly(True)
        self.txt_rem_py_sqlalchemy.setStyleSheet("background-color: #050811; color: #E2E8F0; font-family: monospace; font-size: 11px;")
        self.rem_subtabs.addTab(self.txt_rem_py_sqlalchemy, "Python (SQLAlchemy)")

        self.txt_rem_py_psycopg = QPlainTextEdit()
        self.txt_rem_py_psycopg.setReadOnly(True)
        self.txt_rem_py_psycopg.setStyleSheet("background-color: #050811; color: #E2E8F0; font-family: monospace; font-size: 11px;")
        self.rem_subtabs.addTab(self.txt_rem_py_psycopg, "Python (psycopg)")

        self.txt_rem_node = QPlainTextEdit()
        self.txt_rem_node.setReadOnly(True)
        self.txt_rem_node.setStyleSheet("background-color: #050811; color: #E2E8F0; font-family: monospace; font-size: 11px;")
        self.rem_subtabs.addTab(self.txt_rem_node, "Node.js (pg)")

        self.txt_rem_java = QPlainTextEdit()
        self.txt_rem_java.setReadOnly(True)
        self.txt_rem_java.setStyleSheet("background-color: #050811; color: #E2E8F0; font-family: monospace; font-size: 11px;")
        self.rem_subtabs.addTab(self.txt_rem_java, "Java (JDBC)")

        self.txt_rem_php = QPlainTextEdit()
        self.txt_rem_php.setReadOnly(True)
        self.txt_rem_php.setStyleSheet("background-color: #050811; color: #E2E8F0; font-family: monospace; font-size: 11px;")
        self.rem_subtabs.addTab(self.txt_rem_php, "PHP (PDO)")

        rem_layout.addWidget(self.rem_subtabs)

        btn_copy_rem = QPushButton("Copy Code Snippet")
        btn_copy_rem.setProperty("class", "secondary")
        btn_copy_rem.clicked.connect(self._copy_current_remediation)
        rem_layout.addWidget(btn_copy_rem)

        self.tabs.addTab(tab_remediation, "Defensive Remediation")

        # Tab 5: Aggregated Findings Summary
        tab_agg = QWidget()
        agg_layout = QVBoxLayout(tab_agg)
        agg_layout.setContentsMargins(10, 10, 10, 10)
        self.txt_aggregation = QPlainTextEdit()
        self.txt_aggregation.setReadOnly(True)
        self.txt_aggregation.setStyleSheet("background-color: #050811; color: #38BDF8; font-family: monospace; font-size: 11px;")
        agg_layout.addWidget(self.txt_aggregation)
        self.tabs.addTab(tab_agg, "Aggregated Summary")

        right_layout.addWidget(self.tabs)
        splitter.addWidget(right_card)

        splitter.setSizes([450, 750])
        layout.addWidget(splitter)
        self.refresh_findings()

    def _build_kpi_pill(self, title: str, val: str, tag: str, color: str, bg: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            f"background-color: #111827; border: 1px solid #1E293B; border-radius: 8px; padding: 8px 10px;"
        )
        l = QVBoxLayout(frame)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(2)

        lbl_t = QLabel(title.upper())
        lbl_t.setStyleSheet("font-size: 9px; font-weight: bold; color: #94A3B8; font-family: monospace;")
        l.addWidget(lbl_t)

        val_row = QHBoxLayout()
        val_row.setSpacing(6)
        lbl_v = QLabel(val)
        lbl_v.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {color};")
        lbl_tag = QLabel(tag)
        lbl_tag.setStyleSheet(
            f"font-size: 9px; font-family: monospace; font-weight: bold; color: {color}; background-color: {bg}; border-radius: 4px; padding: 2px 4px;"
        )
        val_row.addWidget(lbl_v)
        val_row.addWidget(lbl_tag)
        val_row.addStretch()
        l.addLayout(val_row)
        return frame

    def _build_matrix_card(self, title: str, val: str, sub: str, color: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            "background-color: #0F172A; border: 1px solid #1E293B; border-radius: 6px; padding: 6px 10px;"
        )
        l = QVBoxLayout(frame)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(2)
        lbl_t = QLabel(title.upper())
        lbl_t.setStyleSheet("font-size: 9px; font-weight: bold; color: #94A3B8; font-family: monospace;")
        lbl_v = QLabel(f"<span style='color: {color}; font-weight: bold; font-family: monospace;'>{val}</span> <span style='font-size: 10px; color: #64748B;'>({sub})</span>")
        lbl_v.setTextFormat(Qt.TextFormat.RichText)
        l.addWidget(lbl_t)
        l.addWidget(lbl_v)
        return frame

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

            item_sev = QTableWidgetItem(f"[{f.severity}]")
            if str(f.severity) == "CRITICAL":
                item_sev.setForeground(Qt.GlobalColor.red)
            elif str(f.severity) == "HIGH":
                item_sev.setForeground(Qt.GlobalColor.yellow)
            else:
                item_sev.setForeground(Qt.GlobalColor.cyan)

            item_type = QTableWidgetItem(str(f.finding_type))
            item_param = QTableWidgetItem(f.parameter)
            item_title = QTableWidgetItem(f.title)

            # Store ID in title item user data
            item_title.setData(1000, f.id)

            self.table.setItem(row, 0, item_sev)
            self.table.setItem(row, 1, item_type)
            self.table.setItem(row, 2, item_param)
            self.table.setItem(row, 3, item_title)

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
        self.lbl_detail_badge.setText(f"{finding.severity} · CVSS 9.8 · CWE-89: SQL Injection")
        self.lbl_detail_title.setText(f"{finding.title}")
        self.lbl_detail_param.setText(
            f"Endpoint: {finding.url}  |  Parameter: {finding.parameter}  |  Confidence: {finding.confidence}"
        )
        self.txt_payload.setPlainText(finding.payload)
        self.txt_evidence.setPlainText(
            finding.evidence
            or 'ERROR: invalid input syntax for integer: "PostgreSQL 15.3 on x86_64-pc-linux-gnu, compiled by gcc 11.2.0"\nSTATEMENT: SELECT * FROM products WHERE cat_id = 1\' AND CAST((SELECT version()) AS int)--'
        )

        # Mock Raw Traffic
        self.txt_raw_req.setPlainText(
            f"GET {finding.url} HTTP/1.1\n"
            "Host: testphp.vulnweb.com\n"
            "User-Agent: SQLPhantom/4.2.0 (Automated Pentest Engine)\n"
            f"Payload: {finding.payload}\n"
            "Connection: keep-alive"
        )
        self.txt_raw_res.setPlainText(
            "HTTP/1.1 500 Internal Server Error\n"
            "Server: nginx/1.19.0\n"
            "Content-Type: text/html; charset=UTF-8\n\n"
            f"<!-- SQL Error Reflection -->\n{finding.evidence or 'syntax error at or near CAST'}"
        )

        # Populate defensive snippets
        snippets = RemediationAssistant.generate_snippets(finding)
        self.txt_rem_py_sqlalchemy.setPlainText(snippets.get("python_sqlalchemy", ""))
        self.txt_rem_py_psycopg.setPlainText(snippets.get("python_psycopg", ""))
        self.txt_rem_node.setPlainText(snippets.get("nodejs_pg", ""))
        self.txt_rem_java.setPlainText(snippets.get("java_jdbc", ""))
        self.txt_rem_php.setPlainText(snippets.get("php_pdo", ""))

    def _copy_exploit_payload(self) -> None:
        if self._current_finding:
            QApplication.clipboard().setText(self._current_finding.payload)
            self.lbl_status.setText("Exploit payload copied to clipboard!")

    def _copy_poc_curl(self) -> None:
        if self._current_finding:
            curl_cmd = f"curl -s -i \"{self._current_finding.url}\" -H 'User-Agent: SQLPhantom/4.2.0'"
            QApplication.clipboard().setText(curl_cmd)
            self.lbl_status.setText("PoC cURL command copied to clipboard!")

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
