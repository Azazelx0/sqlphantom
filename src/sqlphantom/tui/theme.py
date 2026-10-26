"""
SQLPhantom Textual TUI Theme and CSS styles.
Conforms to the Stitch Cyber Violet Dark design system:
Deep Obsidian (#0B0F19), Dark Slate (#1E293B), Electric Purple (#7C3AED).
"""

SQLPHANTOM_CSS = """
Screen {
    background: #0B0F19;
    color: #F8FAFC;
}

Header {
    dock: top;
    height: 3;
    background: #111827;
    color: #A855F7;
    border-bottom: solid #7C3AED;
}

Footer {
    dock: bottom;
    height: 1;
    background: #111827;
    color: #94A3B8;
}

#nav-bar {
    dock: top;
    height: 3;
    background: #111827;
    border-bottom: solid #334155;
    layout: horizontal;
    padding: 0 1;
}

.nav-btn {
    margin: 0 1;
    background: #1E293B;
    color: #F8FAFC;
    border: none;
    height: 1;
}

.nav-btn:hover {
    background: #7C3AED;
    color: #FFFFFF;
}

.nav-btn.-active {
    background: #7C3AED;
    color: #FFFFFF;
    text-style: bold;
}

/* KPI Cards */
.kpi-container {
    layout: horizontal;
    height: 5;
    margin: 1 0;
}

.kpi-card {
    width: 1fr;
    height: 5;
    background: #1E293B;
    border: solid #334155;
    margin: 0 1;
    padding: 0 1;
    content-align: center middle;
}

.kpi-title {
    color: #94A3B8;
    text-style: bold;
}

.kpi-value {
    color: #A855F7;
    text-style: bold;
    text-align: center;
}

/* Containers */
.card-box {
    background: #1E293B;
    border: solid #334155;
    margin: 1 0;
    padding: 1;
}

.card-title {
    color: #A855F7;
    text-style: bold;
    margin-bottom: 1;
}

/* Tables */
DataTable {
    background: #0F172A;
    border: solid #334155;
    height: 1fr;
}

DataTable > .datatable--header {
    background: #1E293B;
    color: #A855F7;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #7C3AED;
    color: #FFFFFF;
}

/* Forms and Inputs */
Input {
    background: #0F172A;
    border: solid #334155;
    color: #F8FAFC;
    margin-bottom: 1;
}

Input:focus {
    border: solid #7C3AED;
}

Button {
    background: #7C3AED;
    color: #FFFFFF;
    border: none;
    margin: 1 1;
}

Button:hover {
    background: #9333EA;
}

.btn-secondary {
    background: #334155;
    color: #F8FAFC;
}

.btn-secondary:hover {
    background: #475569;
}

.btn-danger {
    background: #EF4444;
    color: #FFFFFF;
}

.btn-danger:hover {
    background: #DC2626;
}

/* Progress & Live Stream */
ProgressBar {
    margin: 1 0;
    color: #A855F7;
}

RichLog {
    background: #050811;
    border: solid #334155;
    color: #E2E8F0;
    height: 1fr;
    padding: 0 1;
}

/* Detail panel */
.detail-pane {
    background: #1E293B;
    border: solid #334155;
    height: 1fr;
    padding: 1;
}
"""
