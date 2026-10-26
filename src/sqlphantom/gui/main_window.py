"""
SQLPhantom PySide6 Desktop GUI Main Window.
"""

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
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
    Features persistent left sidebar navigation and dynamic stacked screen views.
    """

    def __init__(
        self,
        db_path: str | Path = ":memory:",
        stage_duration: float = 0.4,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("SQLPhantom — sqlmap Enhanced")
        self.resize(1280, 800)

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

        # 1. Left Navigation Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar-panel")
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(6, 12, 6, 12)
        side_layout.setSpacing(4)

        logo_path = Path(__file__).resolve().parent / "assets" / "logo.png"
        if not logo_path.exists():
            logo_path = Path("assets/logo.png")
        if logo_path.exists():
            from PySide6.QtGui import QPixmap
            logo_lbl = QLabel()
            logo_lbl.setAlignment(Qt.AlignCenter)
            pix = QPixmap(str(logo_path)).scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            logo_lbl.setPixmap(pix)
            logo_lbl.setStyleSheet("padding: 6px 0px 0px 0px;")
            side_layout.addWidget(logo_lbl)

        brand_lbl = QLabel(__product__)
        brand_lbl.setAlignment(Qt.AlignCenter)
        brand_lbl.setObjectName("sidebar-brand")
        sub_lbl = QLabel(f"{__tagline__}")
        sub_lbl.setAlignment(Qt.AlignCenter)
        sub_lbl.setObjectName("sidebar-subtitle")
        side_layout.addWidget(brand_lbl)
        side_layout.addWidget(sub_lbl)

        # Nav Buttons
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

        status_lbl = QLabel("sqlmap API :8775 Online")
        status_lbl.setStyleSheet("font-size: 10px; color: #10B981; padding: 8px 12px;")
        side_layout.addWidget(status_lbl)

        main_layout.addWidget(sidebar)

        # 2. Main Workspace Screen Stack
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

        main_layout.addWidget(self.stack)
        self.navigate_to("dashboard")

    def navigate_to(self, screen_key: str) -> None:
        if screen_key in self.screens:
            # Update active nav button styling
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

    def launch_quick_scan(self) -> None:
        target = Target(url="http://testphp.vulnweb.com/listproducts.php?cat=1")
        scope = ScopeRule(allowed_domains=["vulnweb.com"], block_private_ips=True)
        config = AssessmentConfig(target=target, scope=scope, level=2, risk=1)

        job_id = self.assessment_service.create_assessment(config)
        self.assessment_service.start_assessment(job_id)
        self.active_job_id = job_id
        self.navigate_to("monitor")

    def show_about_dialog(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()

    def toggle_theme(self) -> None:
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        from sqlphantom.gui.theme import get_theme_stylesheet
        self.setStyleSheet(get_theme_stylesheet(self.current_theme))
