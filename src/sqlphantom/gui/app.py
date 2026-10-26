"""
SQLPhantom PySide6 Desktop GUI application runner.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

from sqlphantom.gui.main_window import MainWindow
from sqlphantom.gui.theme import DARK_STYLESHEET


def run_gui_app(db_path: str | Path | None = None) -> int:
    """Initialize and run the PySide6 desktop GUI workstation."""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)

    if db_path is None:
        user_data_dir = Path.home() / ".sqlphantom"
        user_data_dir.mkdir(exist_ok=True)
        db_path = user_data_dir / "sqlphantom.db"

    window = MainWindow(db_path=db_path)
    window.show()

    return app.exec()
