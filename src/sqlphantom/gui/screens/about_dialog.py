"""
SQLPhantom PySide6 About dialog with brand logo and upstream attribution.
"""

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
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
    About dialog presenting project identity, brand logo, upstream sqlmap attribution,
    and open-source licensing.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About SQLPhantom")
        self.setFixedSize(560, 420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Header with Logo
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        if not logo_path.exists():
            logo_path = Path("assets/logo.png")

        if logo_path.exists():
            lbl_logo = QLabel()
            pixmap = QPixmap(str(logo_path)).scaled(
                96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            lbl_logo.setPixmap(pixmap)
            header_layout.addWidget(lbl_logo)

        header_text = QVBoxLayout()
        title_lbl = QLabel(f"{__product__} v{__version__}")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #A855F7;")
        tagline_lbl = QLabel(f"<b>{__tagline__}</b>")
        tagline_lbl.setStyleSheet("font-size: 14px; color: #F8FAFC;")
        header_text.addWidget(title_lbl)
        header_text.addWidget(tagline_lbl)
        header_layout.addLayout(header_text)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        desc_lbl = QLabel(
            "SQLPhantom is an enhanced, open-source modernization of sqlmap featuring a PySide6 GUI, "
            "Textual TUI, structured findings, database schema explorer, and a robust application architecture."
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

        layout.addWidget(desc_lbl)
        layout.addWidget(attribution_lbl)
        layout.addStretch()
        layout.addLayout(btn_box)
