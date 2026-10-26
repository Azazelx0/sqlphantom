# SQLPhantom User Manual

Welcome to the **SQLPhantom** user manual. This document guides you through system requirements, installation, interface execution, core workflows, file storage locations, and troubleshooting.

> [!NOTE]
> **Implementation Status: Fully Implemented & Ready (v0.1.0)**
> SQLPhantom is feature-complete with all primary interfaces (Desktop GUI, Terminal TUI, CLI), upstream REST engine supervision, defensive remediation generation, database schema browsing, session drift comparison, and standalone executable bundling.

---

## 1. System Requirements

### Hardware Requirements
- **Processor**: x86_64 or ARM64 processor (dual-core 1.5 GHz minimum; quad-core recommended).
- **Memory (RAM)**: 2 GB minimum; 4 GB or more recommended when running the desktop GUI and extensive database dump operations.
- **Disk Space**: At least 250 MB free space for application dependencies and SQLite session databases.

### Supported Operating Systems
- **Microsoft Windows**: Windows 10 (1809+) or Windows 11 (64-bit).
- **Linux**: Any modern POSIX Linux distribution (Ubuntu 22.04 LTS+, Debian 12+, Fedora 39+, Arch Linux, Kali Linux 2023+).
- **macOS**: macOS 13 (Ventura) or later (community support tier).

### Software Prerequisites
- **Python**: Version **3.11** or higher (`3.11`, `3.12`, `3.13`, `3.14`). Verify using `python --version`.
- **Git**: Required to clone repository and manage upstream submodules.
- **Display System (for GUI)**:
  - Windows: Native Windows Desktop.
  - Linux: X11 or Wayland with standard Qt6 runtime libraries (`libxcb`, `libxkbcommon`, `libgl1`).
- **Terminal (for TUI/CLI)**:
  - Windows: Windows Terminal (recommended) or PowerShell with UTF-8 support enabled.
  - Linux/macOS: Any modern ANSI/UTF-8 compatible terminal emulator (Alacritty, Kitty, GNOME Terminal, Konsole, tmux).

---

## 2. Installation & Setup

### Step 1: Clone the Repository

Clone the SQLPhantom repository to your local system:

```bash
git clone https://github.com/Azazelx0/sqlphantom.git
cd sqlphantom
```

### Step 2: Create a Virtual Environment

It is strongly recommended to use a dedicated Python virtual environment to isolate dependencies:

#### Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> [!TIP]
> If PowerShell displays a script execution policy error, enable local script execution for the current user:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

#### Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install SQLPhantom

Install SQLPhantom in editable development mode:

```bash
# Basic installation (Runtime dependencies: PySide6, Textual, Pydantic, Rich, HTTPX)
pip install -e .

# Full development installation (Includes pytest, pytest-asyncio, pytest-qt, ruff, mypy)
pip install -e ".[dev]"
```

Verify that the CLI command is available:

```bash
sqlphantom --version
```

---

## 3. Launching the Interfaces

SQLPhantom provides three primary entry points:

### 3.1. Command-Line Interface (`sqlphantom`) `[READY]`

The CLI entry point allows launching the desktop GUI, interactive terminal TUI, or inspecting version information:

```bash
# Show version and branding
sqlphantom --version

# Show general CLI help
sqlphantom --help

# Launch Desktop GUI workstation
sqlphantom --gui
# Or directly:
sqlphantom-gui

# Launch Terminal TUI
sqlphantom --tui
# Or directly:
sqlphantom-tui
```

### 3.2. Desktop Graphical Interface (`sqlphantom-gui`) `[READY]`

The desktop graphical interface provides a rich, multi-tab window titled **`SQLPhantom — sqlmap Enhanced`**.

```bash
sqlphantom-gui
# Or: sqlphantom --gui
```

#### What `sqlphantom-gui` Delivers:
- **Visual Target Builder**: Intuitive wizard for URL parameters, HTTP methods, headers, cookies, and injection level/risk sliders.
- **Visual Scope Safeguards**: Multi-line allowlist editor for domain targets, regex patterns, and private IP rejection with interactive pre-flight testing.
- **Raw HTTP Request Workbench**: Import or paste full HTTP requests from Burp Suite or OWASP ZAP with one-click parameter extraction.
- **Live Assessment Telemetry**: Color-coded streaming terminal logs, telemetry KPI cards, and real-time stage progress bars with emergency cancel controls.
- **Defensive Remediation Assistant**: Automated parameterized query code generation (SQLAlchemy, psycopg, Node.js pg, Java JDBC, PHP PDO, C# EF Core) mapped to CWE-89 & OWASP ASVS v4.0.3.
- **Interactive Database Schema Explorer**: Hierarchical tree exploration of extracted database schemas, tables, and columns.
- **Virtualized Data Dump Grid**: High-performance grid for previewing extracted rows with one-click CSV export.
- **Historical Sessions & Vulnerability Drift**: Session history viewer with side-by-side drift comparison between sequential scans.
- **Light & Dark Theme Switching**: Instant toggle between Cyber Violet Dark and Enterprise Slate Light themes.

### 3.3. Terminal User Interface (`sqlphantom-tui`) `[READY]`

The interactive TUI provides a full-featured console dashboard optimized for keyboard-driven operators and remote SSH sessions.

```bash
sqlphantom-tui
# Or: sqlphantom --tui
```

#### What `sqlphantom-tui` Delivers:
- Full-screen dashboard using Textual and Rich with single-key navigation (`d` for Dashboard, `n` for New Scan, `m` for Monitor, `f` for Findings, `r` for Fast Scan, `?` for Help, `q` for Quit).
- Real-time streaming log panel with payload inspection and stage progression indicators.
- Active targets and background jobs monitoring table.
- Interactive findings triage browser with OWASP ASVS remediation recommendations and multi-format report export (HTML, Markdown, JSON).

---

## 4. Assessment Workflows

### Workflow 1: Defining Scope & Adding Targets
1. Open the **Scope Boundary Rules** dialog in the wizard.
2. Define target boundaries (e.g. `testphp.vulnweb.com`).
3. Enter the target URL or paste an entire HTTP request captured from Burp Suite or OWASP ZAP into the **Request Editor**.
4. Test the target in the pre-flight tester. If a URL resolves outside the authorized boundary or touches private RFC 1918 IPs, dispatch is blocked with an explicit error.

### Workflow 2: Launching an Assessment Job
1. Choose assessment parameters (Level 1–5, Risk 1–3, DBMS type, or specific techniques: Boolean, Error, UNION, Stacked, Time-based).
2. Configure optional upstream proxy (HTTP/SOCKS5) and request throttling delay.
3. Click **Start Assessment**.
4. SQLPhantom automatically starts an isolated `sqlmapapi.py` subprocess with credentials and dynamic port allocation, sets scan options via REST API, and begins streaming real-time telemetry.
5. Scan progress and heuristic milestones are emitted over the internal `EventBus` and displayed in the UI.

### Workflow 3: Analyzing Discovered Findings
1. Confirmed vulnerabilities appear in real time in the **Findings** pane.
2. Selecting a finding displays the affected parameter, injection technique, payload snippet, and extracted evidence.
3. Operators can mark findings as `ACTIVE`, `CONFIRMED`, `FALSE_POSITIVE`, or `VERIFIED_FIXED`, and add custom analyst notes saved to SQLite WAL storage.
4. Switch to the **Defensive Remediation** tab to copy secure parameterized code snippets for your backend framework.

### Workflow 4: Enumerating Databases & Extracting Data
1. Navigate to the **Database Explorer** tab.
2. Expand the database hierarchy to view tables and columns discovered during the scan.
3. Select any table to inspect data dumps in the virtualized grid.
4. Click **Export Table to CSV** to save records for reporting.

### Workflow 5: Generating Assessment Reports
1. In the **Findings** pane, click **Export Report** (or choose HTML, Markdown, or JSON).
2. All sensitive data (credentials, auth tokens, session cookies, API keys) are automatically scrubbed and replaced with `[REDACTED]`.
3. HTML reports include executive metric summaries, the official SQLPhantom branding, vulnerability breakdowns, and OWASP remediation guidelines.

---

## 5. Data Storage Locations

SQLPhantom stores configuration, audit databases, scan logs, and exported reports in standard, OS-compliant application directories:

### Directory Locations

| Platform | Configuration Directory | Data & Database Directory |
| :--- | :--- | :--- |
| **Microsoft Windows** | `%APPDATA%\sqlphantom` (`C:\Users\<User>\AppData\Roaming\sqlphantom`) | `%LOCALAPPDATA%\sqlphantom` (`C:\Users\<User>\AppData\Local\sqlphantom`) |
| **Linux** | `~/.config/sqlphantom` (or `$XDG_CONFIG_HOME/sqlphantom`) | `~/.local/share/sqlphantom` (or `$XDG_DATA_HOME/sqlphantom`) |
| **macOS** | `~/Library/Application Support/sqlphantom` | `~/Library/Application Support/sqlphantom` |

### Storage File Layout

```
<Data Directory>/
├── sqlphantom.db           # Central SQLite database (sessions, targets, jobs, findings)
├── config.toml             # User configuration file (UI themes, proxy, scope defaults)
├── logs/
│   ├── sqlphantom.log      # Application logs (Ruff/Python structured logging)
│   └── engine_api.log      # sqlmapapi subprocess stdout/stderr capture
├── dumps/                  # Dumped database tables saved per session
└── reports/                # Generated HTML, Markdown, and JSON report exports
```

### SQLite Database Integrity
The SQLite database (`sqlphantom.db`) runs with **Write-Ahead Logging (WAL)** enabled for high-concurrency read/write operations between the background engine polling task and UI threads. Schema evolution is managed via automated versioned migrations in the `migrations/` directory.

---

## 6. Troubleshooting & Common Questions

### 1. Python Version Error
- **Symptom**: `TypeError`, syntax errors, or `pip` failing to find compatible dependencies.
- **Cause**: SQLPhantom requires Python **3.11** or higher.
- **Solution**: Verify your active Python version with `python --version`. If needed, install Python 3.11+ using `pyenv`, your distribution package manager, or the official installer from [python.org](https://www.python.org).

### 2. Linux GUI Launch Failure (Missing Qt Libraries)
- **Symptom**: `ImportError: libGL.so.1: cannot open shared object file` or Qt platform plugin initialization failures on Linux.
- **Cause**: Minimal Linux installations may lack standard X11/Wayland and OpenGL libraries required by PySide6.
- **Solution**: Install Qt6 dependencies on Debian/Ubuntu:
  ```bash
  sudo apt-get update
  sudo apt-get install -y libgl1-mesa-glx libegl1 libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xfixes0
  ```

### 3. Port Conflict on `8775` (sqlmapapi)
- **Symptom**: Error indicating port `8775` is already in use when launching an assessment.
- **Cause**: Another instance of `sqlmapapi.py` or a conflicting service is bound to port 8775.
- **Solution**: Specify an alternative port using the `--port` option:
  ```bash
  sqlphantom engine start --port 8780
  ```
  Or terminate existing orphaned processes:
  - Windows: `Get-Process python | Where-Object { $_.CommandLine -like "*sqlmapapi*" } | Stop-Process`
  - Linux: `pkill -f sqlmapapi.py`

### 4. Windows PowerShell Unicode Characters Distorted
- **Symptom**: Terminal UI borders or Unicode symbols appear as question marks or corrupt boxes in PowerShell.
- **Cause**: Default console code page is not configured for UTF-8.
- **Solution**: Use **Windows Terminal** rather than legacy `conhost.exe`, and ensure UTF-8 encoding is enabled in PowerShell:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  ```

### 5. Running Tests to Verify Installation
Verify that your local installation passes all automated checks:

```bash
# Run unit and integration tests
pytest

# Run static type checking
mypy src tests

# Run linter checks
ruff check src tests
```

---

## 7. Security and Compliance Reminder

> [!CAUTION]
> SQLPhantom is intended exclusively for authorized penetration testing, vulnerability assessment, and educational research on systems where you possess explicit, written permission from the asset owner. Unauthorized vulnerability scanning or exploitation is illegal under computer misuse legislation worldwide.
