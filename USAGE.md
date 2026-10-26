# SQLPhantom User Manual

Welcome to the **SQLPhantom** user manual. This document guides you through system requirements, installation, interface execution, core workflows, file storage locations, and troubleshooting.

> [!NOTE]
> **Implementation Status: Version 0.1.0-dev (Phase 1 Foundation)**
> SQLPhantom is currently in active development. Project scaffolding, dependency definitions, packaging, and domain models are being established.
> 
> Throughout this guide:
> - Features currently in active development are marked `[IN_PROGRESS]`.
> - Features planned for subsequent milestones (TUI in Phase 2, GUI in Phase 3, Reporting in Phase 4) are explicitly tagged `[PLANNED]`.
> - Mock or stub functionality is not represented as working.

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

### 3.1. Command-Line Interface (`sqlphantom`) `[IN_PROGRESS]`

The CLI entry point allows headless scans, automated pipelines, database management, and diagnostic checks.

```bash
# Show version and branding
sqlphantom --version

# Show general CLI help and available subcommands
sqlphantom --help

# Start or check status of the background sqlmapapi engine daemon [IN_PROGRESS]
sqlphantom engine status
sqlphantom engine start --port 8775

# Run an ad-hoc scan against an authorized target [IN_PROGRESS]
sqlphantom scan --url "http://example.internal/item.php?id=1" --dbms mysql

# List past scan sessions stored in SQLite [IN_PROGRESS]
sqlphantom session list
```

### 3.2. Desktop Graphical Interface (`sqlphantom-gui`) `[PLANNED]`

The desktop graphical interface provides a rich, multi-tab window titled **`SQLPhantom — sqlmap Enhanced`**.

```bash
sqlphantom-gui
```

#### What `sqlphantom-gui` Will Offer:
- **Visual Target Builder**: Intuitive forms for URL parameters, HTTP headers, cookies, and injection boundaries without memorizing CLI syntax.
- **Live Assessment Telemetry**: Color-coded streaming logs, request graphs, and real-time stage progress bars.
- **Request/Response Diff Viewer**: Side-by-side inspection of baseline HTTP requests and injection payloads with automatic secret redaction.
- **Interactive Database Tree**: Hierarchical exploration of extracted database schemas, tables, and columns.
- **Virtualized Data Dump Grid**: High-performance grid for previewing extracted rows and exporting to CSV, JSON, or SQLite.

*(Note: During Phase 1, invoking `sqlphantom-gui` displays a clean informative notification detailing its release in Phase 3).*

### 3.3. Terminal User Interface (`sqlphantom-tui`) `[PLANNED]`

The interactive TUI provides a full-featured console dashboard optimized for keyboard-driven operators and remote SSH sessions.

```bash
sqlphantom-tui
```

#### What `sqlphantom-tui` Will Offer:
- Full-screen dashboard using Textual and Rich with vim-style keyboard navigation.
- Real-time streaming log panel with search and log level filters.
- Active targets and background jobs monitoring table.
- Interactive findings browser and data dump table viewer.

*(Note: During Phase 1, invoking `sqlphantom-tui` displays a clean informative notification detailing its release in Phase 2).*

---

## 4. Planned Workflows & Features

This section details how key assessment workflows will operate once fully implemented:

### Workflow 1: Defining Scope & Adding Targets `[PLANNED]`
1. Open the **Scope Settings** dialog.
2. Define target boundaries (e.g. `*.target-company.internal`, IP subnet `10.10.14.0/24`).
3. Enter the target URL or paste an entire HTTP request captured from Burp Suite or OWASP ZAP.
4. SQLPhantom automatically checks the target against scope guardrails. If a URL resolves outside the authorized boundary, dispatch is blocked with an explicit error.

### Workflow 2: Launching an Assessment Job `[IN_PROGRESS]`
1. Choose assessment parameters (Level 1–5, Risk 1–3, DBMS type, or specific techniques: Boolean, Error, UNION, Stacked, Time-based).
2. Click **Start Scan** (or run `sqlphantom scan`).
3. SQLPhantom automatically starts an isolated `sqlmapapi.py` subprocess on localhost, sets scan options via REST API, and begins polling for real-time telemetry.
4. Scan progress and heuristic milestones are emitted over the internal `EventBus` and displayed in the UI.

### Workflow 3: Analyzing Discovered Findings `[PLANNED]`
1. As vulnerabilities are confirmed by the engine, they appear immediately in the **Findings** pane.
2. Selecting a finding displays the affected parameter, injection technique, payload snippet, and reproducible cURL / sqlmap reproduction commands.
3. Operators can mark findings as `Verified`, `False Positive`, or `Informational`, and add custom notes.

### Workflow 4: Enumerating Databases & Extracting Data `[PLANNED]`
1. Navigate to the **Database Explorer** tab.
2. Expand the database hierarchy to view tables and columns discovered during the scan.
3. Select specific columns and specify a row limit (e.g. max 20 rows) to extract minimal necessary proof while adhering to data privacy policies.
4. Export the extracted table directly to CSV, JSON, or SQLite.

### Workflow 5: Generating Assessment Reports `[PLANNED]`
1. Open **Reports** → **Generate Report**.
2. Select desired formats: **HTML** (self-contained interactive report with charts), **Markdown** (for Jira/GitHub issues), or **JSON** (for SIEM/vulnerability tracking).
3. Toggle sensitive data masking (automatically replaces credentials, cookies, and tokens with `[REDACTED]`).
4. Generate and save the report artifact.

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
