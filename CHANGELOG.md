# Changelog

All notable changes to the **SQLPhantom** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0-dev] - Unreleased

### Added
- **Repository Scaffolding & Packaging**:
  - Configured modern Python packaging in [`pyproject.toml`](file:///d:/Projects/SQLPhantom/pyproject.toml) using the `hatchling` build backend.
  - Established modular monolith directory layout under `src/sqlphantom/` with clean layer boundaries.
  - Authored comprehensive documentation suite: `README.md`, `FEATURES.md`, `USAGE.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `THIRD_PARTY_NOTICES.md`, and `LICENSE` (GPL v2).
- **Stitch MCP UI Design System**:
  - Created project `SQLPhantom` (`projects/4909255305486689225`) and established **SQLPhantom Cyber Violet Dark** design system (`assets/447596690595683055`).
  - Generated and downloaded production HTML & PNG mockups for Main Dashboard, Live Assessment Monitor, and Findings Viewer.
- **Phase 1: Foundation Milestone**:
  - Pydantic v2 core domain models: `Target`, `ScopeRule`, `AssessmentConfig`, `Finding`, `JobResult`, `Project`, `Session`.
  - Typed immutable domain events: `JobCreated`, `JobStarted`, `StageChanged`, `ProgressUpdated`, `FindingDiscovered`, `JobCancelled`, `JobFailed`, `JobCompleted`.
  - Scope guardrails: Domain allowlists, URL pattern matching, and automatic RFC 1918 / loopback / link-local private IP protection.
  - Thread-safe pub/sub `EventBus` with subscriber exception isolation.
  - `JobManager` orchestrating job state machine and supervisor monitoring.
  - SQLite storage with WAL mode and repository pattern (`ProjectRepository`, `FindingRepository`, `SessionRepository`).
  - `MockEngineAdapter` simulating multi-stage scan lifecycle and cancellation.
- **Phase 2: Interactive Terminal Workstation (TUI MVP)**:
  - Full-screen Textual application shell with dark theme TCSS.
  - Dashboard, Assessment Setup Wizard, Live Monitor, Findings Triage, and Help screens.
  - Reusable `KPICard` and `LogStream` widgets.
  - Headless async UI tests using Textual test pilot framework.
- **Phase 3: Desktop Graphical Interface (GUI MVP)**:
  - PySide6 desktop workstation titled `SQLPhantom — sqlmap Enhanced`.
  - Custom QSS stylesheet adhering to Stitch design tokens (`#0B0F19`, `#1E293B`, `#7C3AED`).
  - Thread-safe `EventSignalBridge` connecting background domain events to Qt signals.
  - Screens: Dashboard, Assessment Wizard, Raw HTTP Request Workbench, Live Monitor, Findings Viewer, and About Dialog.
  - Headless automated tests with `pytest-qt`.
- **Phase 4: Reports & Plugin Architecture**:
  - Sensitive credential & token redaction subsystem (`Bearer`, `Basic`, `cookie`, `session_id`, `password`, `api_key`).
  - Multi-format report generator: HTML, Markdown, and JSON.
  - `compare_sessions` algorithm tracking new, resolved, and common vulnerabilities.
  - Plugin extension contracts (`BasePlugin`, `ReportExporterPlugin`, `FindingEnricherPlugin`) and `PluginRegistry` with sandboxed execution.
- **Phase 5: Real Engine Integration & Hardening**:
  - `SqlmapProcessSupervisor` for isolated `sqlmapapi.py --server` daemon management with mandatory authentication.
  - `SqlmapApiClient` HTTP client for task lifecycle, scan execution, and data extraction.
  - `SqlmapEngineAdapter` translating domain configurations to sqlmap options.
  - Complete 40-test automated verification suite passing at 100%.

---

[0.1.0-dev]: https://github.com/Azazelx0/sqlphantom/releases/tag/v0.1.0-dev
