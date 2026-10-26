"""
SQLPhantom Textual Terminal User Interface Application.
"""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Button, Footer, Header

from sqlphantom import __product__, __tagline__, __version__
from sqlphantom.application.event_bus import EventBus
from sqlphantom.application.job_manager import JobManager
from sqlphantom.application.services import AssessmentService, ProjectService, ReportService
from sqlphantom.domain.models import AssessmentConfig, Project, ScopeRule, Target
from sqlphantom.engine.mock_adapter import MockEngineAdapter
from sqlphantom.storage.database import DatabaseManager
from sqlphantom.storage.repositories import FindingRepository, ProjectRepository, SessionRepository
from sqlphantom.tui.screens.assessment_wizard import AssessmentWizardScreen
from sqlphantom.tui.screens.dashboard import DashboardScreen
from sqlphantom.tui.screens.findings import FindingsScreen
from sqlphantom.tui.screens.help import HelpScreen
from sqlphantom.tui.screens.live_monitor import LiveMonitorScreen
from sqlphantom.tui.theme import SQLPHANTOM_CSS


class SQLPhantomApp(App):
    """
    SQLPhantom Interactive Terminal Workstation.
    Full-featured terminal UI providing assessment configuration,
    live execution telemetry, findings inspection, and report export.
    """

    TITLE = f"{__product__} · Enhanced sqlmap"
    SUB_TITLE = f"{__tagline__} (v{__version__})"
    CSS = SQLPHANTOM_CSS

    BINDINGS = [
        Binding("d", "nav('dashboard')", "Dashboard", priority=True),
        Binding("n", "nav('wizard')", "New Assessment", priority=True),
        Binding("m", "nav('monitor')", "Live Monitor", priority=True),
        Binding("f", "nav('findings')", "Findings", priority=True),
        Binding("r", "quick_scan", "Fast Scan", priority=True),
        Binding("question_mark", "nav('help')", "Help", priority=True),
        Binding("q", "quit", "Quit", priority=True),
    ]

    def __init__(
        self,
        db_path: str | Path = ":memory:",
        stage_duration: float = 0.4,
        **kwargs,
    ):
        super().__init__(**kwargs)
        # Core Foundation Services
        self.db_manager = DatabaseManager(db_path)
        self.project_repo = ProjectRepository(self.db_manager)
        self.finding_repo = FindingRepository(self.db_manager)
        self.session_repo = SessionRepository(self.db_manager)

        self.event_bus = EventBus(async_dispatch=True)
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
        self._current_screen_id = "dashboard"

        # Initialize default project and target
        self._seed_default_workspace()

    def _seed_default_workspace(self) -> None:
        projects = self.project_service.list_projects()
        if not projects:
            p = self.project_service.create_project(
                name="Security Audit Lab",
                description="Default authorized testing workspace",
            )
            target = Target(url="http://testphp.vulnweb.com/listproducts.php?cat=1")
            self.project_service.add_target(p.id, target)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="nav-bar"):
            yield Button("Dashboard [d]", id="nav-dashboard", classes="nav-btn -active")
            yield Button("New Scan [n]", id="nav-wizard", classes="nav-btn")
            yield Button("Live Monitor [m]", id="nav-monitor", classes="nav-btn")
            yield Button("Findings [f]", id="nav-findings", classes="nav-btn")
            yield Button("Help [?]", id="nav-help", classes="nav-btn")

        with Container(id="workspace-container"):
            yield DashboardScreen(id="screen-dashboard")

        yield Footer()

    def action_nav(self, screen_name: str) -> None:
        self.switch_screen(screen_name)

    def switch_screen(self, screen_name: str) -> None:
        """Switch the main workspace view to the requested screen."""
        self._current_screen_id = screen_name

        # Update navigation buttons
        for btn_id, target in [
            ("nav-dashboard", "dashboard"),
            ("nav-wizard", "wizard"),
            ("nav-monitor", "monitor"),
            ("nav-findings", "findings"),
            ("nav-help", "help"),
        ]:
            try:
                btn = self.query_one(f"#{btn_id}", Button)
                if target == screen_name:
                    btn.add_class("-active")
                else:
                    btn.remove_class("-active")
            except Exception:
                pass

        container = self.query_one("#workspace-container", Container)
        container.remove_children()

        if screen_name == "dashboard":
            container.mount(DashboardScreen(id="screen-dashboard"))
        elif screen_name == "wizard":
            container.mount(AssessmentWizardScreen(id="screen-wizard"))
        elif screen_name == "monitor":
            container.mount(LiveMonitorScreen(id="screen-monitor"))
        elif screen_name == "findings":
            container.mount(FindingsScreen(id="screen-findings"))
        elif screen_name == "help":
            container.mount(HelpScreen(id="screen-help"))

    def action_quick_scan(self) -> None:
        """Trigger an instant simulated test scan."""
        target = Target(url="http://testphp.vulnweb.com/listproducts.php?cat=1")
        scope = ScopeRule(allowed_domains=["vulnweb.com"], block_private_ips=True)
        config = AssessmentConfig(target=target, scope=scope, level=2, risk=1)

        job_id = self.assessment_service.create_assessment(config)
        self.assessment_service.start_assessment(job_id)
        self.active_job_id = job_id
        self.switch_screen("monitor")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "nav-dashboard":
            self.switch_screen("dashboard")
        elif btn_id == "nav-wizard" or btn_id == "btn-quick-wizard":
            self.switch_screen("wizard")
        elif btn_id == "nav-monitor":
            self.switch_screen("monitor")
        elif btn_id == "nav-findings" or btn_id == "btn-quick-findings":
            self.switch_screen("findings")
        elif btn_id == "nav-help":
            self.switch_screen("help")
        elif btn_id == "btn-quick-scan":
            self.action_quick_scan()
