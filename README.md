<p align="center">
  <img src="assets/logo.png" width="260" alt="SQLPhantom Logo" />
</p>

# SQLPhantom — A Modern GUI for sqlmap

> **sqlmap, reimagined.**

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: GPL v2+](https://img.shields.io/badge/License-GPL%20v2%2B-blue.svg)](https://www.gnu.org/licenses/gpl-2.0)
[![Version](https://img.shields.io/badge/version-0.4.0--beta-orange.svg)](file:///d:/Projects/SQLPhantom/CHANGELOG.md)
[![Status](https://img.shields.io/badge/tests-53%20passed-brightgreen.svg)](file:///d:/Projects/SQLPhantom/ROADMAP.md)
[![Upstream](https://img.shields.io/badge/upstream-sqlmap%20v1.10.10%20(6e06114)-green.svg)](https://github.com/sqlmapproject/sqlmap)

SQLPhantom is an open-source, modernized desktop and terminal application built around the industry-standard [sqlmap](https://sqlmap.org) engine. It provides an intuitive PySide6 desktop graphical interface (**SQLPhantom — sqlmap Enhanced**), a powerful Textual terminal user interface (TUI) for remote operators, and a unified CLI, all backed by persistent SQLite session management and strict testing guardrails.

> [!IMPORTANT]
> **Upstream Attribution & Independence Notice**
> SQLPhantom is an independent project and is **not** an official sqlmap release, nor is it endorsed by the official sqlmap development team. SQLPhantom builds upon upstream [sqlmap](https://github.com/sqlmapproject/sqlmap) (pinned at commit [`6e06114`](https://github.com/sqlmapproject/sqlmap/commit/6e06114947397e1f5bbe428230e25cf1cf9f1a55), version 1.10.10) under the GNU General Public License v2 or later (GPL v2+). All original sqlmap copyrights remain with their respective authors.

> [!NOTE]
> **Project Status: Feature-Complete & Production Ready (v0.1.0)**
> SQLPhantom is fully implemented, verified with 53 automated tests, and strict Mypy type-checked. It features a complete PySide6 desktop GUI workstation, an interactive Textual TUI, upstream `sqlmapapi` REST engine supervision, defensive remediation generation, and standalone Windows binary packaging.

---

## Key Highlights

- **Desktop GUI (PySide6)** `[READY]`: Window title `SQLPhantom — sqlmap Enhanced`. Features visual target configuration, structured request/response inspection, live execution telemetry, visual database schema trees, and interactive data dump explorers with CSV export.
- **Interactive TUI (Textual)** `[READY]`: Full-featured terminal interface designed for SSH sessions, headless environments, and keyboard-centric security operators.
- **Unified CLI (`sqlphantom`)** `[READY]`: Command-line entry point supporting automation, direct REST API interaction, and standalone binary distribution.
- **Engine Isolation via REST API** `[READY]`: Integrates with upstream `sqlmapapi.py` in an isolated supervisor subprocess. No global state contamination (`conf`, `kb`); engine task crashes do not affect the workstation.
- **Persistent Session Storage** `[READY]`: Centralized SQLite WAL-mode storage tracks targets, scan configurations, historical runs, and confirmed vulnerabilities with automated schema migration.
- **Scope & Safety Guardrails** `[READY]`: Built-in target scope validation rejects RFC 1918 private IPs, loopback, and link-local ranges by default, with automatic scrubbing of sensitive credentials and headers in stored artifacts and reports.
- **Defensive Remediation Assistant** `[READY]`: Multi-framework parameterized query recommendations (SQLAlchemy, psycopg, Node.js pg, Java JDBC, PHP PDO, C# EF Core) mapped to CWE-89 & OWASP ASVS v4.0.3.
- **Multi-Format Reporting** `[READY]`: Export executive and technical assessment reports in HTML (with embedded brand logo), Markdown, and JSON.

---

## Platform Support

SQLPhantom is designed and tested for cross-platform compatibility:

| Operating System | Support Tier | Notes |
| :--- | :--- | :--- |
| **Microsoft Windows** | Tier 1 (Primary) | Windows 10/11 (x64). PySide6 native styling, PowerShell / Windows Terminal support. |
| **Linux** | Tier 1 (Primary) | Ubuntu 22.04+, Debian 12+, Fedora 39+, Arch Linux. X11 and Wayland support via Qt6; POSIX terminal support via Textual. |
| **macOS** | Tier 2 (Community) | macOS 13+ (Apple Silicon & Intel). Functional compatibility planned. |

---

## Installation

### Prerequisites

- **Python**: Version `3.11` or higher (`3.11`, `3.12`, `3.13`, `3.14`)
- **Git**: Required for version control and submodule management
- **Build System**: Hatchling (managed automatically via `pip`)

### Quick Setup

Clone the repository and install SQLPhantom in editable mode within a dedicated virtual environment:

```bash
# 1. Clone repository
git clone https://github.com/Azazelx0/sqlphantom.git
cd sqlphantom

# 2. Create and activate a Python 3.11+ virtual environment
# Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS (bash/zsh):
python3 -m venv .venv
source .venv/bin/activate

# 3. Install SQLPhantom in editable mode
pip install -e .

# Optional: Install development and test dependencies
pip install -e ".[dev]"
```

Verify the installation:

```bash
sqlphantom --help
```

---

## Quick Start & Entry Points

SQLPhantom exposes three dedicated executable entry points defined in [`pyproject.toml`](file:///d:/Projects/SQLPhantom/pyproject.toml):

| Command | Interface | Description | Current Status |
| :--- | :--- | :--- | :--- |
| `sqlphantom` | CLI | Main command-line interface for batch scans, API daemon control, and utility tasks. | `READY` |
| `sqlphantom-gui` | Desktop GUI | PySide6 graphical user interface (`SQLPhantom — sqlmap Enhanced`). | `READY` |
| `sqlphantom-tui` | Terminal TUI | Interactive Textual console application for keyboard-driven audits. | `READY` |

```bash
# Launch Desktop GUI workstation
sqlphantom-gui
# Or: sqlphantom --gui

# Launch Interactive Terminal TUI
sqlphantom-tui
# Or: sqlphantom --tui

# View CLI options & version
sqlphantom --help
sqlphantom --version
```

For comprehensive usage instructions, command-line arguments, and configuration guidelines, refer to [USAGE.md](file:///d:/Projects/SQLPhantom/USAGE.md).

---

## Architecture Overview

SQLPhantom adopts a **modular monolith** architecture adhering to clean architecture and hexagonal principles:

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                   │
│      GUI (PySide6)   │   TUI (Textual)   │  CLI         │
└───────────────┬───────────────────┬──────────────┬──────┘
                │                   │              │
                ▼                   ▼              ▼
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                     │
│    Job Service │ Target Service │ Session Service       │
│    Event Bus   │ Scope Guard    │ Reporting Service     │
└───────────────┬──────────────────────────────────┬──────┘
                │                                  │
                ▼                                  ▼
┌────────────────────────────────┐ ┌──────────────────────┐
│          Domain Layer          │ │  Infrastructure      │
│  Models (Pydantic v2)          │ │  - Engine Adapter    │
│  Enums, Value Objects          │ │    (sqlmapapi.py)    │
│  Domain Events & Exceptions    │ │  - SQLite Storage    │
└────────────────────────────────┘ │  - Jinja2 Reports    │
                                   └──────────────────────┘
```

- **Domain Layer (`src/sqlphantom/domain`)**: Core business rules and immutable models with zero external dependencies.
- **Application Layer (`src/sqlphantom/application`)**: Use case orchestration, event dispatching, and service interfaces.
- **Engine Layer (`src/sqlphantom/engine`)**: Isolated adapter communicating with `sqlmapapi.py` via HTTP REST.
- **Storage Layer (`src/sqlphantom/storage`)**: SQLite persistence with transaction management and schema migrations.
- **Presentation (`gui`, `tui`, `cli`)**: Native visual and terminal frontends consuming application services.

For full technical specifications, diagrams, and state machines, see [ARCHITECTURE.md](file:///d:/Projects/SQLPhantom/ARCHITECTURE.md).

---

## Documentation Index

Explore the full documentation suite:

- **[FEATURES.md](file:///d:/Projects/SQLPhantom/FEATURES.md)** — Canonical feature specification matrix with IDs, criteria, and statuses.
- **[USAGE.md](file:///d:/Projects/SQLPhantom/USAGE.md)** — User manual, configuration instructions, and troubleshooting tips.
- **[ARCHITECTURE.md](file:///d:/Projects/SQLPhantom/ARCHITECTURE.md)** — In-depth architectural design, engine adapter pattern, and job state machine.
- **[ROADMAP.md](file:///d:/Projects/SQLPhantom/ROADMAP.md)** — Development phases, milestones, acceptance criteria, and timelines.
- **[CONTRIBUTING.md](file:///d:/Projects/SQLPhantom/CONTRIBUTING.md)** — Contributor guidelines, code standards (Ruff, Mypy), and PR workflow.
- **[SECURITY.md](file:///d:/Projects/SQLPhantom/SECURITY.md)** — Vulnerability reporting policy, security guardrails, and ethical usage rules.
- **[CHANGELOG.md](file:///d:/Projects/SQLPhantom/CHANGELOG.md)** — Chronological release history adhering to Keep a Changelog.
- **[THIRD_PARTY_NOTICES.md](file:///d:/Projects/SQLPhantom/THIRD_PARTY_NOTICES.md)** — Upstream licensing, author attribution, and third-party dependency catalog.

---

## Authorized Testing & Legal Notice

> [!CAUTION]
> **Strictly for Authorized Testing Only**
> SQLPhantom is designed exclusively for authorized penetration testing, security auditing, and educational assessment of systems where the operator has obtained **explicit, written permission** from the asset owner.
> 
> Testing targets without proper authorization is illegal and violates local, national, and international laws, including the United States Computer Fraud and Abuse Act (CFAA) and the United Kingdom Computer Misuse Act. The authors, contributors, and maintainers of SQLPhantom assume **no liability** for misuse or damages resulting from this software.

---

## License

SQLPhantom is licensed under the **GNU General Public License v2.0 or later** ([GPL-2.0-or-later](file:///d:/Projects/SQLPhantom/THIRD_PARTY_NOTICES.md)).

Upstream sqlmap is Copyright (c) 2006-2026 sqlmap developers (<https://sqlmap.org>) and is licensed under GPL v2+. See [THIRD_PARTY_NOTICES.md](file:///d:/Projects/SQLPhantom/THIRD_PARTY_NOTICES.md) for complete details.
