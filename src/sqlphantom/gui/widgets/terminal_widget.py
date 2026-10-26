"""
Real-time PySide6 color-coded terminal log viewer.
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTextEdit, QWidget


class TerminalWidget(QTextEdit):
    """
    Monospace terminal output console rendering live assessment payloads,
    network status, and vulnerability notifications.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet(
            """
            QTextEdit {
                background-color: #050811;
                border: 1px solid #334155;
                border-radius: 6px;
                color: #E2E8F0;
                padding: 10px;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 12px;
                line-height: 1.5;
            }
            """
        )
        self.document().setDefaultFont(QFont("Consolas", 10))

    def append_info(self, message: str) -> None:
        html = f'<span style="color:#38BDF8; font-weight:bold;">[INFO]</span> <span style="color:#CBD5E1;">{message}</span>'
        self.append(html)

    def append_stage(self, stage: str, previous: str | None = None) -> None:
        prev_text = f' <span style="color:#64748B;">(was {previous})</span>' if previous else ""
        html = f'<span style="color:#C084FC; font-weight:bold;">[STAGE]</span> <span style="color:#A855F7; font-weight:bold;">Transitioning to {stage}</span>{prev_text}'
        self.append(html)

    def append_payload(self, message: str) -> None:
        html = f'<span style="color:#A855F7; font-weight:bold;">[PAYLOAD]</span> <span style="color:#F8FAFC;">{message}</span>'
        self.append(html)

    def append_vuln(self, title: str, parameter: str) -> None:
        html = f'<span style="color:#EF4444; font-weight:bold;">[VULN]</span> <span style="color:#FBBF24; font-weight:bold;">CONFIRMED: {title} on parameter \'{parameter}\'</span>'
        self.append(html)

    def append_cancel(self, reason: str) -> None:
        html = f'<span style="color:#EF4444; font-weight:bold;">[CANCEL]</span> <span style="color:#F87171; font-weight:bold;">Execution cancelled: {reason}</span>'
        self.append(html)

    def append_completed(self, count: int, duration: float) -> None:
        html = f'<span style="color:#10B981; font-weight:bold;">[DONE]</span> <span style="color:#34D399; font-weight:bold;">Assessment completed in {duration:.1f}s — Found {count} vulnerabilities</span>'
        self.append(html)
