"""
SQLPhantom local SQLite persistence and connection management.
"""

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
import sqlite3
import threading
from typing import Any, cast


class DatabaseManager:
    """
    Manages local SQLite database connections, schema migrations, and transactions.
    Configured with WAL mode and foreign key constraints for concurrent read performance.
    """

    def __init__(self, db_path: str | Path = ":memory:"):
        self.db_path = str(db_path)
        self._local = threading.local()
        self._lock = threading.Lock()
        self.initialize()

    def _create_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0,
        )
        conn.row_factory = sqlite3.Row
        # Enable WAL mode and foreign key enforcement
        if self.db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager yielding a thread-local database connection."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = self._create_connection()

        conn: sqlite3.Connection = self._local.conn
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def initialize(self) -> None:
        """Create database tables and required indexes if they do not exist."""
        schema = """
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            targets_json TEXT DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS findings (
            id TEXT PRIMARY KEY,
            job_id TEXT,
            finding_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            confidence TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            parameter TEXT NOT NULL,
            payload TEXT NOT NULL,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            evidence TEXT DEFAULT '',
            remediation TEXT DEFAULT '',
            analyst_notes TEXT DEFAULT '',
            dbms TEXT,
            discovered_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_findings_job ON findings(job_id);
        CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);

        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            config_json TEXT NOT NULL,
            result_json TEXT,
            created_at TEXT NOT NULL,
            notes TEXT DEFAULT '',
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project_id);

        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_events_job ON events(job_id);
        """
        with self.get_connection() as conn:
            conn.executescript(schema)
            # Safe migration for newly added columns on existing schemas
            try:
                conn.execute("ALTER TABLE findings ADD COLUMN status TEXT DEFAULT 'ACTIVE'")
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE findings ADD COLUMN analyst_notes TEXT DEFAULT ''")
            except Exception:
                pass

    def execute(self, query: str, params: tuple[Any, ...] | dict[str, Any] = ()) -> sqlite3.Cursor:
        """Execute a query within a transactional connection."""
        with self.get_connection() as conn:
            return conn.execute(query, params)

    def fetchone(self, query: str, params: tuple[Any, ...] | dict[str, Any] = ()) -> sqlite3.Row | None:
        """Execute a query and fetch the single matching row."""
        with self.get_connection() as conn:
            cur = conn.execute(query, params)
            return cast(sqlite3.Row | None, cur.fetchone())

    def fetchall(self, query: str, params: tuple[Any, ...] | dict[str, Any] = ()) -> list[sqlite3.Row]:
        """Execute a query and fetch all matching rows."""
        with self.get_connection() as conn:
            cur = conn.execute(query, params)
            return cur.fetchall()

    def close(self) -> None:
        """Close thread-local connection if present."""
        if hasattr(self._local, "conn") and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None
