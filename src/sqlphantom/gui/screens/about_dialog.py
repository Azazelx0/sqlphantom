"""
SQLPhantom PySide6 About dialog.
"""

from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from sqlphantom import (
    __description__,
    __product__,
    __tagline__,
    __upstream__,
    __upstream_commit__,
    __upstream_version__,
    __version__,
)


class AboutDialog(QDialog):
    """
    About dialog presenting project identity, upstream sqlmap attribution,
    and open-source licensing.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About SQLPhantom")
        self.setFixedSize(520, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title_lbl = QLabel(f"{__product__} v{__version__}")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #A855F7;")
        tagline_lbl = QLabel(f"<b>{__tagline__}</b>")
        tagline_lbl.setStyleSheet("font-size: 14px; color: #F8FAFC;")

        desc_lbl = QLabel(
            "SQLPhantom is an enhanced fork of sqlmap featuring a PySide6 GUI, "
            "Textual TUI, and an improved security testing workflow."
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #CBD5E1; line-height: 1.4;")

        attribution_lbl = QLabel(
            f"<b>Upstream Baseline:</b> sqlmap v{__upstream_version__} (commit {__upstream_commit__[:7]})<br>"
            f"<b>Upstream Project:</b> {__upstream__}<br>"
            f"<b>License:</b> GNU General Public License v2 or later (GPLv2+)<br>"
            "sqlmap is Copyright (c) 2006-2026 sqlmap developers.<br><br>"
            "<i>Notice: SQLPhantom is an independent open-source fork and is not an official "
            "sqlmap release. No official endorsement is claimed.</i>"
        )
        attribution_lbl.setWordWrap(True)
        attribution_lbl.setStyleSheet("font-size: 11px; color: #94A3B8;")

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_box.addWidget(btn_close)

        layout.addWidget(title_lbl)
        layout.addWidget(tagline_lbl)
        layout.addWidget(desc_lbl)
        layout.addWidget(attribution_lbl)
        layout.addStretch()
        layout.addLayout(btn_box)
