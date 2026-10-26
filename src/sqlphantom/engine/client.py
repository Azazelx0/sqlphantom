"""
SQLPhantom HTTP REST client communicating with sqlmapapi daemon endpoints.
"""

from typing import Any
import httpx


class SqlmapApiClient:
    """
    Client for interacting with upstream sqlmapapi.py endpoints.
    Provides synchronous operations over HTTP with robust timeout handling.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8775",
        username: str | None = None,
        password: str | None = None,
        timeout: float = 15.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout

    def _client(self) -> httpx.Client:
        auth = (self.username, self.password) if (self.username and self.password) else None
        return httpx.Client(base_url=self.base_url, auth=auth, timeout=self.timeout)

    def new_task(self) -> str:
        """Create a new session task and return its taskid."""
        with self._client() as client:
            resp = client.get("/task/new")
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success"):
                raise RuntimeError(f"Failed to create new task: {data}")
            return data["taskid"]

    def delete_task(self, task_id: str) -> bool:
        """Delete an existing task."""
        with self._client() as client:
            resp = client.get(f"/task/{task_id}/delete")
            if resp.status_code == 200:
                return resp.json().get("success", False)
            return False

    def start_scan(self, task_id: str, options: dict[str, Any]) -> bool:
        """Initiate scan execution for a task with specified sqlmap options."""
        with self._client() as client:
            resp = client.post(f"/scan/{task_id}/start", json=options)
            resp.raise_for_status()
            return resp.json().get("success", False)

    def get_status(self, task_id: str) -> dict[str, Any]:
        """Query scan status (e.g. status='running' or 'terminated')."""
        with self._client() as client:
            resp = client.get(f"/scan/{task_id}/status")
            resp.raise_for_status()
            return resp.json()

    def get_data(self, task_id: str) -> list[dict[str, Any]]:
        """Retrieve confirmed vulnerabilities and extracted injection data."""
        with self._client() as client:
            resp = client.get(f"/scan/{task_id}/data")
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])

    def get_log(self, task_id: str) -> list[dict[str, Any]]:
        """Retrieve terminal log messages recorded by the engine."""
        with self._client() as client:
            resp = client.get(f"/scan/{task_id}/log")
            resp.raise_for_status()
            data = resp.json()
            return data.get("log", [])

    def stop_scan(self, task_id: str) -> bool:
        """Request scan to stop gracefully."""
        with self._client() as client:
            resp = client.get(f"/scan/{task_id}/stop")
            if resp.status_code == 200:
                return resp.json().get("success", False)
            return False

    def kill_scan(self, task_id: str) -> bool:
        """Force termination of an active scan task."""
        with self._client() as client:
            resp = client.get(f"/scan/{task_id}/kill")
            if resp.status_code == 200:
                return resp.json().get("success", False)
            return False
