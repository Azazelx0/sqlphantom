"""
SQLPhantom PySide6 Sessions and Project Workspace History screen.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sqlphantom.domain.models import Session


class SessionsScreen(QWidget):
    """
    Project Workspace and Historical Session Management screen.
    Allows operators to inspect past assessment runs, review status and notes,
    and run session drift comparison between sequential audits.
    """

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self._sessions_map: dict[str, Session] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Top Bar
        top_bar = QHBoxLayout()
        title_lbl = QLabel("Assessment Sessions & Project Workspaces")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC;")
        top_bar.addWidget(title_lbl)
        top_bar.addStretch()

        self.btn_refresh = QPushButton("Refresh Sessions")
        self.btn_refresh.setProperty("class", "secondary")
        self.btn_refresh.clicked.connect(self.refresh_sessions)
        top_bar.addWidget(self.btn_refresh)

        self.btn_compare = QPushButton("Compare Selected Sessions")
        self.btn_compare.setProperty("class", "secondary")
        self.btn_compare.clicked.connect(self._compare_sessions)
        top_bar.addWidget(self.btn_compare)

        layout.addLayout(top_bar)

        self.lbl_status = QLabel("Select sessions to inspect historical audit execution.")
        self.lbl_status.setStyleSheet("color: #38BDF8; font-weight: bold;")
        layout.addWidget(self.lbl_status)

        # Splitter: Sessions Table vs Detail / Comparison
        splitter = QSplitter()

        # Left Table
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("Historical Audit Sessions:"))

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Target URL", "Findings", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self._on_session_selected)
        left_layout.addWidget(self.table)
        splitter.addWidget(left_widget)

        # Right Detail / Diff Console
        right_frame = QFrame()
        right_frame.setProperty("class", "card-frame")
        right_layout = QVBoxLayout(right_frame)

        self.lbl_detail_title = QLabel("Session Detail & Vulnerability Drift:")
        self.lbl_detail_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #A855F7;")
        right_layout.addWidget(self.lbl_detail_title)

        self.txt_diff = QPlainTextEdit()
        self.txt_diff.setReadOnly(True)
        self.txt_diff.setStyleSheet("background-color: #050811; color: #E2E8F0; font-family: monospace;")
        right_layout.addWidget(self.txt_diff)
        splitter.addWidget(right_frame)

        splitter.setSizes([450, 550])
        layout.addWidget(splitter)
        self.refresh_sessions()

    def refresh_sessions(self) -> None:
        self.table.setRowCount(0)
        self._sessions_map.clear()

        sessions: list[Session] = []
        if hasattr(self.main_window, "session_repo") and self.main_window.session_repo:
            sessions = self.main_window.session_repo.list_all()

        for s in sessions:
            self._sessions_map[s.id] = s
            row = self.table.rowCount()
            self.table.insertRow(row)

            date_str = s.created_at.strftime("%Y-%m-%d %H:%M")
            url_str = str(s.config.target.url)
            findings_count = len(s.result.findings) if s.result else 0
            if s.result:
                status_str = s.result.status.value if hasattr(s.result.status, "value") else str(s.result.status)
            else:
                status_str = "PENDING"

            item_date = QTableWidgetItem(date_str)
            item_url = QTableWidgetItem(url_str)
            item_findings = QTableWidgetItem(str(findings_count))
            item_status = QTableWidgetItem(status_str)

            # Store ID in date item
            item_date.setData(1000, s.id)

            self.table.setItem(row, 0, item_date)
            self.table.setItem(row, 1, item_url)
            self.table.setItem(row, 2, item_findings)
            self.table.setItem(row, 3, item_status)

        if sessions:
            self.lbl_status.setText(f"Loaded {len(sessions)} session(s) from persistent store.")
            self._display_session(sessions[0])
        else:
            self.lbl_status.setText("No saved sessions. Run an assessment to create audit history.")
            self.txt_diff.setPlainText("No sessions found in local SQLite database.")

    def _on_session_selected(self) -> None:
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        date_item = self.table.item(row, 0)
        if date_item:
            session_id = date_item.data(1000)
            if session_id and session_id in self._sessions_map:
                self._display_session(self._sessions_map[session_id])

    def _display_session(self, session: Session) -> None:
        detail_lines = [
            f"=== Session: {session.id} ===",
            f"Project ID: {session.project_id}",
            f"Created At: {session.created_at.isoformat()}",
            f"Target URL: {session.config.target.url}",
            f"HTTP Method: {session.config.target.method}",
            f"Testing Level: {session.config.level} | Risk: {session.config.risk}",
            f"Threads: {session.config.threads} | Timeout: {session.config.timeout}s",
            "",
            f"Findings Discovered: {len(session.result.findings) if session.result else 0}",
        ]
        if session.result and session.result.findings:
            detail_lines.append("")
            detail_lines.append("Vulnerability Breakdown:")
            for f in session.result.findings:
                detail_lines.append(f"  • [{f.severity}] {f.title} (Param: {f.parameter})")

        self.txt_diff.setPlainText("\n".join(detail_lines))

    def _compare_sessions(self) -> None:
        selected_rows = list({item.row() for item in self.table.selectedItems()})
        if len(selected_rows) < 2:
            self.lbl_status.setText("Please select at least 2 sessions to run vulnerability comparison.")
            return

        row1, row2 = selected_rows[0], selected_rows[1]
        id1 = self.table.item(row1, 0).data(1000)
        id2 = self.table.item(row2, 0).data(1000)

        s1 = self._sessions_map.get(id1)
        s2 = self._sessions_map.get(id2)
        if not s1 or not s2 or not s1.result or not s2.result:
            self.lbl_status.setText("Both selected sessions must have completed results.")
            return

        from sqlphantom.reporting.generator import compare_sessions

        diff = compare_sessions(s1, s2)
        diff_lines = [
            "=== Vulnerability Drift Comparison ===",
            f"Baseline Session: {s1.id[:8]} ({s1.created_at.strftime('%Y-%m-%d %H:%M')})",
            f"Target Session:   {s2.id[:8]} ({s2.created_at.strftime('%Y-%m-%d %H:%M')})",
            "",
            f"New Findings (Introduced):    {len(diff.new_findings)}",
            f"Resolved Findings (Remediated): {len(diff.resolved_findings)}",
            f"Persistent Findings (Common):   {len(diff.common_findings)}",
            "",
        ]

        if diff.new_findings:
            diff_lines.append("🚨 New Findings:")
            for nf in diff.new_findings:
                diff_lines.append(f"  + [{nf.severity}] {nf.title} (Param: {nf.parameter})")
            diff_lines.append("")

        if diff.resolved_findings:
            diff_lines.append("✅ Remediated Findings:")
            for rf in diff.resolved_findings:
                diff_lines.append(f"  - [{rf.severity}] {rf.title} (Param: {rf.parameter})")
            diff_lines.append("")

        self.txt_diff.setPlainText("\n".join(diff_lines))
        self.lbl_status.setText(f"Comparison complete: {len(diff.new_findings)} new, {len(diff.resolved_findings)} resolved.")
