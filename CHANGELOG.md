# Changelog

All notable changes to the **SQLPhantom** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0-dev] - Unreleased

### Added
- **Repository Scaffolding & Packaging**:
  - Configured modern Python packaging in [`pyproject.toml`](file:///d:/Projects/SQLPhantom/pyproject.toml) using the `hatchling` build backend.
  - Established modular monolith directory layout under `src/sqlphantom/` with clean layer boundaries:
    - `domain/`: Enterprise domain models, enums, value objects, and events.
    - `application/`: Service orchestration, use cases, target scope validation, and event bus.
    - `engine/`: Subprocess supervisor and REST API client for upstream sqlmap integration.
    - `storage/`: SQLite connection pool, migrations, and repository pattern.
    - `reporting/`: Multi-format report generation (HTML, Markdown, JSON).
    - `plugins/`: Extension hook specifications and sandboxed runners.
    - `gui/`: Desktop graphical user interface built with PySide6 (Qt 6).
    - `tui/`: Interactive console user interface built with Textual and Rich.
- **Upstream Engine Integration Baseline**:
  - Integrated upstream [sqlmap](https://github.com/sqlmapproject/sqlmap) as a pristine submodule pinned at commit [`6e06114`](https://github.com/sqlmapproject/sqlmap/commit/6e06114947397e1f5bbe428230e25cf1cf9f1a55) (version `1.10.10`).
  - Adopted the `sqlmapapi.py` REST API adapter pattern to ensure strict process isolation and prevent global state pollution.
- **Developer Tooling & Static Analysis**:
  - Configured strict static type checking via Mypy (`python_version = "3.11"`, `strict = true`).
  - Configured Ruff for high-speed linting and formatting with a 100-character line limit.
  - Setup Pytest test harness with `pytest-asyncio` for async workflows and `pytest-qt` for future GUI testing.
- **Executable CLI Entry Points**:
  - Defined script entry points:
    - `sqlphantom`: Main command-line interface.
    - `sqlphantom-gui`: PySide6 desktop application launcher.
    - `sqlphantom-tui`: Textual terminal application launcher.
- **Documentation Suite**:
  - Authored [README.md](file:///d:/Projects/SQLPhantom/README.md) with SQLPhantom branding, quick start, and platform support.
  - Authored [FEATURES.md](file:///d:/Projects/SQLPhantom/FEATURES.md) with canonical specification matrix across 14 feature categories and non-goals.
  - Authored [USAGE.md](file:///d:/Projects/SQLPhantom/USAGE.md) user manual covering requirements, workflows, storage locations, and troubleshooting.
  - Authored [ARCHITECTURE.md](file:///d:/Projects/SQLPhantom/ARCHITECTURE.md) detailing the modular monolith design, component diagrams, engine adapter, job state machine, and persistence.
  - Authored [ROADMAP.md](file:///d:/Projects/SQLPhantom/ROADMAP.md) detailing development phases from Phase 0 through Phase 5.
  - Authored [CONTRIBUTING.md](file:///d:/Projects/SQLPhantom/CONTRIBUTING.md) developer guidelines for code standards, testing, and pull requests.
  - Authored [SECURITY.md](file:///d:/Projects/SQLPhantom/SECURITY.md) covering vulnerability reporting, supported versions, and defensive guardrails.
  - Authored [THIRD_PARTY_NOTICES.md](file:///d:/Projects/SQLPhantom/THIRD_PARTY_NOTICES.md) documenting upstream attribution, dependency inventory, and license notices.

### In Progress (Phase 1 Foundation)
- Core domain model definitions using Pydantic v2 (`Target`, `Job`, `ScanConfig`, `Finding`, `Session`).
- Asynchronous typed `EventBus` implementation for reactive component communication.
- SQLite connection management with Write-Ahead Logging (WAL) and automated migration runner.
- `SqlmapApiProcess` subprocess supervisor for managing the `sqlmapapi.py` daemon lifecycle.
- `SqlmapApiClient` async HTTP client for sqlmap REST endpoints.
- Scope validation guardrails enforcing URL whitelists and CIDR range restrictions.

---

[0.1.0-dev]: https://github.com/sqlphantom/sqlphantom/releases/tag/v0.1.0-dev
