"""
SQLPhantom PySide6 Live Assessment Monitoring screen.
Faithfully reproduces Stitch live_monitor.html:
- 6-Stage Execution Pipeline Stepper (INIT, PROBE, FP, DETECTION, EXPLOITATION, CLEANUP)
- 5-Card Live Telemetry Strip (Current Technique, Requests Sent, Active Parameter, DBMS Identified, Network Latency)
- Center Split (7 cols: macOS terminal console with filters; 5 cols: Confirmed Injection Vectors Feed)
- Bottom Packet Inspector Drawer (HTTP Request/Response raw packet preview)
"""

from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from sqlphantom.gui.widgets.kpi_card import KPICard
from sqlphantom.gui.widgets.terminal_widget import TerminalWidget


class LiveMonitorScreen(QWidget):
    """
    Real-time assessment observation workstation showing telemetry,
    live execution stages, terminal event logs, confirmed injection vectors,
    and raw packet inspection.
    """

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(18, 14, 18, 18)
        layout.setSpacing(14)

        # =========================================================================
        # 1. TOP TARGET CONTEXT & WORKSTATION EXECUTION HEADER
        # =========================================================================
        header_card = QFrame()
        header_card.setStyleSheet(
            "background-color: #111827; border: 1px solid #1E293B; border-radius: 10px; padding: 10px 16px;"
        )
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(12)

        lbl_method_badge = QLabel("GET")
        lbl_method_badge.setStyleSheet(
            "background-color: #7C3AED; color: #FFFFFF; font-weight: bold; font-family: monospace; font-size: 11px; border-radius: 4px; padding: 3px 8px;"
        )
        self.lbl_target = QLabel("http://testphp.vulnweb.com/listproducts.php?cat=1")
        self.lbl_target.setStyleSheet("font-size: 13px; font-weight: bold; color: #F8FAFC; font-family: monospace;")

        lbl_scope_badge = QLabel("In Scope")
        lbl_scope_badge.setStyleSheet(
            "background-color: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: bold;"
        )

        h_layout.addWidget(lbl_method_badge)
        h_layout.addWidget(self.lbl_target)
        h_layout.addWidget(lbl_scope_badge)
        h_layout.addStretch()

        self.lbl_status = QLabel("Status: RUNNING")
        self.lbl_status.setStyleSheet("font-size: 12px; font-weight: bold; color: #C084FC;")
        h_layout.addWidget(self.lbl_status)

        self.btn_cancel = QPushButton("⏹ Stop Assessment")
        self.btn_cancel.setStyleSheet(
            "background-color: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 6px; padding: 6px 14px; font-size: 11px; font-weight: bold;"
        )
        self.btn_cancel.clicked.connect(self.cancel_current_scan)

        self.btn_view_findings = QPushButton("Findings (2)")
        self.btn_view_findings.setStyleSheet(
            "background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; font-size: 11px; font-weight: 600;"
        )
        self.btn_view_findings.clicked.connect(lambda: self.main_window.navigate_to("findings"))

        h_layout.addWidget(self.btn_cancel)
        h_layout.addWidget(self.btn_view_findings)
        layout.addWidget(header_card)

        # =========================================================================
        # 2. STAGE EXECUTION PROGRESS STEPPER (6 Stages)
        # =========================================================================
        stepper_card = QFrame()
        stepper_card.setStyleSheet(
            "background-color: #111827; border: 1px solid #1E293B; border-radius: 10px; padding: 12px 16px;"
        )
        stepper_layout = QVBoxLayout(stepper_card)
        stepper_layout.setSpacing(10)

        step_hdr = QHBoxLayout()
        lbl_pipeline_title = QLabel("⚙ Assessment Execution Pipeline")
        lbl_pipeline_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #F8FAFC;")
        lbl_threads = QLabel("Thread Pool: 8/8 · Level 2 · Risk 2  ·  Target Response Ratio: 99.4% OK")
        lbl_threads.setStyleSheet("font-size: 11px; color: #94A3B8; font-family: monospace;")
        step_hdr.addWidget(lbl_pipeline_title)
        step_hdr.addStretch()
        step_hdr.addWidget(lbl_threads)
        stepper_layout.addLayout(step_hdr)

        # Stepper Row (6 Stages)
        self.stage_boxes: list[QFrame] = []
        stages_data = [
            ("1. INIT", "INITIALIZATION", True),
            ("2. PROBE", "TARGET_PROBE", True),
            ("3. FP", "FINGERPRINTING", True),
            ("4. DETECTION", "DETECTION (68%)", False),  # active
            ("5. EXPLOIT", "EXPLOITATION", False),
            ("6. CLEANUP", "CLEANUP", False),
        ]

        stages_row = QHBoxLayout()
        stages_row.setSpacing(8)

        for tag, title, done in stages_data:
            box = QFrame()
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(8, 6, 8, 6)
            box_layout.setSpacing(2)

            lbl_t = QLabel(tag)
            lbl_t.setStyleSheet("font-size: 10px; font-family: monospace; font-weight: bold; color: #94A3B8;")
            lbl_name = QLabel(title)
            lbl_name.setStyleSheet("font-size: 11px; font-weight: 600; color: #F8FAFC;")

            if done:
                box.setStyleSheet(
                    "background-color: #0F172A; border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 6px;"
                )
                lbl_t.setStyleSheet("font-size: 10px; font-family: monospace; color: #34D399;")
            elif "DETECTION" in tag or "68%" in title:
                box.setStyleSheet(
                    "background-color: rgba(124, 58, 237, 0.2); border: 1px solid #8B5CF6; border-radius: 6px;"
                )
                lbl_t.setStyleSheet("font-size: 10px; font-family: monospace; color: #C084FC; font-weight: bold;")
                lbl_name.setStyleSheet("font-size: 11px; font-weight: bold; color: #EDE9FE;")
            else:
                box.setStyleSheet(
                    "background-color: #0F172A; border: 1px solid #1E293B; border-radius: 6px; opacity: 0.5;"
                )
                lbl_t.setStyleSheet("font-size: 10px; font-family: monospace; color: #64748B;")
                lbl_name.setStyleSheet("font-size: 11px; color: #64748B;")

            box_layout.addWidget(lbl_t)
            box_layout.addWidget(lbl_name)
            stages_row.addWidget(box)
            self.stage_boxes.append(box)

        stepper_layout.addLayout(stages_row)

        # Smooth Master Progress Bar
        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(68)
        self.prog_bar.setFixedHeight(8)
        self.prog_bar.setTextVisible(False)
        self.prog_bar.setStyleSheet(
            """
            QProgressBar {
                background-color: #050811;
                border: 1px solid #1E293B;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7C3AED, stop:0.5 #A855F7, stop:1 #38BDF8);
                border-radius: 4px;
            }
            """
        )
        stepper_layout.addWidget(self.prog_bar)
        layout.addWidget(stepper_card)

        # =========================================================================
        # 3. LIVE TELEMETRY METRICS ROW (5 Cards)
        # =========================================================================
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(10)

        self.kpi_stage = KPICard("Current Technique", "Boolean & Error-based", "[B] Blind  ·  [E] Error  ·  [T] Time")
        self.kpi_progress = KPICard("Requests Sent", "342", "42 req/s  ·  Bandwidth: 1.48 MB")
        self.kpi_findings = KPICard("Active Parameter", "cat  [QUERY]", "Target Param 1/3  ·  Injection Focus")
        self.kpi_dbms = KPICard("DBMS Identified", "PostgreSQL 15.3", "Confidence: 99.8% (Exact)")
        self.kpi_latency = KPICard("Network Latency", "32ms", "HTTP 200/500: 339 / 3")

        kpi_row.addWidget(self.kpi_stage)
        kpi_row.addWidget(self.kpi_progress)
        kpi_row.addWidget(self.kpi_findings)
        kpi_row.addWidget(self.kpi_dbms)
        kpi_row.addWidget(self.kpi_latency)
        layout.addLayout(kpi_row)

        # =========================================================================
        # 4. CENTER MAIN SECTION (Terminal Stream 7 cols + Confirmed Vectors 5 cols)
        # =========================================================================
        center_splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- LEFT PANE (Col 7): Live Terminal Console ---
        term_card = QFrame()
        term_card.setStyleSheet(
            "background-color: #111827; border: 1px solid #1E293B; border-radius: 10px; padding: 0px;"
        )
        term_layout = QVBoxLayout(term_card)
        term_layout.setContentsMargins(0, 0, 0, 0)
        term_layout.setSpacing(0)

        # macOS style window header
        term_hdr = QFrame()
        term_hdr.setStyleSheet(
            "background-color: #1E293B; border-bottom: 1px solid #334155; border-top-left-radius: 10px; border-top-right-radius: 10px; padding: 8px 14px;"
        )
        term_hdr_layout = QHBoxLayout(term_hdr)
        term_hdr_layout.setContentsMargins(0, 0, 0, 0)
        term_hdr_layout.setSpacing(8)

        lbl_dots = QLabel("🔴 🟡 🟢")
        lbl_dots.setStyleSheet("font-size: 10px;")
        lbl_term_title = QLabel("sqlmap Heuristic Engine v4.2.0 Output")
        lbl_term_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #F8FAFC; font-family: monospace;")

        lbl_autoscroll = QLabel("● Auto-scroll: ON")
        lbl_autoscroll.setStyleSheet("font-size: 10px; color: #34D399; font-family: monospace; font-weight: bold;")

        term_hdr_layout.addWidget(lbl_dots)
        term_hdr_layout.addWidget(lbl_term_title)
        term_hdr_layout.addStretch()
        term_hdr_layout.addWidget(lbl_autoscroll)
        term_layout.addWidget(term_hdr)

        self.terminal = TerminalWidget()
        self.terminal.setMinimumHeight(280)
        term_layout.addWidget(self.terminal)

        # Terminal Control Bar
        term_controls = QFrame()
        term_controls.setStyleSheet(
            "background-color: #0F172A; border-top: 1px solid #1E293B; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; padding: 6px 12px;"
        )
        term_ctl_layout = QHBoxLayout(term_controls)
        term_ctl_layout.setContentsMargins(0, 0, 0, 0)
        term_ctl_layout.setSpacing(8)

        self.search_filter = QLineEdit()
        self.search_filter.setPlaceholderText("Filter console logs (regex supported)...")
        self.search_filter.setStyleSheet(
            "background-color: #050811; border: 1px solid #1E293B; border-radius: 4px; padding: 4px 8px; font-size: 11px; color: #F8FAFC;"
        )
        btn_copy = QPushButton("Copy Payloads")
        btn_copy.setStyleSheet(
            "background-color: #1E293B; color: #CBD5E1; border: 1px solid #334155; border-radius: 4px; padding: 4px 10px; font-size: 11px;"
        )
        btn_clear = QPushButton("Clear")
        btn_clear.setStyleSheet(
            "background-color: #1E293B; color: #94A3B8; border: 1px solid #334155; border-radius: 4px; padding: 4px 10px; font-size: 11px;"
        )
        btn_clear.clicked.connect(self.terminal.clear)

        term_ctl_layout.addWidget(self.search_filter)
        term_ctl_layout.addWidget(btn_copy)
        term_ctl_layout.addWidget(btn_clear)
        term_layout.addWidget(term_controls)

        center_splitter.addWidget(term_card)

        # --- RIGHT PANE (Col 5): Confirmed Injection Vectors Feed ---
        vectors_card = QFrame()
        vectors_card.setStyleSheet(
            "background-color: #111827; border: 1px solid #1E293B; border-radius: 10px; padding: 14px;"
        )
        vec_layout = QVBoxLayout(vectors_card)
        vec_layout.setSpacing(10)

        vec_hdr = QHBoxLayout()
        lbl_vec_title = QLabel("Confirmed Injection Vectors (2)")
        lbl_vec_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #F8FAFC;")
        lbl_feed_badge = QLabel("● REAL-TIME FEED")
        lbl_feed_badge.setStyleSheet(
            "font-size: 10px; font-family: monospace; font-weight: bold; color: #EF4444; background-color: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 4px; padding: 2px 6px;"
        )
        vec_hdr.addWidget(lbl_vec_title)
        vec_hdr.addStretch()
        vec_hdr.addWidget(lbl_feed_badge)
        vec_layout.addLayout(vec_hdr)

        # Vector Card 1: Critical Error-based
        vcard1 = QFrame()
        vcard1.setStyleSheet(
            "background-color: #0F172A; border: 1px solid rgba(239, 68, 68, 0.4); border-left: 4px solid #EF4444; border-radius: 6px; padding: 10px;"
        )
        vc1_layout = QVBoxLayout(vcard1)
        vc1_layout.setSpacing(4)

        vc1_top = QHBoxLayout()
        lbl_c1_sev = QLabel("CRITICAL")
        lbl_c1_sev.setStyleSheet(
            "background-color: rgba(239, 68, 68, 0.25); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.5); border-radius: 4px; padding: 2px 6px; font-size: 10px; font-weight: bold; font-family: monospace;"
        )
        lbl_c1_name = QLabel("Error-based SQL Injection")
        lbl_c1_name.setStyleSheet("font-size: 12px; font-weight: bold; color: #F8FAFC;")
        vc1_top.addWidget(lbl_c1_sev)
        vc1_top.addWidget(lbl_c1_name)
        vc1_top.addStretch()
        lbl_c1_param = QLabel("Param: cat [GET]")
        lbl_c1_param.setStyleSheet("font-size: 11px; color: #A855F7; font-family: monospace; font-weight: bold;")
        vc1_top.addWidget(lbl_c1_param)
        vc1_layout.addLayout(vc1_top)

        lbl_c1_desc = QLabel(
            "PostgreSQL error disclosure allows arbitrary query exfiltration via syntax-induced CAST conversion failure."
        )
        lbl_c1_desc.setStyleSheet("font-size: 11px; color: #94A3B8;")
        lbl_c1_desc.setWordWrap(True)
        vc1_layout.addWidget(lbl_c1_desc)

        lbl_c1_proof = QLabel("cat=1' AND CAST((SELECT version()) AS int)--")
        lbl_c1_proof.setStyleSheet(
            "background-color: #050811; color: #C084FC; font-family: monospace; font-size: 10px; border: 1px solid #1E293B; border-radius: 4px; padding: 4px 6px;"
        )
        vc1_layout.addWidget(lbl_c1_proof)

        vc1_bot = QHBoxLayout()
        lbl_c1_cvss = QLabel("CVSS 9.8 · CWE-89")
        lbl_c1_cvss.setStyleSheet("font-size: 10px; color: #64748B; font-family: monospace;")
        btn_c1_proof = QPushButton("⚡ Exploit Proof")
        btn_c1_proof.setStyleSheet(
            "background-color: #7C3AED; color: #FFFFFF; border-radius: 4px; padding: 3px 8px; font-size: 10px; font-weight: bold;"
        )
        btn_c1_proof.clicked.connect(lambda: self.main_window.navigate_to("findings"))
        vc1_bot.addWidget(lbl_c1_cvss)
        vc1_bot.addStretch()
        vc1_bot.addWidget(btn_c1_proof)
        vc1_layout.addLayout(vc1_bot)

        vec_layout.addWidget(vcard1)

        # Vector Card 2: High Boolean Blind
        vcard2 = QFrame()
        vcard2.setStyleSheet(
            "background-color: #0F172A; border: 1px solid rgba(245, 158, 11, 0.4); border-left: 4px solid #F59E0B; border-radius: 6px; padding: 10px;"
        )
        vc2_layout = QVBoxLayout(vcard2)
        vc2_layout.setSpacing(4)

        vc2_top = QHBoxLayout()
        lbl_c2_sev = QLabel("HIGH")
        lbl_c2_sev.setStyleSheet(
            "background-color: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 4px; padding: 2px 6px; font-size: 10px; font-weight: bold; font-family: monospace;"
        )
        lbl_c2_name = QLabel("Boolean-based Blind Injection")
        lbl_c2_name.setStyleSheet("font-size: 12px; font-weight: bold; color: #F8FAFC;")
        vc2_top.addWidget(lbl_c2_sev)
        vc2_top.addWidget(lbl_c2_name)
        vc2_top.addStretch()
        lbl_c2_param = QLabel("Param: cat [GET]")
        lbl_c2_param.setStyleSheet("font-size: 11px; color: #A855F7; font-family: monospace; font-weight: bold;")
        vc2_top.addWidget(lbl_c2_param)
        vc2_layout.addLayout(vc2_top)

        lbl_c2_desc = QLabel(
            "Reliable predicate inference verified through conditional truth differential. Statistical confidence ratio 99.8%."
        )
        lbl_c2_desc.setStyleSheet("font-size: 11px; color: #94A3B8;")
        lbl_c2_desc.setWordWrap(True)
        vc2_layout.addWidget(lbl_c2_desc)

        lbl_c2_meta = QLabel("Level: 2 · Risk: 2 · Confirmed")
        lbl_c2_meta.setStyleSheet("font-size: 10px; color: #64748B; font-family: monospace;")
        vc2_layout.addWidget(lbl_c2_meta)

        vec_layout.addWidget(vcard2)

        # Active Tampers strip
        tamper_strip = QFrame()
        tamper_strip.setStyleSheet(
            "background-color: #050811; border: 1px solid #1E293B; border-radius: 6px; padding: 6px 10px;"
        )
        ts_layout = QHBoxLayout(tamper_strip)
        ts_layout.setContentsMargins(0, 0, 0, 0)
        ts_layout.setSpacing(6)
        lbl_ts = QLabel("Active Tampers:")
        lbl_ts.setStyleSheet("font-size: 10px; color: #94A3B8; font-family: monospace;")
        lbl_t1 = QLabel("space2comment")
        lbl_t1.setStyleSheet(
            "background-color: #1E293B; color: #C084FC; font-size: 10px; font-family: monospace; border-radius: 3px; padding: 2px 6px;"
        )
        lbl_t2 = QLabel("randomcase")
        lbl_t2.setStyleSheet(
            "background-color: #1E293B; color: #C084FC; font-size: 10px; font-family: monospace; border-radius: 3px; padding: 2px 6px;"
        )
        ts_layout.addWidget(lbl_ts)
        ts_layout.addWidget(lbl_t1)
        ts_layout.addWidget(lbl_t2)
        ts_layout.addStretch()
        vec_layout.addWidget(tamper_strip)

        center_splitter.addWidget(vectors_card)
        center_splitter.setSizes([720, 500])
        layout.addWidget(center_splitter)

        # =========================================================================
        # 5. BOTTOM PACKET INSPECTOR DRAWER (Request & Response Split)
        # =========================================================================
        packet_card = QFrame()
        packet_card.setStyleSheet(
            "background-color: #111827; border: 1px solid #1E293B; border-radius: 10px; padding: 10px 14px;"
        )
        p_layout = QVBoxLayout(packet_card)
        p_layout.setContentsMargins(0, 0, 0, 0)
        p_layout.setSpacing(6)

        p_hdr = QHBoxLayout()
        lbl_pkt_title = QLabel("⇄ Packet Inspector")
        lbl_pkt_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #F8FAFC;")
        lbl_req_badge = QLabel("Request #342 [ACTIVE]")
        lbl_req_badge.setStyleSheet(
            "background-color: rgba(124, 58, 237, 0.2); color: #C084FC; border: 1px solid rgba(124, 58, 237, 0.4); border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: bold; font-family: monospace;"
        )
        lbl_res_badge = QLabel("Response #342 [200 OK]")
        lbl_res_badge.setStyleSheet(
            "background-color: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: bold; font-family: monospace;"
        )
        lbl_hash = QLabel("Payload Hash: 0x8a92f0c1")
        lbl_hash.setStyleSheet("font-size: 10px; color: #64748B; font-family: monospace;")

        btn_send_editor = QPushButton("Send to Request Editor →")
        btn_send_editor.setStyleSheet(
            "background-color: #1E293B; color: #C084FC; border: 1px solid #334155; border-radius: 4px; padding: 3px 10px; font-size: 11px;"
        )
        btn_send_editor.clicked.connect(lambda: self.main_window.navigate_to("request"))

        p_hdr.addWidget(lbl_pkt_title)
        p_hdr.addWidget(lbl_req_badge)
        p_hdr.addWidget(lbl_res_badge)
        p_hdr.addStretch()
        p_hdr.addWidget(lbl_hash)
        p_hdr.addWidget(btn_send_editor)
        p_layout.addLayout(p_hdr)

        # Split Request & Response texts
        split_packets = QHBoxLayout()
        split_packets.setSpacing(10)

        self.txt_req_packet = QPlainTextEdit()
        self.txt_req_packet.setReadOnly(True)
        self.txt_req_packet.setMaximumHeight(100)
        self.txt_req_packet.setStyleSheet(
            "background-color: #050811; color: #CBD5E1; font-family: monospace; font-size: 10px; border: 1px solid #1E293B; border-radius: 4px;"
        )
        self.txt_req_packet.setPlainText(
            "GET /listproducts.php?cat=1%20AND%208821=8821%20--%20- HTTP/1.1\n"
            "Host: testphp.vulnweb.com\n"
            "User-Agent: SQLPhantom/4.2.0 (Automated Pentest Engine; x86_64)\n"
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\n"
            "Connection: keep-alive"
        )

        self.txt_res_packet = QPlainTextEdit()
        self.txt_res_packet.setReadOnly(True)
        self.txt_res_packet.setMaximumHeight(100)
        self.txt_res_packet.setStyleSheet(
            "background-color: #050811; color: #34D399; font-family: monospace; font-size: 10px; border: 1px solid #1E293B; border-radius: 4px;"
        )
        self.txt_res_packet.setPlainText(
            "HTTP/1.1 200 OK\n"
            "Server: nginx/1.19.0\n"
            "Content-Type: text/html; charset=UTF-8\n"
            "Content-Length: 4821\n"
            "<div class='catalog-title'>Category: Printers & Supplies</div>\n"
            "<span class='prod-desc'>Found 12 items matching predicate TRUE</span>"
        )

        split_packets.addWidget(self.txt_req_packet)
        split_packets.addWidget(self.txt_res_packet)
        p_layout.addLayout(split_packets)

        layout.addWidget(packet_card)

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)

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
            self.lbl_target.setText("http://testphp.vulnweb.com/listproducts.php?cat=1")
            self.lbl_status.setText("Status: IDLE")
            self.terminal.append_info("Workstation ready. Launch an assessment to observe live payloads.")
            return

        status = self.main_window.assessment_service.get_status(job_id)
        context = self.main_window.job_manager.get_context(job_id)
        url = context.config.target.url if context else "http://testphp.vulnweb.com/listproducts.php?cat=1"

        self.lbl_target.setText(url)
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
            self.kpi_dbms.update_value("PostgreSQL 15.3")

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
