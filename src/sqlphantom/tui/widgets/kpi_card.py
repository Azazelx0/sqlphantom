"""
Reusable KPI metric card widget for the Textual TUI.
"""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Static


class KPICard(Static):
    """Card widget rendering a key performance indicator or status counter."""

    DEFAULT_CSS = """
    KPICard {
        width: 1fr;
        height: 5;
        background: #1E293B;
        border: solid #334155;
        margin: 0 1;
        padding: 0 1;
        content-align: center middle;
    }
    """

    def __init__(self, title: str, value: str, subtext: str = "", id: str | None = None):
        super().__init__(id=id)
        self.title_text = title
        self.value_text = value
        self.subtext = subtext

    def compose(self) -> ComposeResult:
        yield Label(self.title_text, classes="kpi-title")
        yield Label(self.value_text, classes="kpi-value")
        if self.subtext:
            yield Label(self.subtext, classes="kpi-subtext")

    def update_value(self, new_value: str) -> None:
        self.value_text = new_value
        try:
            val_label = self.query_one(".kpi-value", Label)
            val_label.update(new_value)
        except Exception:
            pass
