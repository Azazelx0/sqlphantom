"""
SQLPhantom TUI Help and Keyboard Reference screen.
"""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Label, Static

from sqlphantom import __product__, __tagline__, __upstream__, __upstream_commit__, __version__


class HelpScreen(Static):
    """
    Reference manual displaying navigation keybindings, product details,
    and security boundaries.
    """

    def compose(self) -> ComposeResult:
        with Vertical(classes="card-box"):
            yield Label(f"{__product__} v{__version__} — {__tagline__}", classes="card-title")
            yield Label(
                f"Modernized, interactive terminal workstation for authorized penetration testing.\n"
                f"Upstream: {__upstream__} (baseline {__upstream_commit__[:7]})\n",
                classes="kpi-title",
            )

            yield Label("Navigation Keyboard Shortcuts:", classes="card-title")
            yield DataTable(id="help-keys-table")

            yield Label("\nResponsible Security Testing Notice:", classes="card-title")
            yield Label(
                "SQLPhantom is strictly designed for authorized security assessments, laboratory testing, "
                "and educational research. All targets must be explicitly permitted within configured scope "
                "boundaries. RFC 1918 private IP protection is enabled by default to prevent unintended intranet probing.",
                classes="kpi-subtext",
            )

    def on_mount(self) -> None:
        table = self.query_one("#help-keys-table", DataTable)
        table.add_columns("Key", "Action", "Description")
        table.add_row("d", "Dashboard", "Return to main workstation dashboard")
        table.add_row("n", "New Assessment", "Open target and boundary scope setup wizard")
        table.add_row("m", "Live Monitor", "Inspect active scan telemetry and terminal event log")
        table.add_row("f", "Findings", "Review verified vulnerabilities and export reports")
        table.add_row("r", "Fast Mock Scan", "Quickly trigger a simulated test assessment")
        table.add_row("?", "Help", "Open this keybindings and usage overview")
        table.add_row("q", "Quit", "Exit the SQLPhantom terminal workstation")
