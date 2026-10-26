"""
Reusable PySide6 KPI metric card widget.
"""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class KPICard(QFrame):
    """Card widget rendering key metrics and operational telemetry."""

    def __init__(self, title: str, value: str, subtext: str = "", parent=None):
        super().__init__(parent)
        self.setProperty("class", "card-frame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        self.lbl_title = QLabel(title.upper())
        self.lbl_title.setProperty("class", "kpi-title")

        self.lbl_value = QLabel(value)
        self.lbl_value.setProperty("class", "kpi-value")

        self.lbl_subtext = QLabel(subtext)
        self.lbl_subtext.setProperty("class", "kpi-subtext")

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)
        if subtext:
            layout.addWidget(self.lbl_subtext)
        else:
            self.lbl_subtext.hide()

    def update_value(self, new_value: str) -> None:
        self.lbl_value.setText(new_value)

    def update_subtext(self, new_subtext: str) -> None:
        self.lbl_subtext.setText(new_subtext)
        self.lbl_subtext.show()
