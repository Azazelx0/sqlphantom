# SQLPhantom Feature Specification

This document serves as the canonical feature specification matrix for **SQLPhantom** (`0.1.0-dev`). It tracks all intended and in-progress capabilities across desktop, terminal, engine, storage, security, and developer domains.

## Status Legend

- `IN_PROGRESS`: Actively under implementation in Phase 1 (Foundation).
- `PLANNED`: Formalized design scheduled for subsequent development phases (Phases 2–5).
- `IMPLEMENTED`: Code complete and functionally working.
- `TESTED`: Code complete with passing automated unit/integration tests.
- `DEFERRED`: Temporarily postponed to a future version milestone.

---

## 1. Graphical User Interface (GUI)

The desktop GUI is built with PySide6 (Qt 6) and targets penetration testers and security engineers requiring visual workflows.

### GUI-001: Main Application Shell & Window Management
- **Description**: Main window shell titled `SQLPhantom — sqlmap Enhanced` featuring responsive split panes, top menu bar, status bar, and workspace navigation drawer.
- **User Value**: Provides a cohesive desktop workspace for managing assessments, viewing engine health, and switching contexts without terminal fragmentation.
- **Dependencies**: `PySide6>=6.6`, [DEV-001](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-001-typed-domain-event-bus), [DEV-002](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-002-pydantic-v2-domain-models).
- **Acceptance Criteria**: Window opens with title `SQLPhantom — sqlmap Enhanced`; restores window size/state across restarts; displays real-time engine process status in the status bar.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/gui/test_main_window.py`

### GUI-002: Target Configuration Wizard
- **Description**: Multi-step wizard and form allowing users to configure target URLs, HTTP methods, headers, cookies, data payloads, injection parameters, and assessment depth.
- **User Value**: Eliminates manual construction of long, error-prone CLI flag sequences while exposing advanced sqlmap options.
- **Dependencies**: `PySide6>=6.6`, [HTTP-001](file:///d:/Projects/SQLPhantom/FEATURES.md#http-001-raw-http-request-parser), [SCOPE-001](file:///d:/Projects/SQLPhantom/FEATURES.md#scope-001-target-url--host-whitelisting).
- **Acceptance Criteria**: Form validates inputs via Pydantic; supports pasting raw Burp/ZAP HTTP requests; verifies URL scope before enabling submission.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/gui/test_target_wizard.py`

### GUI-003: Live Job Telemetry & Execution Console
- **Description**: Real-time console view displaying colorized sqlmap output logs, current attack technique, target status, and request throughput graphs.
- **User Value**: Delivers immediate visibility into assessment progress without manual polling or log file tailing.
- **Dependencies**: [ENG-004](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-004-scan-polling--telemetry-ingestion), [JOB-004](file:///d:/Projects/SQLPhantom/FEATURES.md#job-004-stage-progression-telemetry).
- **Acceptance Criteria**: Live streaming log updates without UI freezing; search and log level filtering (DEBUG, INFO, WARNING); auto-scroll toggle.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/gui/test_live_telemetry.py`

### GUI-004: Request & Response Inspector
- **Description**: Dual-pane hex and text viewer showing individual HTTP requests dispatched by the engine and the corresponding server responses.
- **User Value**: Allows operators to analyze exact payloads, boundary tests, and differential response characteristics.
- **Dependencies**: [HTTP-001](file:///d:/Projects/SQLPhantom/FEATURES.md#http-001-raw-http-request-parser), [SEC-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sec-001-credential--header-redaction).
- **Acceptance Criteria**: Displays headers and body with syntax highlighting; automatically redacts sensitive authorization tokens; allows payload copying.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/gui/test_request_inspector.py`

### GUI-005: Visual Database Schema Tree Browser
- **Description**: Interactive tree hierarchy displaying extracted databases, tables, columns, and data types as sqlmap enumerates the target.
- **User Value**: Provides immediate conceptual structure of compromised relational databases without reading tabular CLI dumps.
- **Dependencies**: [ASSESS-003](file:///d:/Projects/SQLPhantom/FEATURES.md#assess-003-database-schema--table-enumeration), [SESS-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sess-001-sqlite-persistent-session-store).
- **Acceptance Criteria**: Updates dynamically as enumeration tasks complete; supports node expansion, search filtering, and context menu actions for dumping specific tables.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/gui/test_schema_tree.py`

### GUI-006: Data Dump Table Grid with Export
- **Description**: High-performance virtualized table grid for previewing extracted rows and dumping them to CSV, JSON, or SQLite formats.
- **User Value**: Enables quick data validation and evidence capture without external spreadsheet or database tools.
- **Dependencies**: [ASSESS-004](file:///d:/Projects/SQLPhantom/FEATURES.md#assess-004-column-extraction--data-dump), [SESS-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sess-001-sqlite-persistent-session-store).
- **Acceptance Criteria**: Handles 50,000+ rows smoothly via Qt model virtualization; allows column sorting, filtering, and one-click export.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/gui/test_data_grid.py`

### GUI-007: Scope Boundary Configuration Dialog
- **Description**: Visual editor for defining allowed domains, subdomains, IP ranges (CIDR), and explicitly excluded paths.
- **User Value**: Protects operators from accidentally scanning third-party infrastructure or out-of-scope targets.
- **Dependencies**: [SCOPE-001](file:///d:/Projects/SQLPhantom/FEATURES.md#scope-001-target-url--host-whitelisting), [SCOPE-002](file:///d:/Projects/SQLPhantom/FEATURES.md#scope-002-cidr-network-range-validation).
- **Acceptance Criteria**: Rejects out-of-scope targets before job submission; displays prominent visual warnings when targets approach boundary limits.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/gui/test_scope_dialog.py`

### GUI-008: Finding Detail & Proof-of-Concept Drawer
- **Description**: Slide-over panel detailing detected SQL injection vulnerabilities, parameter names, payload types, CVSS score estimate, and reproducible cURL/sqlmap reproduction commands.
- **User Value**: Accelerates vulnerability reporting and client verification by generating ready-to-run PoC snippets.
- **Dependencies**: [FIND-001](file:///d:/Projects/SQLPhantom/FEATURES.md#find-001-vulnerability-data-model--ingestion), [FIND-003](file:///d:/Projects/SQLPhantom/FEATURES.md#find-003-reproducible-poc-generator).
- **Acceptance Criteria**: Displays payload, injection type (boolean, time-based, error, UNION), parameter, and verified PoC string.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/gui/test_finding_drawer.py`

### GUI-009: Session History & Workspace Switcher
- **Description**: Sidebar and modal for loading, switching, and archiving project workspaces and historical scan sessions.
- **User Value**: Allows operators to return to past assessments, inspect previous findings, and resume interrupted scans.
- **Dependencies**: [SESS-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sess-001-sqlite-persistent-session-store), [SESS-002](file:///d:/Projects/SQLPhantom/FEATURES.md#sess-002-workspace--project-management).
- **Acceptance Criteria**: Lists past sessions with target summary, date, status, and finding count; allows switching without data loss.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/gui/test_workspace_switcher.py`

### GUI-010: Dark and Light Theme Support
- **Description**: Native Qt stylesheet themes supporting Dark and Light color palettes aligned with operating system preferences.
- **User Value**: Reduces eye strain during extended testing sessions and adapts to operator desktop environment settings.
- **Dependencies**: `PySide6>=6.6`.
- **Acceptance Criteria**: Clean UI rendering in both themes with high-contrast text and accessible status indicators.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/gui/test_themes.py`

---

## 2. Terminal User Interface (TUI)

The TUI is built with Textual and Rich, providing a rich, reactive console interface for remote and terminal-first operators.

### TUI-001: Textual Main Application Frame
- **Description**: Full-screen console layout featuring header, breadcrumb navigation, interactive tabs (Targets, Active Jobs, Findings, Logs), and footer key bindings.
- **User Value**: Delivers GUI-like capabilities within a standard terminal or SSH connection.
- **Dependencies**: `textual>=0.40`, `rich>=13.0`, [DEV-001](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-001-typed-domain-event-bus).
- **Acceptance Criteria**: Launches via `sqlphantom-tui`; responsive to terminal resize events; standard vim-style and arrow navigation keys.
- **Status**: `TESTED`
- **Associated Tests**: `tests/tui/test_tui.py`

### TUI-002: Interactive Target & Parameter Input Screen
- **Description**: Modal form for specifying target URL, HTTP method, post data, cookies, and injection boundaries with keyboard navigation.
- **User Value**: Allows quick target entry without memorizing complex CLI switches.
- **Dependencies**: `textual>=0.40`, [DEV-002](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-002-pydantic-v2-domain-models).
- **Acceptance Criteria**: Form validation with immediate feedback; history of previously entered URLs accessible via up/down arrows.
- **Status**: `TESTED`
- **Associated Tests**: `tests/tui/test_tui.py`

### TUI-003: Live Status & Log Streaming Widget
- **Description**: Textual widget displaying streaming logs, progress bars, and current stage indicators in real time.
- **User Value**: Keeps operator informed during lengthy blind or time-based SQL injection scans.
- **Dependencies**: `textual>=0.40`, [ENG-004](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-004-scan-polling--telemetry-ingestion).
- **Acceptance Criteria**: Non-blocking log rendering; support for pause/resume scrolling; syntax-highlighted SQL payloads.
- **Status**: `TESTED`
- **Associated Tests**: `tests/tui/test_tui.py`

### TUI-004: Keyboard-Driven Findings Browser
- **Description**: Interactive list and detail view for browsing discovered vulnerabilities, affected parameters, and injection techniques.
- **User Value**: Enables fast triage and inspection directly from the terminal.
- **Dependencies**: [FIND-001](file:///d:/Projects/SQLPhantom/FEATURES.md#find-001-vulnerability-data-model--ingestion).
- **Acceptance Criteria**: Keybindings for switching between findings, viewing raw HTTP requests, and copying reproduction commands.
- **Status**: `TESTED`
- **Associated Tests**: `tests/tui/test_tui.py`

### TUI-005: Database Dump Table Grid
- **Description**: Terminal table widget rendering extracted database tables, schemas, and columns using Rich tables.
- **User Value**: Allows inspecting database contents directly in the terminal session.
- **Dependencies**: [ASSESS-004](file:///d:/Projects/SQLPhantom/FEATURES.md#assess-004-column-extraction--data-dump), `rich>=13.0`.
- **Acceptance Criteria**: Formats tabular data with automatic column wrapping; supports horizontal scrolling for wide database tables.
- **Status**: `IMPLEMENTED`
- **Associated Tests**: `tests/tui/test_tui.py`

### TUI-006: Session Management & Quick Launch
- **Description**: Screen to resume previous sessions, re-run completed jobs, or purge old session data.
- **User Value**: Operator can disconnect and reconnect to terminal sessions without losing audit context.
- **Dependencies**: [SESS-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sess-001-sqlite-persistent-session-store).
- **Acceptance Criteria**: Loads session list from SQLite; resumes state on selection.
- **Status**: `TESTED`
- **Associated Tests**: `tests/tui/test_tui.py`

---

## 3. Engine Integration (Engine)

The engine layer encapsulates communication with the upstream sqlmap engine using the official REST API (`sqlmapapi.py`).

### ENG-001: sqlmapapi Subprocess Lifecycle Supervisor
- **Description**: Manager class responsible for spawning, health-checking, and cleanly terminating the `sqlmapapi.py --server` daemon in an isolated subprocess.
- **User Value**: Guarantees zero risk of global state contamination or thread deadlocks from upstream sqlmap internals, ensuring UI stability.
- **Dependencies**: Python standard library `subprocess`, `sys`.
- **Acceptance Criteria**: Spawns server on an available localhost port; waits for ready signal; terminates cleanly on application exit without leaving orphan processes.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/unit/test_engine_process.py`, `tests/integration/test_engine_lifecycle.py`

### ENG-002: REST API Async Client
- **Description**: High-performance HTTP client wrapping sqlmap REST API endpoints (`/task/new`, `/task/<id>/delete`, `/scan/<id>/start`, `/scan/<id>/status`, `/scan/<id>/data`, `/scan/<id>/log`, `/scan/<id>/stop`, `/scan/<id>/kill`).
- **User Value**: Provides strongly-typed Python async methods for every sqlmap API capability.
- **Dependencies**: `httpx>=0.25`, [DEV-002](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-002-pydantic-v2-domain-models).
- **Acceptance Criteria**: Implements connection retry, timeout handling, error response mapping, and authentication token injection.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/unit/test_engine_client.py`

### ENG-003: Task Creation & Option Mapping
- **Description**: Translator mapping high-level SQLPhantom domain scan configurations into sqlmapapi `/option/<id>/set` payloads.
- **User Value**: Translates friendly UI options into the exact parameter names and types expected by sqlmap engine.
- **Dependencies**: [DEV-002](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-002-pydantic-v2-domain-models).
- **Acceptance Criteria**: Maps all core sqlmap options (URL, method, data, cookies, level, risk, technique, tamper, dbms); validates types before sending.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/unit/test_option_mapping.py`

### ENG-004: Scan Polling & Telemetry Ingestion
- **Description**: Asynchronous polling worker that queries `/scan/<id>/status`, `/scan/<id>/log`, and `/scan/<id>/data`, emitting typed events.
- **User Value**: Converts raw JSON polling responses into structured domain events for UI and storage layers.
- **Dependencies**: [DEV-001](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-001-typed-domain-event-bus), [ENG-002](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-002-rest-api-async-client).
- **Acceptance Criteria**: Incremental log ingestion without duplicate messages; emits events on state changes; handles network hiccups gracefully.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_scan_polling.py`

### ENG-005: Process Graceful Stop & Kill Fallback
- **Description**: Two-tiered termination strategy: issues `/scan/<id>/stop` then `/scan/<id>/kill`, falling back to OS process termination if necessary.
- **User Value**: Guarantees that scans stop immediately when requested by operator, avoiding hung background connections.
- **Dependencies**: [ENG-001](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-001-sqlmapapi-subprocess-lifecycle-supervisor), [ENG-002](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-002-rest-api-async-client).
- **Acceptance Criteria**: Scan stops within 3 seconds of user request; cleans up temporary engine task files.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_scan_cancellation.py`

### ENG-006: Engine Version & Health Check
- **Description**: Diagnostics service checking upstream sqlmap commit baseline, Python environment, network bind capability, and API responsiveness.
- **User Value**: Alerts users immediately if upstream dependencies or runtime prerequisites are misconfigured.
- **Dependencies**: [ENG-001](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-001-sqlmapapi-subprocess-lifecycle-supervisor).
- **Acceptance Criteria**: Returns engine version (`1.10.10`), git commit hash (`6e06114`), and API latency; reports failures with remediation advice.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/unit/test_engine_health.py`

---

## 4. HTTP Handling (HTTP)

### HTTP-001: Raw HTTP Request Parser
- **Description**: RFC 7230/9112 compliant parser that parses raw HTTP requests exported from Burp Suite, OWASP ZAP, or browser dev tools.
- **User Value**: Allows operators to paste captured requests directly to configure targets without manually re-entering headers and parameters.
- **Dependencies**: [DEV-002](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-002-pydantic-v2-domain-models).
- **Acceptance Criteria**: Correctly parses method, path, headers, cookies, query string, and body across GET, POST, PUT, PATCH, DELETE.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_http_parser.py`

### HTTP-002: Header & Cookie Injection Configuration
- **Description**: Interface and models for configuring custom HTTP request headers, User-Agent rotation, Bearer tokens, and session cookies.
- **User Value**: Accommodates complex authenticated workflows and custom API authentication schemes.
- **Dependencies**: [DEV-002](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-002-pydantic-v2-domain-models).
- **Acceptance Criteria**: Correctly passes custom headers and cookies to engine configuration; redacts secrets in persisted logs.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_http_config.py`

### HTTP-003: Proxy & Upstream Tunnel Routing
- **Description**: Proxy routing configuration supporting HTTP, HTTPS, SOCKS4, and SOCKS5 upstream proxies with optional authentication.
- **User Value**: Allows routing traffic through Burp Suite upstream, Tor, or internal corporate bastion hosts.
- **Dependencies**: [ENG-003](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-003-task-creation--option-mapping).
- **Acceptance Criteria**: Validates proxy URL format; configures sqlmap proxy parameters correctly; supports upstream SSL inspection.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_proxy_config.py`

### HTTP-004: TLS/SSL Custom Cipher & Certificate Handling
- **Description**: Configuration options for custom client certificates, CA bundles, and disabling certificate verification for self-signed staging targets.
- **User Value**: Enables seamless assessment of staging, development, and internal corporate endpoints using internal PKI.
- **Dependencies**: [ENG-003](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-003-task-creation--option-mapping).
- **Acceptance Criteria**: Exposes flags for ignoring invalid SSL certificates; accepts client certificate and key paths.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_ssl_config.py`

### HTTP-005: Rate Limiting & Request Throttling
- **Description**: Controls for setting request delay, timeout, retries, and maximum requests-per-second to prevent target DoS.
- **User Value**: Ensures assessment complies with client SLA constraints and avoids triggering rate limits or service degradation.
- **Dependencies**: [ENG-003](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-003-task-creation--option-mapping).
- **Acceptance Criteria**: Enforces minimum delay between requests in engine settings; validates safe ranges.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_rate_limiting.py`

---

## 5. Assessment & Detection (Assessment)

### ASSESS-001: Injection Technique Selector
- **Description**: Fine-grained configuration for enabling or disabling specific SQL injection techniques: Boolean-based blind (B), Error-based (E), UNION query-based (U), Stacked queries (S), Time-based blind (T), and Inline queries (Q).
- **User Value**: Allows targeted, minimal-impact testing when specific techniques are known or when certain techniques are prohibited by engagement rules.
- **Dependencies**: [ENG-003](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-003-task-creation--option-mapping).
- **Acceptance Criteria**: Maps selected technique flags into sqlmap `--technique` options; validates combinations.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_technique_selector.py`

### ASSESS-002: DBMS Fingerprinting & Heuristic Detection
- **Description**: Automated heuristic detection of back-end DBMS (MySQL, PostgreSQL, Oracle, Microsoft SQL Server, SQLite, etc.) and version detection.
- **User Value**: Surfaces underlying database technology early, allowing rapid assessment customization.
- **Dependencies**: [ENG-004](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-004-scan-polling--telemetry-ingestion).
- **Acceptance Criteria**: Ingests sqlmap banner and heuristic detection logs; records identified DBMS type and version in domain model.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_dbms_detection.py`

### ASSESS-003: Database Schema & Table Enumeration
- **Description**: Structured retrieval of database names, tables, and column metadata without dumping table data.
- **User Value**: Enables safe inventorying of target database structure to prioritize sensitive tables before initiating data extraction.
- **Dependencies**: [ENG-003](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-003-task-creation--option-mapping), [FIND-001](file:///d:/Projects/SQLPhantom/FEATURES.md#find-001-vulnerability-data-model--ingestion).
- **Acceptance Criteria**: Issues `--dbs`, `--tables`, `--columns` commands; parses resulting schema data into structured domain entities.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_schema_enumeration.py`

### ASSESS-004: Column Extraction & Data Dump
- **Description**: Targeted extraction of specific database columns or row ranges with configurable limits.
- **User Value**: Allows operators to dump minimal necessary proof (e.g. `LIMIT 5`) rather than extracting entire tables.
- **Dependencies**: [ENG-003](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-003-task-creation--option-mapping), [SESS-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sess-001-sqlite-persistent-session-store).
- **Acceptance Criteria**: Enforces configurable row limit safeguards (default max 100 rows unless explicitly overridden); stores dump in SQLite.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_data_dump.py`

### ASSESS-005: Custom Tamper Script Integration
- **Description**: Selection and chaining of upstream sqlmap tamper scripts (e.g., `between`, `charencode`, `space2comment`) with custom tamper script loading.
- **User Value**: Enables bypassing specific web application firewall (WAF) encoding rules.
- **Dependencies**: [ENG-003](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-003-task-creation--option-mapping).
- **Acceptance Criteria**: Lists available upstream tamper scripts; validates script file existence; formats tamper argument correctly.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_tamper_integration.py`

### ASSESS-006: WAF/IPS Detection Notification
- **Description**: Detects upstream engine warnings regarding WAF/IPS intervention and alerts operator with suggested tamper scripts.
- **User Value**: Informs tester when defensive controls are altering responses and recommends remediation.
- **Dependencies**: [ENG-004](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-004-scan-polling--telemetry-ingestion), [DEV-001](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-001-typed-domain-event-bus).
- **Acceptance Criteria**: Emits `WafDetectedEvent` when WAF signatures are identified; provides actionable suggestions.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_waf_detection.py`

---

## 6. Scope & Guardrails (Scope)

### SCOPE-001: Target URL & Host Whitelisting
- **Description**: Explicit scope definition allowing only specified target hosts, domains, and URL patterns.
- **User Value**: Guarantees that scans cannot inadvertently target out-of-scope infrastructure.
- **Dependencies**: [DEV-002](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-002-pydantic-v2-domain-models).
- **Acceptance Criteria**: Rejects target URLs whose hostname does not match configured scope list; returns clear validation errors.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_scope_whitelisting.py`

### SCOPE-002: CIDR Network Range Validation
- **Description**: Validates that target hostnames resolve exclusively to IP addresses within authorized CIDR IP blocks.
- **User Value**: Prevents DNS rebinding or unintended testing of shared cloud hosting IP addresses outside engagement boundaries.
- **Dependencies**: [SCOPE-001](file:///d:/Projects/SQLPhantom/FEATURES.md#scope-001-target-url--host-whitelisting).
- **Acceptance Criteria**: Performs DNS resolution check; verifies resolved IP against CIDR whitelist; halts if target resolves outside scope.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_cidr_validation.py`

### SCOPE-003: Out-of-Scope Pre-Flight Dispatch Guard
- **Description**: Interceptor running before any engine scan task is dispatched, verifying all URLs, redirects, and proxy destinations against active scope rules.
- **User Value**: Fail-safe boundary defense preventing accidental dispatches at the application layer.
- **Dependencies**: [SCOPE-001](file:///d:/Projects/SQLPhantom/FEATURES.md#scope-001-target-url--host-whitelisting), [JOB-001](file:///d:/Projects/SQLPhantom/FEATURES.md#job-001-job-lifecycle-state-machine).
- **Acceptance Criteria**: Throws `OutOfScopeException` and blocks job transition to `RUNNING` if target fails scope checks.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_scope_guard.py`

### SCOPE-004: Wildcard Domain Rule Enforcement
- **Description**: Supports scoping rules with subdomain wildcards (e.g., `*.example.com`) while explicitly preventing dangerous top-level wildcards (e.g., `*.com` or `*`).
- **User Value**: Supports broad corporate domain testing while enforcing safety checks against accidental internet-wide scanning.
- **Dependencies**: [SCOPE-001](file:///d:/Projects/SQLPhantom/FEATURES.md#scope-001-target-url--host-whitelisting).
- **Acceptance Criteria**: Validates wildcard patterns; rejects single-level or public suffix wildcards.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_wildcard_rules.py`

---

## 7. Job Lifecycle & Queue (Jobs)

### JOB-001: Job Lifecycle State Machine
- **Description**: Formal state machine governing job lifecycle: `CREATED` → `QUEUED` → `RUNNING` (with stages) → `COMPLETED` / `FAILED` / `CANCELLED`.
- **User Value**: Provides predictable, reliable job state transitions and clean error recovery.
- **Dependencies**: [DEV-001](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-001-typed-domain-event-bus), [DEV-002](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-002-pydantic-v2-domain-models).
- **Acceptance Criteria**: Disallows invalid state transitions; persists state changes to storage; emits transition events.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/unit/test_job_state_machine.py`

### JOB-002: Concurrent Job Queue Management
- **Description**: Configurable job scheduler supporting sequential or bounded concurrent job execution with priority ordering.
- **User Value**: Allows queueing multiple targets or parameters for overnight or batch assessments without overloading local resources.
- **Dependencies**: [JOB-001](file:///d:/Projects/SQLPhantom/FEATURES.md#job-001-job-lifecycle-state-machine).
- **Acceptance Criteria**: Enforces configurable maximum concurrency (default 1 to prevent engine starvation); processes queue in FIFO or priority order.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_job_queue.py`

### JOB-003: Job Pause, Resume & Cancellation
- **Description**: Clean cancellation and pause capabilities for active jobs with checkpoint saving in SQLite.
- **User Value**: Allows operators to halt scans immediately when target maintenance windows end and resume later.
- **Dependencies**: [ENG-005](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-005-process-graceful-stop--kill-fallback), [JOB-001](file:///d:/Projects/SQLPhantom/FEATURES.md#job-001-job-lifecycle-state-machine).
- **Acceptance Criteria**: Stops scan safely; records resume token/checkpoint; updates job state to `CANCELLED` or `PAUSED`.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_job_cancellation.py`

### JOB-004: Stage Progression Telemetry
- **Description**: Tracks granular progress across stages: Target Connection → Heuristic Check → Vulnerability Identification → Fingerprinting → Enumeration.
- **User Value**: Provides meaningful high-level progress indicators beyond raw log lines.
- **Dependencies**: [ENG-004](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-004-scan-polling--telemetry-ingestion).
- **Acceptance Criteria**: Calculates stage progress percentage; updates job model with active stage name and elapsed duration.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_stage_telemetry.py`

### JOB-005: Job Execution History & Metrics
- **Description**: Records scan start time, completion time, total HTTP requests sent, bytes transferred, and finding counts.
- **User Value**: Gives operators audit metrics for post-engagement reporting and capacity planning.
- **Dependencies**: [JOB-001](file:///d:/Projects/SQLPhantom/FEATURES.md#job-001-job-lifecycle-state-machine), [SESS-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sess-001-sqlite-persistent-session-store).
- **Acceptance Criteria**: Computes and stores aggregate metrics upon job termination.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_job_metrics.py`

### JOB-006: Background Task Worker Isolation
- **Description**: Worker runner decoupling UI threads from background scan execution and network I/O.
- **User Value**: Prevents UI stutter or unresponsiveness during intensive scanning operations.
- **Dependencies**: Python `asyncio`, [ENG-001](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-001-sqlmapapi-subprocess-lifecycle-supervisor).
- **Acceptance Criteria**: Zero UI frame drops or freezes; background exceptions handled cleanly without crashing main event loop.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_worker_isolation.py`

---

## 8. Findings & Vulnerability Management (Findings)

### FIND-001: Vulnerability Data Model & Ingestion
- **Description**: Domain models representing discovered SQL injection vulnerabilities, injection types, affected parameters, payloads, and DBMS technology.
- **User Value**: Standardizes vulnerability data structure for rendering, storage, and reporting.
- **Dependencies**: [DEV-002](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-002-pydantic-v2-domain-models).
- **Acceptance Criteria**: Models all sqlmap injection types; parses raw engine data payloads into typed entities; validates schemas.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/unit/test_finding_model.py`

### FIND-002: Severity & CWE Classification
- **Description**: Automatic mapping of discovered vulnerabilities to Common Weakness Enumeration (CWE-89) and default CVSS v3.1 base score metrics.
- **User Value**: Enhances raw scan results with industry-standard vulnerability risk classifications.
- **Dependencies**: [FIND-001](file:///d:/Projects/SQLPhantom/FEATURES.md#find-001-vulnerability-data-model--ingestion).
- **Acceptance Criteria**: Categorizes SQL injection findings under CWE-89; assigns appropriate severity ratings (High/Critical) based on capability.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_cwe_mapping.py`

### FIND-003: Reproducible Proof-of-Concept Generator
- **Description**: Generates reproducible cURL commands, Python requests snippets, and standalone sqlmap commands for each detected vulnerability.
- **User Value**: Allows security engineers to instantly verify findings and supply clean reproduction steps to development teams.
- **Dependencies**: [FIND-001](file:///d:/Projects/SQLPhantom/FEATURES.md#find-001-vulnerability-data-model--ingestion).
- **Acceptance Criteria**: Generated cURL command reproduces the injection payload with exact headers and parameters.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_poc_generator.py`

### FIND-004: Finding Deduplication & Aggregation
- **Description**: Deduplicates multiple injection payloads detected on the same target parameter, grouping them into a single consolidated finding.
- **User Value**: Prevents report bloat and avoids cluttering operator triage queues with redundant records.
- **Dependencies**: [FIND-001](file:///d:/Projects/SQLPhantom/FEATURES.md#find-001-vulnerability-data-model--ingestion).
- **Acceptance Criteria**: Groups findings by target URL, HTTP method, and parameter name while preserving all verified technique payloads.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_finding_deduplication.py`

### FIND-005: False Positive Marking & Operator Notes
- **Description**: Allows operators to mark findings as verified, false positive, or informational, and attach Markdown assessment notes.
- **User Value**: Gives operators control over final report contents directly inside the application.
- **Dependencies**: [FIND-001](file:///d:/Projects/SQLPhantom/FEATURES.md#find-001-vulnerability-data-model--ingestion), [SESS-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sess-001-sqlite-persistent-session-store).
- **Acceptance Criteria**: Persists operator triage status and notes in SQLite; excludes marked false positives from reports by default.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_finding_triage.py`

---

## 9. Sessions & Persistence (Sessions)

### SESS-001: SQLite Persistent Session Store
- **Description**: Centralized SQLite repository managing targets, configurations, scan jobs, findings, logs, and dumped tables.
- **User Value**: Preserves all assessment data across application restarts and prevents data loss.
- **Dependencies**: Python standard library `sqlite3`, [DEV-002](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-002-pydantic-v2-domain-models).
- **Acceptance Criteria**: Implements WAL mode for concurrent access; provides ACID transaction safety; supports CRUD for all entities.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/unit/test_sqlite_storage.py`

### SESS-002: Workspace & Project Management
- **Description**: Organization of assessments into distinct workspaces/projects with isolated database records and export bundles.
- **User Value**: Keeps multiple client engagements and assessments strictly separated.
- **Dependencies**: [SESS-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sess-001-sqlite-persistent-session-store).
- **Acceptance Criteria**: Creates, renames, switches, and deletes workspaces; ensures no data leakage across project boundaries.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_workspace_service.py`

### SESS-003: Target History & Replay
- **Description**: Historical log of previously tested targets with capability to re-run scans with identical or modified parameters.
- **User Value**: Saves time when re-testing fixed vulnerabilities during remediation verification.
- **Dependencies**: [SESS-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sess-001-sqlite-persistent-session-store), [JOB-001](file:///d:/Projects/SQLPhantom/FEATURES.md#job-001-job-lifecycle-state-machine).
- **Acceptance Criteria**: Clones historical target configuration into a new scan job; tracks verification history.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_target_replay.py`

### SESS-004: Database Schema Migration Runner
- **Description**: Version-controlled migration system managing SQLite schema evolution across SQLPhantom versions.
- **User Value**: Enables seamless database upgrades when new application versions introduce schema changes without user intervention.
- **Dependencies**: [SESS-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sess-001-sqlite-persistent-session-store).
- **Acceptance Criteria**: Applies pending migrations in sequential order; tracks applied schema version; supports rollback on failure.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/unit/test_migrations.py`

---

## 10. Reporting (Reporting)

### REP-001: HTML Executive & Technical Report Export
- **Description**: Standalone, interactive HTML report generation containing executive summary, vulnerability details, affected parameters, and reproduction steps.
- **User Value**: Produces client-ready deliverables without manual document editing.
- **Dependencies**: `jinja2`, [FIND-001](file:///d:/Projects/SQLPhantom/FEATURES.md#find-001-vulnerability-data-model--ingestion), [SEC-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sec-001-credential--header-redaction).
- **Acceptance Criteria**: Generates self-contained HTML (embedded CSS/JS); includes summary charts, finding tables, and proof-of-concept details.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_html_report.py`

### REP-002: Markdown Report Generation
- **Description**: Clean GitHub-flavored Markdown report exporter suitable for ingestion into bug trackers (Jira, GitLab, GitHub Issues).
- **User Value**: Accelerates engineering handoffs and ticketing workflows.
- **Dependencies**: [FIND-001](file:///d:/Projects/SQLPhantom/FEATURES.md#find-001-vulnerability-data-model--ingestion).
- **Acceptance Criteria**: Valid GFM markdown output; includes collapsible raw payload blocks and structured finding tables.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_markdown_report.py`

### REP-003: Machine-Readable JSON Export
- **Description**: Comprehensive JSON export adhering to a versioned SQLPhantom report schema for ingestion into SIEMs and vulnerability management platforms.
- **User Value**: Supports automated DevSecOps pipelines and corporate vulnerability databases.
- **Dependencies**: [DEV-002](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-002-pydantic-v2-domain-models).
- **Acceptance Criteria**: Exports valid JSON matching schema; includes targets, scan metadata, findings, and timings.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_json_report.py`

### REP-004: Sensitive Data Masking in Reports
- **Description**: Automatic redaction and masking of discovered user credentials, sensitive database fields, and authorization tokens in all generated reports.
- **User Value**: Prevents compliance violations and credential leaks when sharing reports across teams.
- **Dependencies**: [SEC-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sec-001-credential--header-redaction), [REP-001](file:///d:/Projects/SQLPhantom/FEATURES.md#rep-001-html-executive--technical-report-export).
- **Acceptance Criteria**: Masks passwords, tokens, and PII patterns with `[REDACTED]`; operator can toggle masking behavior.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_report_masking.py`

### REP-005: Custom Report Template Support
- **Description**: Template engine allowing organizations to supply custom Jinja2 HTML and Markdown templates with corporate branding and logos.
- **User Value**: Enables security consultancies to produce branded reports matching client requirements.
- **Dependencies**: [REP-001](file:///d:/Projects/SQLPhantom/FEATURES.md#rep-001-html-executive--technical-report-export).
- **Acceptance Criteria**: Loads external templates from user config directory; injects report context variables.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_custom_templates.py`

---

## 11. Plugins & Extensions (Plugins)

### PLUG-001: Plugin Interface & Hook Specifications
- **Description**: Formal hook specifications for extending SQLPhantom behaviors using Python protocol interfaces.
- **User Value**: Enables community and enterprise extensions without modifying core source code.
- **Dependencies**: Python standard library `typing`.
- **Acceptance Criteria**: Defines hooks for `on_scan_init`, `on_target_probe`, `on_vulnerability_found`, `on_scan_complete`.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_plugin_hooks.py`

### PLUG-002: Pre-Scan Request Modifier Hook
- **Description**: Plugin hook enabling programmatic modification of target requests before engine dispatch (e.g. signing requests with HMAC or AWS SigV4).
- **User Value**: Supports complex enterprise authentication protocols not natively supported by sqlmap.
- **Dependencies**: [PLUG-001](file:///d:/Projects/SQLPhantom/FEATURES.md#plug-001-plugin-interface--hook-specifications), [HTTP-002](file:///d:/Projects/SQLPhantom/FEATURES.md#http-002-header--cookie-injection-configuration).
- **Acceptance Criteria**: Plugin can inspect and mutate headers/body before request is sent; logs mutations clearly.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_request_plugin.py`

### PLUG-003: Post-Scan Finding Notification Hook
- **Description**: Plugin hook triggering webhook notifications (Slack, Discord, Microsoft Teams, generic HTTP POST) when high-severity vulnerabilities are verified.
- **User Value**: Provides immediate alerting to security teams upon critical finding confirmation.
- **Dependencies**: [PLUG-001](file:///d:/Projects/SQLPhantom/FEATURES.md#plug-001-plugin-interface--hook-specifications), [FIND-001](file:///d:/Projects/SQLPhantom/FEATURES.md#find-001-vulnerability-data-model--ingestion).
- **Acceptance Criteria**: Triggers configured webhook payloads asynchronously without blocking scan completion.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_webhook_plugin.py`

### PLUG-004: Plugin Discovery & Safe Sandboxing
- **Description**: Discovery of installed plugins from user directories with exception isolation to prevent faulty plugins from crashing the host application.
- **User Value**: Keeps the core application resilient against third-party plugin bugs.
- **Dependencies**: [PLUG-001](file:///d:/Projects/SQLPhantom/FEATURES.md#plug-001-plugin-interface--hook-specifications).
- **Acceptance Criteria**: Catches and logs plugin exceptions without crashing UI or scan jobs; displays loaded plugins in settings.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_plugin_discovery.py`

---

## 12. Security & Compliance (Security)

### SEC-001: Credential & Header Redaction
- **Description**: Automatic filtering of sensitive HTTP headers (`Authorization`, `Cookie`, `X-Api-Key`), session tokens, and passwords before saving to database or displaying in UI logs.
- **User Value**: Protects credentials from exposure in shared logs, screenshots, and export files.
- **Dependencies**: [DEV-002](file:///d:/Projects/SQLPhantom/FEATURES.md#dev-002-pydantic-v2-domain-models).
- **Acceptance Criteria**: Masks matching values with `***REDACTED***` in stored records and UI displays; provides explicit operator reveal toggle.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_redaction.py`

### SEC-002: Secure Subprocess Execution with Parameter Sanitization
- **Description**: Safe subprocess management using explicit argument arrays, absolute executable paths, and avoidance of `shell=True`.
- **User Value**: Eliminates command injection risks when launching engine subprocesses or external tools.
- **Dependencies**: [ENG-001](file:///d:/Projects/SQLPhantom/FEATURES.md#eng-001-sqlmapapi-subprocess-lifecycle-supervisor).
- **Acceptance Criteria**: Validates all arguments; strictly avoids shell interpolation; passes arguments via sanitized list.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_subprocess_security.py`

### SEC-003: Local SQLite File Permissions & Storage Isolation
- **Description**: Applies restrictive operating system file permissions (`0600` on POSIX, ACL restrictions on Windows) to SQLite database files.
- **User Value**: Prevents unauthorized local users from reading sensitive assessment data or extracted dumps.
- **Dependencies**: [SESS-001](file:///d:/Projects/SQLPhantom/FEATURES.md#sess-001-sqlite-persistent-session-store).
- **Acceptance Criteria**: Creates SQLite files with restricted owner-only read/write permissions.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_file_permissions.py`

### SEC-004: Strict Input Validation via Pydantic v2
- **Description**: Comprehensive validation of all inputs, configuration options, and API responses using Pydantic v2 schemas.
- **User Value**: Prevents malformed inputs, type confusion, or injection into internal components.
- **Dependencies**: `pydantic>=2.0`.
- **Acceptance Criteria**: Enforces type safety, constraints, and valid ranges across all domain models; returns clean validation errors.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/unit/test_pydantic_validation.py`

### SEC-005: Authorized Testing Disclaimer & Operator Confirmation
- **Description**: Prominent legal warning dialog and required operator confirmation regarding authorization prior to initiating the first scan in any workspace.
- **User Value**: Ensures compliance with security assessment policies and legal testing mandates.
- **Dependencies**: [GUI-001](file:///d:/Projects/SQLPhantom/FEATURES.md#gui-001-main-application-shell--window-management), [TUI-001](file:///d:/Projects/SQLPhantom/FEATURES.md#tui-001-textual-main-application-frame).
- **Acceptance Criteria**: Scan initiation blocked until operator accepts legal responsibility; records acceptance timestamp in workspace metadata.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_disclaimer_confirmation.py`

---

## 13. Developer Infrastructure & Tooling (Developer)

### DEV-001: Typed Domain Event Bus
- **Description**: Central asynchronous event dispatcher for loosely-coupled communication between domain, application, storage, and UI layers.
- **User Value**: Enables clean separation of concerns and testability without tight coupling.
- **Dependencies**: Python standard library `asyncio`.
- **Acceptance Criteria**: Type-safe event registration and dispatch; error isolation so failing listeners do not break event delivery.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/unit/test_event_bus.py`

### DEV-002: Pydantic v2 Domain Models
- **Description**: Complete domain model hierarchy (`Target`, `Job`, `ScanConfig`, `Finding`, `Session`, `LogEntry`) defined with Pydantic v2.
- **User Value**: Guarantees data consistency, serialization support, and immutability where needed.
- **Dependencies**: `pydantic>=2.0`.
- **Acceptance Criteria**: All models pass strict type validation; support JSON schema generation and round-trip serialization.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/unit/test_domain_models.py`

### DEV-003: Pytest Test Harness & Fixtures
- **Description**: Comprehensive testing harness with unit, integration, and UI test fixtures, including mock `sqlmapapi` server and temporary SQLite databases.
- **User Value**: Enables fast, reliable automated test execution and regression prevention.
- **Dependencies**: `pytest>=8.0`, `pytest-asyncio>=0.23`, `pytest-qt>=4.2`.
- **Acceptance Criteria**: Test suite runs cleanly with `pytest`; provides isolated temp directories and mock servers.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/test_harness.py`

### DEV-004: Strict Mypy Static Type Checking
- **Description**: Complete codebase compliance with `mypy --strict`, enforcing type hints across all modules and tests.
- **User Value**: Eliminates entire classes of runtime type errors before execution.
- **Dependencies**: `mypy>=1.10`.
- **Acceptance Criteria**: `mypy src tests` passes with zero errors under `strict = true`.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: CI static analysis check.

### DEV-005: Ruff Linting & Formatting Enforcement
- **Description**: Standardized linting and code formatting configuration in `pyproject.toml` using Ruff.
- **User Value**: Enforces uniform code style, modern Python idioms, and rapid lint feedback.
- **Dependencies**: `ruff>=0.4`.
- **Acceptance Criteria**: `ruff check src tests` and `ruff format --check src tests` pass cleanly.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: CI static analysis check.

### DEV-006: CLI Entry Point Infrastructure
- **Description**: Unified command-line interface entry points (`sqlphantom`, `sqlphantom-gui`, `sqlphantom-tui`) mapped in `pyproject.toml`.
- **User Value**: Allows seamless invocation of CLI, GUI, or TUI commands after package installation.
- **Dependencies**: `hatchling`.
- **Acceptance Criteria**: Commands executable from PATH after `pip install -e .`; display help text and version cleanly.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/unit/test_cli_entrypoints.py`

---

## 14. Cross-Platform Compatibility (Cross-platform)

### PLAT-001: Windows 10/11 Path & Subprocess Support
- **Description**: First-class support for Windows environments, including PowerShell path separators, process creation flags (`CREATE_NO_WINDOW`), and Windows Terminal ANSI colors.
- **User Value**: Flawless execution on Windows operator workstations without POSIX emulation.
- **Dependencies**: Python standard library `os`, `sys`, `subprocess`.
- **Acceptance Criteria**: Spawns and manages `sqlmapapi` cleanly on Windows; paths correctly normalized; GUI renders natively.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_windows_compat.py`

### PLAT-002: POSIX / Linux Terminal & Qt Compatibility
- **Description**: Full Linux support across X11 and Wayland display servers, with responsive Textual TUI support in standard POSIX terminals.
- **User Value**: Seamless deployment on Kali Linux, Ubuntu, Debian, Arch Linux, and remote VPS servers.
- **Dependencies**: `PySide6>=6.6`, `textual>=0.40`.
- **Acceptance Criteria**: GUI runs on Wayland and X11 without segmentation faults; TUI renders cleanly across standard terminal emulators.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_linux_compat.py`

### PLAT-003: OS-Specific Configuration & Data Directory Resolution
- **Description**: Standard directory resolution adhering to OS conventions: `%LOCALAPPDATA%\sqlphantom` on Windows, `XDG_DATA_HOME` / `~/.local/share/sqlphantom` on Linux.
- **User Value**: Prevents workspace clutter and conforms to platform standards.
- **Dependencies**: Python standard library `pathlib`, `os`.
- **Acceptance Criteria**: Resolves appropriate data and config directories per platform; creates directories if missing.
- **Status**: `IN_PROGRESS`
- **Associated Tests**: `tests/unit/test_path_resolution.py`

### PLAT-004: Unicode & ANSI Console Handling across Shells
- **Description**: Proper encoding management guaranteeing clean UTF-8 output and ANSI formatting across PowerShell, cmd.exe, bash, and zsh.
- **User Value**: Prevents garbled console text, broken borders, and Unicode errors during scans.
- **Dependencies**: `rich>=13.0`.
- **Acceptance Criteria**: Detects console encoding capabilities; falls back gracefully to ASCII characters if terminal lacks Unicode support.
- **Status**: `PLANNED`
- **Associated Tests**: `tests/unit/test_console_encoding.py`

---

## Non-Goals

To maintain rigorous architectural focus, safety, and upstream maintainability, the following capabilities are explicitly declared as **Non-Goals** for SQLPhantom:

1. **No Custom SQL Injection Detection Engine**: SQLPhantom will **not** rewrite or reimplement the core SQL injection detection, heuristic, or payload generation logic. We rely directly on the mature, battle-tested upstream [sqlmap](https://github.com/sqlmapproject/sqlmap) engine via its REST API.
2. **No Anti-Virus / EDR Evasion or Weaponized Exploitation**: SQLPhantom is designed strictly as a security assessment and compliance tool. It will **not** include automated payload encryption, anti-analysis packing, rootkit deployment, or weaponized OS post-exploitation modules.
3. **No Autonomous Worming or Mass Scanning**: SQLPhantom will **not** implement autonomous worm-like propagation, blind mass internet sweeping, or automated attack escalation across networks.
4. **No Closed-Source Commercial Tier**: SQLPhantom is and will remain 100% free and open-source software under the GPL v2+ license. There will be no "enterprise-only" features, paywalled capabilities, or proprietary cloud telemetry backdoors.
5. **No Direct Monkey-Patching of Upstream sqlmap**: SQLPhantom interacts with upstream sqlmap exclusively through its process and REST API boundary (`sqlmapapi.py`). It will **not** import or monkey-patch sqlmap's internal global state (`conf`, `kb`) directly inside the UI process.
