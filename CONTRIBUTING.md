# Contributing to SQLPhantom

Thank you for your interest in contributing to **SQLPhantom**! We welcome bug fixes, documentation improvements, architectural enhancements, and feature implementations from the security and developer communities.

As an open-source security tool built on upstream sqlmap, we maintain high standards for code quality, type safety, test coverage, and ethical security practices.

---

## 1. Development Environment Setup

### Prerequisites
- **Python**: Version `3.11` or higher (`3.11`, `3.12`, `3.13`, `3.14`).
- **Git**: Configured with standard line endings and commit identity.

### Clone & Local Installation

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/Azazelx0/sqlphantom.git
   cd sqlphantom
   ```

2. **Create and activate a dedicated virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install SQLPhantom with development dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -e ".[dev]"
   ```
   This installs runtime dependencies (`PySide6`, `textual`, `pydantic`, `rich`, `httpx`) along with developer tools (`pytest`, `pytest-asyncio`, `pytest-qt`, `ruff`, `mypy`).

4. **Verify the development environment**:
   ```bash
   ruff check src tests
   mypy src tests
   pytest
   ```

---

## 2. Coding Standards & Guidelines

### Python Version & Modern Idioms
- Target **Python 3.11+**. Use modern Python features:
  - Structural pattern matching (`match` / `case`) where appropriate.
  - Standard collection type annotations (`list[str]`, `dict[str, int]`, `tuple[int, ...]`) instead of `typing.List`, `typing.Dict`.
  - Union syntax `X | Y` instead of `Union[X, Y]` and `X | None` instead of `Optional[X]`.
  - Self-documenting exception groups and enhanced tracebacks.

### Static Typing with Mypy
- SQLPhantom enforces **strict static typing** across all production modules (`src/`) and test suites (`tests/`).
- Every function, method, and class attribute must include explicit type annotations.
- Run type checks locally before submitting code:
  ```bash
  mypy src tests
  ```
- Submissions with unresolved Mypy errors or `# type: ignore` without inline rationale will be rejected.

### Linting and Code Formatting with Ruff
- We use **Ruff** for both linting and automated formatting. Configuration is defined in [`pyproject.toml`](file:///d:/Projects/SQLPhantom/pyproject.toml):
  - Line length limit: **100 characters**.
  - Enabled rules: `E` (pycodestyle errors), `F` (pyflakes), `W` (warnings), `I` (isort imports), `N` (pep8-naming), `UP` (pyupgrade), `B` (flake8-bugbear), `A` (flake8-builtins), `SIM` (flake8-simplify).
- Format and check your code before committing:
  ```bash
  # Check for lint issues
  ruff check src tests

  # Automatically fix fixable issues
  ruff check --fix src tests

  # Format source code
  ruff format src tests
  ```

### Documentation & Docstrings
- All public modules, classes, and functions must include Google-style or Sphinx-style docstrings.
- Docstrings should clearly explain the purpose, parameters, return types, and exceptions raised:
  ```python
  def calculate_job_duration(start_time: float, end_time: float | None = None) -> float:
      """Calculate the total elapsed execution duration of an assessment job.

      Args:
          start_time: Unix timestamp marking scan initiation.
          end_time: Optional Unix timestamp marking termination; defaults to current time.

      Returns:
          Total elapsed execution duration in seconds.

      Raises:
          ValueError: If end_time is chronologically earlier than start_time.
      """
  ```

---

## 3. Testing Practices

All new code must be accompanied by comprehensive automated tests.

### Test Directory Layout
```
tests/
├── unit/               # Fast, isolated tests for domain models, mappers, and utilities
├── integration/        # Tests verifying SQLite storage, REST client, and subprocess supervisor
├── gui/                # PySide6 desktop interface tests using pytest-qt
├── tui/                # Textual console interface tests using Textual test pilots
└── lab/                # Integration tests running against controlled vulnerable testbeds
```

### Running the Test Suite
```bash
# Run all tests
pytest

# Run only unit tests (fast feedback loop)
pytest tests/unit

# Run with test coverage report
pytest --cov=src/sqlphantom --cov-report=term-missing

# Run GUI-specific tests (requires display or virtual framebuffer)
pytest tests/gui

# Run TUI-specific tests
pytest tests/tui
```

### Testing Guidelines:
- **Fast Unit Tests**: Unit tests must not depend on network connectivity, external services, or long sleep delays. Use mock objects or dependency injection.
- **Async Tests**: Use `pytest-asyncio` with `@pytest.mark.asyncio` for asynchronous service and event bus testing.
- **Temporary State**: Always use pytest's `tmp_path` fixture for filesystem, SQLite, and configuration testing. Never write persistent test files to the host system.

---

## 4. Git Workflow & Branch Strategy

### Branch Naming Conventions
Prefix your branch name with a standard category indicator:

| Prefix | Usage | Example |
| :--- | :--- | :--- |
| `feat/` | New functionality or user-facing feature | `feat/job-pause-resume` |
| `fix/` | Bug fix or regression repair | `fix/port-collision-retry` |
| `docs/` | Documentation additions or edits | `docs/update-architecture` |
| `refactor/` | Code structure change without altering functionality | `refactor/event-bus-dispatch` |
| `test/` | Adding or improving test coverage | `test/sqlite-concurrency` |
| `chore/` | Tooling, build config, or dependency updates | `chore/bump-httpx-version` |

### Commit Message Guidelines
We follow the **Conventional Commits** specification:

```
<type>(<scope>): <short description>

[optional detailed explanation body]

[optional issue reference]
```

Examples:
- `feat(engine): implement task option mapping for dbms fingerprinting`
- `fix(storage): resolve WAL lock deadlock on concurrent job writes`
- `docs(usage): add troubleshooting instructions for Linux Wayland libraries`

---

## 5. Pull Request (PR) Process

1. **Keep PRs Focused**: Each pull request should address a single cohesive feature, bug fix, or refactoring task. Avoid bundling unrelated changes.
2. **Sync with Main**: Rebase your feature branch against `main` before submitting your PR to minimize merge conflicts:
   ```bash
   git fetch origin
   git rebase origin/main
   ```
3. **Run Local Quality Verification**: Ensure that the complete quality check passes cleanly:
   ```bash
   ruff check src tests
   ruff format --check src tests
   mypy src tests
   pytest
   ```
4. **Submit Pull Request**: Open a pull request against the `main` branch. Provide a clear summary of your changes, reference any related issue numbers (e.g. `Fixes #42`), and describe manual testing performed.
5. **Code Review**: Address reviewer feedback promptly. Once approved and CI checks pass, maintainers will merge your pull request.

---

## 6. Code Review Checklist

Reviewers and contributors should verify the following before merging:

- [ ] **Architecture**: Does the change respect layer boundaries? (e.g., Domain has zero outer dependencies; UI depends only on Application).
- [ ] **Engine Isolation**: Does the code communicate with sqlmap via the REST API rather than monkey-patching or importing sqlmap internals?
- [ ] **Type Annotations**: Are all functions, methods, and classes typed, and does `mypy src tests` pass without errors?
- [ ] **Testing**: Are there corresponding unit or integration tests with meaningful assertions?
- [ ] **Scope Guardrails**: If the change touches target dispatch, are scope checks enforced?
- [ ] **Secret Redaction**: Are sensitive headers, tokens, and credentials masked in logs and reports?
- [ ] **Upstream Attribution**: Is upstream sqlmap attribution preserved without modifying pristine submodule files?
- [ ] **Cross-Platform**: Does the code work on both Windows (pathing, subprocess flags) and Linux?
