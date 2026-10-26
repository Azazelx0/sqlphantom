"""
SQLPhantom PySide6 Desktop GUI Main Window.
Aligns with Stitch design specs including top app command bar and cybernetic dark aesthetics.
"""

from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from sqlphantom import __product__, __tagline__, __version__
from sqlphantom.application.event_bus import EventBus
from sqlphantom.application.job_manager import JobManager
from sqlphantom.application.services import AssessmentService, ProjectService, ReportService
from sqlphantom.domain.models import AssessmentConfig, Project, ScopeRule, Target
from sqlphantom.engine.mock_adapter import MockEngineAdapter
from sqlphantom.gui.screens.about_dialog import AboutDialog
from sqlphantom.gui.screens.assessment_wizard import AssessmentWizardScreen
from sqlphantom.gui.screens.dashboard import DashboardScreen
from sqlphantom.gui.screens.findings_viewer import FindingsViewerScreen
from sqlphantom.gui.screens.live_monitor import LiveMonitorScreen
from sqlphantom.gui.screens.request_editor import RequestEditorScreen
from sqlphantom.gui.screens.schema_viewer import SchemaViewerScreen
from sqlphantom.gui.screens.sessions_view import SessionsScreen
from sqlphantom.gui.signals import EventSignalBridge
from sqlphantom.storage.database import DatabaseManager
from sqlphantom.storage.repositories import FindingRepository, ProjectRepository, SessionRepository


class MainWindow(QMainWindow):
    """
    Primary desktop application workstation window titled 'SQLPhantom — sqlmap Enhanced'.
    Features persistent left sidebar navigation, top command bar, and dynamic stacked screen views.
    """

    def __init__(
        self,
        db_path: str | Path = ":memory:",
        stage_duration: float = 0.4,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("SQLPhantom — sqlmap Enhanced")
        self.resize(1340, 840)

        logo_path = Path(__file__).resolve().parent / "assets" / "logo.png"
        if not logo_path.exists():
            logo_path = Path("assets/logo.png")
        if logo_path.exists():
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(str(logo_path)))

        # Initialize Application Services
        self.db_manager = DatabaseManager(db_path)
        self.project_repo = ProjectRepository(self.db_manager)
        self.finding_repo = FindingRepository(self.db_manager)
        self.session_repo = SessionRepository(self.db_manager)

        self.event_bus = EventBus(async_dispatch=True)
        self.signal_bridge = EventSignalBridge(self.event_bus)
        self.engine_adapter = MockEngineAdapter(stage_duration=stage_duration)
        self.job_manager = JobManager(
            event_bus=self.event_bus,
            engine=self.engine_adapter,
            poll_interval=0.05,
        )

        self.project_service = ProjectService(repository=self.project_repo)
        self.assessment_service = AssessmentService(job_manager=self.job_manager)
        self.report_service = ReportService()

        self.active_job_id: str | None = None
        self._nav_buttons: dict[str, QPushButton] = {}
        self.current_theme: str = "dark"

        # Default Workspace Seed
        self._seed_default_workspace()

        # Layout Setup
        self._init_ui()
        self._connect_lifecycle_signals()

    def _seed_default_workspace(self) -> None:
        projects = self.project_service.list_projects()
        if not projects:
            p = self.project_service.create_project(
                name="Security Audit Lab",
                description="Default authorized testing workspace",
            )
            target = Target(url="http://testphp.vulnweb.com/listproducts.php?cat=1")
            self.project_service.add_target(p.id, target)

    def _init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Navigation Sidebar (Stitch Design: SideNavBar)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar-panel")
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(10, 14, 10, 14)
        side_layout.setSpacing(6)

        # Top Brand & Workspace Header
        brand_card = QFrame()
        brand_card.setStyleSheet(
            "background-color: rgba(17, 24, 39, 0.7); border: 1px solid rgba(51, 65, 85, 0.6); border-radius: 8px; padding: 6px;"
        )
        brand_layout = QHBoxLayout(brand_card)
        brand_layout.setContentsMargins(4, 4, 4, 4)
        brand_layout.setSpacing(8)

        logo_path = Path(__file__).resolve().parent / "assets" / "logo.png"
        if not logo_path.exists():
            logo_path = Path("assets/logo.png")
        if logo_path.exists():
            from PySide6.QtGui import QPixmap
            logo_lbl = QLabel()
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pix = QPixmap(str(logo_path)).scaled(
                32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(pix)
            brand_layout.addWidget(logo_lbl)

        brand_text_box = QVBoxLayout()
        brand_text_box.setSpacing(1)
        brand_title = QLabel(__product__)
        brand_title.setStyleSheet("font-size: 14px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.5px;")
        brand_sub = QLabel(f"{__version__} · sqlmap Enhanced")
        brand_sub.setStyleSheet("font-size: 10px; color: #94A3B8;")
        brand_text_box.addWidget(brand_title)
        brand_text_box.addWidget(brand_sub)
        brand_layout.addLayout(brand_text_box)
        brand_layout.addStretch()
        side_layout.addWidget(brand_card)

        # Primary Quick Action CTA
        btn_quick_new = QPushButton("  + New Assessment")
        btn_quick_new.setStyleSheet(
            "background-color: #7C3AED; color: #FFFFFF; font-weight: bold; border-radius: 6px; padding: 8px; font-size: 12px;"
        )
        btn_quick_new.clicked.connect(lambda: self.navigate_to("wizard"))
        side_layout.addWidget(btn_quick_new)

        # Navigation Links
        nav_items = [
            ("dashboard", "Dashboard"),
            ("wizard", "New Assessment"),
            ("request", "Request Editor"),
            ("monitor", "Live Monitor"),
            ("findings", "Findings"),
            ("schema", "Schema Explorer"),
            ("sessions", "Sessions & History"),
        ]

        for key, label in nav_items:
            btn = QPushButton(f"  {label}")
            btn.setProperty("class", "nav-button")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, k=key: self.navigate_to(k))
            self._nav_buttons[key] = btn
            side_layout.addWidget(btn)

        side_layout.addStretch()

        btn_theme = QPushButton("  🌓 Toggle Theme")
        btn_theme.setProperty("class", "nav-button")
        btn_theme.clicked.connect(self.toggle_theme)
        side_layout.addWidget(btn_theme)

        btn_about = QPushButton("  About SQLPhantom")
        btn_about.setProperty("class", "nav-button")
        btn_about.clicked.connect(self.show_about_dialog)
        side_layout.addWidget(btn_about)

        # Sidebar Footer: Engine IPC State
        engine_box = QFrame()
        engine_box.setStyleSheet(
            "background-color: rgba(5, 8, 17, 0.8); border: 1px solid #1E293B; border-radius: 6px; padding: 6px 10px;"
        )
        engine_box_layout = QHBoxLayout(engine_box)
        engine_box_layout.setContentsMargins(0, 0, 0, 0)
        lbl_ipc = QLabel("● sqlmap API :8775")
        lbl_ipc.setStyleSheet("font-size: 10px; color: #34D399; font-family: monospace; font-weight: bold;")
        lbl_online = QLabel("ONLINE")
        lbl_online.setStyleSheet("font-size: 10px; color: #10B981; font-weight: bold;")
        engine_box_layout.addWidget(lbl_ipc)
        engine_box_layout.addStretch()
        engine_box_layout.addWidget(lbl_online)
        side_layout.addWidget(engine_box)

        main_layout.addWidget(sidebar)

        # 2. Right Workspace (Top App Bar + Stacked Screens)
        workspace = QWidget()
        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)

        # Top Command Bar (Stitch Design: TopNavBar)
        top_bar = QFrame()
        top_bar.setObjectName("top-app-bar")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(16, 6, 16, 6)
        top_bar_layout.setSpacing(12)

        # Left: Quick Target Input
        self.quick_target_input = QLineEdit()
        self.quick_target_input.setObjectName("target-quick-input")
        self.quick_target_input.setPlaceholderText(
            "Quick Target URL (e.g. http://testphp.vulnweb.com/listproducts.php?cat=1)"
        )
        self.quick_target_input.setText("http://testphp.vulnweb.com/listproducts.php?cat=1")
        self.quick_target_input.setMinimumWidth(380)

        self.btn_top_launch = QPushButton("🚀 Launch Scan")
        self.btn_top_launch.setStyleSheet(
            "background-color: #7C3AED; color: #FFFFFF; font-weight: 600; padding: 6px 14px; border-radius: 6px; font-size: 12px;"
        )
        self.btn_top_launch.clicked.connect(lambda: self.launch_quick_scan())

        top_bar_layout.addWidget(self.quick_target_input)
        top_bar_layout.addWidget(self.btn_top_launch)

        lbl_engines = QLabel("Engines  |  Payloads  |  Proxies")
        lbl_engines.setStyleSheet("font-size: 11px; color: #64748B; font-weight: 600; padding-left: 8px;")
        top_bar_layout.addWidget(lbl_engines)

        top_bar_layout.addStretch()

        # Right: Workstation Status & Operator Controls
        self.lbl_engine_pill = QLabel("● Engine: Idle (Ready)")
        self.lbl_engine_pill.setProperty("class", "badge-pill-emerald")
        self.lbl_engine_pill.setStyleSheet(
            "background-color: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 3px 10px; font-size: 11px; font-weight: 600;"
        )

        self.lbl_jobs_pill = QLabel("0 Active Jobs")
        self.lbl_jobs_pill.setStyleSheet(
            "background-color: #1E293B; color: #94A3B8; border: 1px solid #334155; border-radius: 12px; padding: 3px 10px; font-size: 11px; font-family: monospace;"
        )

        self.btn_stop_all = QPushButton("⏹ Stop All")
        self.btn_stop_all.setStyleSheet(
            "background-color: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 4px 10px; font-size: 11px; font-weight: 600;"
        )
        self.btn_stop_all.clicked.connect(self._stop_all_scans)

        operator_badge = QLabel("sec_operator_01 · ROOT")
        operator_badge.setStyleSheet(
            "background-color: rgba(124, 58, 237, 0.15); color: #C084FC; border: 1px solid rgba(124, 58, 237, 0.3); border-radius: 12px; padding: 3px 10px; font-size: 11px; font-weight: 600;"
        )

        top_bar_layout.addWidget(self.lbl_engine_pill)
        top_bar_layout.addWidget(self.lbl_jobs_pill)
        top_bar_layout.addWidget(self.btn_stop_all)
        top_bar_layout.addWidget(operator_badge)

        workspace_layout.addWidget(top_bar)

        # 3. Stacked Screens
        self.stack = QStackedWidget()
        self.screens: dict[str, QWidget] = {
            "dashboard": DashboardScreen(self),
            "wizard": AssessmentWizardScreen(self),
            "request": RequestEditorScreen(self),
            "monitor": LiveMonitorScreen(self),
            "findings": FindingsViewerScreen(self),
            "schema": SchemaViewerScreen(self),
            "sessions": SessionsScreen(self),
        }

        for screen in self.screens.values():
            self.stack.addWidget(screen)

        workspace_layout.addWidget(self.stack)
        main_layout.addWidget(workspace)

        self.navigate_to("dashboard")

    def _connect_lifecycle_signals(self) -> None:
        bridge = self.signal_bridge
        if bridge:
            bridge.job_started.connect(self._on_scan_started)
            bridge.job_completed.connect(self._on_scan_ended)
            bridge.job_cancelled.connect(lambda r: self._on_scan_ended())
            bridge.job_failed.connect(lambda e: self._on_scan_ended())

    def _on_scan_started(self, *args: Any) -> None:
        self.lbl_engine_pill.setText("● Engine: RUNNING (68%)")
        self.lbl_engine_pill.setStyleSheet(
            "background-color: rgba(124, 58, 237, 0.25); color: #C084FC; border: 1px solid rgba(124, 58, 237, 0.6); border-radius: 12px; padding: 3px 10px; font-size: 11px; font-weight: bold;"
        )
        self.lbl_jobs_pill.setText("1 Active Job")

    def _on_scan_ended(self, *args: Any) -> None:
        self.lbl_engine_pill.setText("● Engine: Idle (Ready)")
        self.lbl_engine_pill.setStyleSheet(
            "background-color: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 3px 10px; font-size: 11px; font-weight: 600;"
        )
        self.lbl_jobs_pill.setText("0 Active Jobs")

    def _stop_all_scans(self) -> None:
        if self.active_job_id:
            self.assessment_service.cancel_assessment(self.active_job_id)
            self._on_scan_ended()

    def navigate_to(self, screen_key: str) -> None:
        if screen_key in self.screens:
            for k, btn in self._nav_buttons.items():
                btn.setChecked(k == screen_key)

            screen = self.screens[screen_key]
            self.stack.setCurrentWidget(screen)

            if hasattr(screen, "refresh_data"):
                screen.refresh_data()
            elif hasattr(screen, "refresh_state"):
                screen.refresh_state()
            elif hasattr(screen, "refresh_findings"):
                screen.refresh_findings()
            elif hasattr(screen, "refresh_sessions"):
                screen.refresh_sessions()

    def launch_quick_scan(self, url: str | None = None) -> None:
        target_url = url
        if not target_url and hasattr(self, "quick_target_input"):
            target_url = self.quick_target_input.text().strip()
        if not target_url:
            target_url = "http://testphp.vulnweb.com/listproducts.php?cat=1"

        parsed = urlparse(target_url)
        domain = parsed.netloc or "vulnweb.com"
        target = Target(url=target_url)
        scope = ScopeRule(allowed_domains=[domain, "vulnweb.com"], block_private_ips=True)
        config = AssessmentConfig(target=target, scope=scope, level=2, risk=1)

        job_id = self.assessment_service.create_assessment(config)
        self.assessment_service.start_assessment(job_id)
        self.active_job_id = job_id
        self._on_scan_started()
        self.navigate_to("monitor")

    def show_about_dialog(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()

    def toggle_theme(self) -> None:
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        from sqlphantom.gui.theme import get_theme_stylesheet
        self.setStyleSheet(get_theme_stylesheet(self.current_theme))
