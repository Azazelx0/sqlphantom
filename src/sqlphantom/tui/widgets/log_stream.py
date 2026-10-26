"""
Real-time color-coded event stream and terminal log viewer widget.
"""

from rich.text import Text
from textual.widgets import RichLog


class LogStream(RichLog):
    """
    Dedicated terminal log viewer displaying real-time assessment events,
    stage transitions, and discovered vulnerabilities.
    """

    DEFAULT_CSS = """
    LogStream {
        background: #050811;
        border: solid #334155;
        color: #E2E8F0;
        height: 1fr;
        padding: 0 1;
    }
    """

    def __init__(self, id: str | None = None):
        super().__init__(highlight=True, markup=True, id=id)

    def log_info(self, message: str) -> None:
        t = Text()
        t.append("[INFO] ", style="bold cyan")
        t.append(message, style="slate")
        self.write(t)

    def log_stage(self, stage: str, previous: str | None = None) -> None:
        t = Text()
        t.append("[STAGE] ", style="bold magenta")
        t.append(f"Transitioning to {stage}", style="bold purple")
        if previous:
            t.append(f" (was {previous})", style="dim")
        self.write(t)

    def log_payload(self, message: str) -> None:
        t = Text()
        t.append("[PAYLOAD] ", style="bold #A855F7")
        t.append(message, style="white")
        self.write(t)

    def log_vuln(self, title: str, parameter: str) -> None:
        t = Text()
        t.append("[VULN] ", style="bold red")
        t.append(f"CONFIRMED: {title} on parameter '{parameter}'", style="bold yellow")
        self.write(t)

    def log_cancel(self, reason: str) -> None:
        t = Text()
        t.append("[CANCEL] ", style="bold #EF4444")
        t.append(f"Execution cancelled: {reason}", style="bold red")
        self.write(t)

    def log_completed(self, count: int, duration: float) -> None:
        t = Text()
        t.append("[DONE] ", style="bold green")
        t.append(
            f"Assessment completed in {duration:.1f}s — Found {count} vulnerabilities",
            style="bold green",
        )
        self.write(t)
