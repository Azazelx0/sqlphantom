"""
SQLPhantom TUI Dashboard screen.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Label, Static

from sqlphantom.tui.widgets.kpi_card import KPICard


class DashboardScreen(Static):
    """
    Main workstation dashboard presenting quick-start actions,
    system telemetry, and recent assessment targets.
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            # Welcome banner
            yield Label(
                "SQLPhantom · Penetration Testing Workstation (sqlmap Enhanced)",
                classes="card-title",
            )

            # KPI Telemetry Strip
            with Horizontal(classes="kpi-container"):
                yield KPICard("Projects", "1", "Active Workspaces", id="kpi-projects")
                yield KPICard("Active Workers", "0", "Ready for Dispatch", id="kpi-workers")
                yield KPICard("Findings", "0", "Vulnerabilities", id="kpi-findings")
                yield KPICard("Engine State", "IDLE", "sqlmap API Online", id="kpi-engine")

            # Quick Action Launchpad
            with Horizontal(classes="card-box"):
                yield Button("Launch Assessment Wizard", id="btn-quick-wizard")
                yield Button("Run Fast Test Scan", id="btn-quick-scan", classes="btn-secondary")
                yield Button("View Discovered Findings", id="btn-quick-findings", classes="btn-secondary")

            # Recent Targets and Audits
            with Vertical(classes="card-box"):
                yield Label("Registered Projects & Targets", classes="card-title")
                yield DataTable(id="dashboard-targets-table")

    def on_mount(self) -> None:
        table = self.query_one("#dashboard-targets-table", DataTable)
        table.add_columns("Project", "Target URL", "Method", "Scope Domain", "Status")
        self.refresh_data()

    def refresh_data(self) -> None:
        table = self.query_one("#dashboard-targets-table", DataTable)
        table.clear()

        app = self.app
        if hasattr(app, "project_service") and app.project_service:
            projects = app.project_service.list_projects()
            self.query_one("#kpi-projects", KPICard).update_value(str(len(projects)))

            total_findings = 0
            if hasattr(app, "finding_repo") and app.finding_repo:
                total_findings = len(app.finding_repo.list_all())
            self.query_one("#kpi-findings", KPICard).update_value(str(total_findings))

            for proj in projects:
                if not proj.targets:
                    table.add_row(proj.name, "(No targets configured)", "-", "-", "Ready")
                else:
                    for target in proj.targets:
                        table.add_row(
                            proj.name,
                            target.url,
                            str(target.method),
                            "In-Scope",
                            "Configured",
                        )
        else:
            table.add_row(
                "Default Lab",
                "http://testphp.vulnweb.com/listproducts.php?cat=1",
                "GET",
                "vulnweb.com",
                "Ready",
            )
