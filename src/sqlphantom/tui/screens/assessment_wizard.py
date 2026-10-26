"""
SQLPhantom TUI Assessment Setup Wizard screen.
"""

from typing import Any
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label, Static

from sqlphantom.domain.enums import HttpMethod
from sqlphantom.domain.models import AssessmentConfig, ScopeRule, Target
from sqlphantom.domain.scope import validate_target_in_scope


class AssessmentWizardScreen(Static):
    """
    Form-based wizard for configuring targets, boundary scopes, and injection parameters.
    """

    def compose(self) -> ComposeResult:
        with Vertical(classes="card-box"):
            yield Label("New Security Assessment Configuration", classes="card-title")

            yield Label("Target URL (HTTP/HTTPS):")
            yield Input(
                value="http://testphp.vulnweb.com/listproducts.php?cat=1",
                placeholder="http://example.com/item.php?id=1",
                id="input-url",
            )

            with Horizontal():
                with Vertical():
                    yield Label("HTTP Method:")
                    yield Input(value="GET", placeholder="GET, POST", id="input-method")

                with Vertical():
                    yield Label("Allowed Domains Scope (comma-separated):")
                    yield Input(
                        value="vulnweb.com",
                        placeholder="example.com, test.internal",
                        id="input-domains",
                    )

            with Horizontal():
                with Vertical():
                    yield Label("Testing Level (1-5):")
                    yield Input(value="2", placeholder="1-5", id="input-level")

                with Vertical():
                    yield Label("Risk Vector (1-3):")
                    yield Input(value="1", placeholder="1-3", id="input-risk")

            yield Label("", id="wizard-error-label", classes="kpi-title")

            with Horizontal():
                yield Button("Launch Assessment", id="btn-start-scan")
                yield Button("Cancel / Reset", id="btn-cancel-wizard", classes="btn-secondary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel-wizard":
            self.app.switch_screen("dashboard")
            return

        if event.button.id == "btn-start-scan":
            self.launch_assessment()

    def launch_assessment(self) -> None:
        err_label = self.query_one("#wizard-error-label", Label)
        err_label.update("")

        url = self.query_one("#input-url", Input).value.strip()
        method_str = self.query_one("#input-method", Input).value.strip().upper()
        domains_str = self.query_one("#input-domains", Input).value.strip()
        level_str = self.query_one("#input-level", Input).value.strip()
        risk_str = self.query_one("#input-risk", Input).value.strip()

        if not url:
            err_label.update("[red]Error: Target URL cannot be empty[/red]")
            return

        try:
            method = HttpMethod(method_str)
        except ValueError:
            err_label.update(f"[red]Error: Invalid HTTP method '{method_str}'[/red]")
            return

        try:
            level = int(level_str)
            risk = int(risk_str)
            if not (1 <= level <= 5 and 1 <= risk <= 3):
                raise ValueError()
        except ValueError:
            err_label.update("[red]Error: Level must be 1-5, Risk must be 1-3[/red]")
            return

        allowed_domains = [d.strip() for d in domains_str.split(",") if d.strip()]
        scope = ScopeRule(allowed_domains=allowed_domains, block_private_ips=True)
        target = Target(url=url, method=method)

        in_scope, reason = validate_target_in_scope(target, scope)
        if not in_scope:
            err_label.update(f"[red]Scope Rejected: {reason}[/red]")
            return

        config = AssessmentConfig(target=target, scope=scope, level=level, risk=risk)

        # Dispatch via AssessmentService
        try:
            app: Any = self.app
            job_id = app.assessment_service.create_assessment(config)
            app.assessment_service.start_assessment(job_id)
            app.active_job_id = job_id

            # Switch to live monitoring screen
            app.switch_screen("monitor")
        except Exception as exc:
            err_label.update(f"[red]Failed to launch job: {exc}[/red]")
