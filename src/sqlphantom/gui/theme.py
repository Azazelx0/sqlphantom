"""
SQLPhantom PySide6 Qt stylesheet (QSS) adhering to Stitch Cyber Violet Dark tokens.
Palette:
- Background Base: #0B0F19 (Deep Obsidian)
- Surface Background: #111827 (Dark Slate Gray)
- Surface Elevated: #1E293B (Card & Container Slate)
- Border / Divider: #334155 (Subtle Slate Border)
- Primary Accent: #7C3AED (Electric Purple)
- Accent Hover: #9333EA
- Text Primary: #F8FAFC
- Text Secondary: #94A3B8
- Critical Alert: #EF4444
"""

DARK_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #0B0F19;
    color: #F8FAFC;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 13px;
}

QWidget {
    background-color: transparent;
    color: #F8FAFC;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Sidebar Navigation */
#sidebar-panel {
    background-color: #111827;
    border-right: 1px solid #334155;
    min-width: 200px;
    max-width: 220px;
}

#sidebar-brand {
    font-size: 16px;
    font-weight: bold;
    color: #A855F7;
    padding: 16px 12px 4px 12px;
}

#sidebar-subtitle {
    font-size: 11px;
    color: #94A3B8;
    padding: 0 12px 16px 12px;
}

QPushButton.nav-button {
    text-align: left;
    padding: 10px 14px;
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 6px;
    margin: 2px 8px;
    font-weight: 500;
}

QPushButton.nav-button:hover {
    background-color: #1E293B;
    color: #F8FAFC;
}

QPushButton.nav-button:checked, QPushButton.nav-button.active {
    background-color: rgba(124, 58, 237, 0.2);
    color: #A855F7;
    font-weight: bold;
    border-left: 3px solid #7C3AED;
}

/* Standard Buttons */
QPushButton {
    background-color: #7C3AED;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #9333EA;
}

QPushButton:pressed {
    background-color: #6D28D9;
}

QPushButton:disabled {
    background-color: #334155;
    color: #64748B;
}

QPushButton.secondary {
    background-color: #1E293B;
    border: 1px solid #334155;
    color: #F8FAFC;
}

QPushButton.secondary:hover {
    background-color: #334155;
}

QPushButton.danger {
    background-color: #EF4444;
    color: #FFFFFF;
}

QPushButton.danger:hover {
    background-color: #DC2626;
}

/* Card Containers */
QFrame.card-frame {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px;
}

QLabel.card-title {
    font-size: 14px;
    font-weight: bold;
    color: #A855F7;
    margin-bottom: 6px;
}

QLabel.kpi-title {
    font-size: 11px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
}

QLabel.kpi-value {
    font-size: 22px;
    font-weight: bold;
    color: #F8FAFC;
}

QLabel.kpi-subtext {
    font-size: 11px;
    color: #64748B;
}

/* Text Inputs and Editors */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #F8FAFC;
    padding: 8px;
    font-size: 13px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #7C3AED;
}

/* Tables */
QTableWidget {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 6px;
    gridline-color: #1E293B;
    color: #F8FAFC;
    selection-background-color: #7C3AED;
    selection-color: #FFFFFF;
}

QHeaderView::section {
    background-color: #1E293B;
    color: #A855F7;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #334155;
    font-weight: bold;
    font-size: 12px;
}

/* Progress Bar */
QProgressBar {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 4px;
    height: 16px;
    text-align: center;
    color: #F8FAFC;
    font-weight: bold;
    font-size: 11px;
}

QProgressBar::chunk {
    background-color: #7C3AED;
    border-radius: 3px;
}

/* Tab Widgets */
QTabWidget::pane {
    border: 1px solid #334155;
    border-radius: 6px;
    background-color: #1E293B;
    top: -1px;
}

QTabBar::tab {
    background-color: #111827;
    border: 1px solid #334155;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 14px;
    margin-right: 2px;
    color: #94A3B8;
}

QTabBar::tab:selected {
    background-color: #1E293B;
    color: #A855F7;
    font-weight: bold;
    border-top: 2px solid #7C3AED;
}

/* Scroll Bars */
QScrollBar:vertical {
    background-color: #0B0F19;
    width: 8px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #7C3AED;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Stitch Top App Bar */
#top-app-bar {
    background-color: #0F172A;
    border-bottom: 1px solid #334155;
    min-height: 48px;
    max-height: 48px;
}

QLineEdit#target-quick-input {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 12px;
    color: #E2E8F0;
    font-family: monospace;
    font-size: 12px;
}

QLineEdit#target-quick-input:focus {
    border: 1px solid #7C3AED;
}

/* Stitch Badges & Bento Cards */
.badge-pill-emerald {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

.badge-pill-rose {
    background-color: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

.badge-pill-violet {
    background-color: rgba(124, 58, 237, 0.2);
    color: #C084FC;
    border: 1px solid rgba(124, 58, 237, 0.4);
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

.badge-pill-amber {
    background-color: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

.bento-card {
    background-color: #111827;
    border: 1px solid #1E293B;
    border-radius: 10px;
    padding: 14px;
}

.bento-card:hover {
    border: 1px solid rgba(124, 58, 237, 0.5);
}

.hero-banner {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px 20px;
}

.stage-stepper-box {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 10px;
}

.stage-stepper-active {
    background-color: rgba(124, 58, 237, 0.25);
    border: 1px solid #8B5CF6;
    border-radius: 8px;
    padding: 8px 10px;
}

.stage-stepper-done {
    background-color: #111827;
    border: 1px solid rgba(16, 185, 129, 0.4);
    border-radius: 8px;
    padding: 8px 10px;
}
"""

LIGHT_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 13px;
}

QWidget {
    background-color: transparent;
    color: #0F172A;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

#sidebar-panel {
    background-color: #F1F5F9;
    border-right: 1px solid #E2E8F0;
    min-width: 200px;
    max-width: 220px;
}

#sidebar-brand {
    font-size: 16px;
    font-weight: bold;
    color: #7C3AED;
    padding: 16px 12px 4px 12px;
}

#sidebar-subtitle {
    font-size: 11px;
    color: #64748B;
    padding: 0 12px 16px 12px;
}

QPushButton.nav-button {
    text-align: left;
    padding: 10px 14px;
    background-color: transparent;
    color: #475569;
    border: none;
    border-radius: 6px;
    margin: 2px 8px;
    font-weight: 500;
}

QPushButton.nav-button:hover {
    background-color: #E2E8F0;
    color: #0F172A;
}

QPushButton.nav-button:checked, QPushButton.nav-button.active {
    background-color: rgba(124, 58, 237, 0.12);
    color: #7C3AED;
    font-weight: bold;
    border-left: 3px solid #7C3AED;
}

QPushButton {
    background-color: #7C3AED;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #6D28D9;
}

QPushButton:disabled {
    background-color: #E2E8F0;
    color: #94A3B8;
}

QPushButton.secondary {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    color: #0F172A;
}

QPushButton.secondary:hover {
    background-color: #F1F5F9;
}

QPushButton.danger {
    background-color: #DC2626;
    color: #FFFFFF;
}

QFrame.card-frame {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 16px;
}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 6px 10px;
    color: #0F172A;
}

QLineEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #7C3AED;
}

QTableWidget, QTreeWidget {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    gridline-color: #F1F5F9;
    color: #0F172A;
}

QHeaderView::section {
    background-color: #F8FAFC;
    color: #475569;
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid #E2E8F0;
    font-weight: 600;
}

QTableWidget::item:selected, QTreeWidget::item:selected {
    background-color: rgba(124, 58, 237, 0.15);
    color: #7C3AED;
}

QProgressBar {
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    text-align: center;
    background-color: #F1F5F9;
    color: #0F172A;
    font-weight: bold;
    height: 16px;
}

QProgressBar::chunk {
    background-color: #7C3AED;
    border-radius: 5px;
}

QTabWidget::pane {
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    background-color: #FFFFFF;
    top: -1px;
}

QTabBar::tab {
    background-color: #F1F5F9;
    border: 1px solid #E2E8F0;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 14px;
    margin-right: 2px;
    color: #64748B;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #7C3AED;
    font-weight: bold;
    border-top: 2px solid #7C3AED;
}
"""


def get_theme_stylesheet(theme_name: str = "dark") -> str:
    """Return the Qt stylesheet for the requested theme."""
    if theme_name.lower() == "light":
        return LIGHT_STYLESHEET
    return DARK_STYLESHEET
