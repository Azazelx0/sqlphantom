"""
SQLPhantom subprocess supervisor managing the upstream sqlmapapi daemon.
"""

import logging
from pathlib import Path
import socket
import subprocess
import sys
import time

logger = logging.getLogger(__name__)


def find_free_port() -> int:
    """Find and return an available local TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class SqlmapProcessSupervisor:
    """
    Manages the lifecycle of an isolated sqlmapapi daemon subprocess.
    Ensures safe initialization, health checking, and clean termination.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int | None = None,
        username: str = "sqlphantom",
        password: str = "phantom_secret_token",
        sqlmap_dir: Path | None = None,
    ):
        self.host = host
        self.port = port or find_free_port()
        self.username = username
        self.password = password
        self.sqlmap_dir = sqlmap_dir or (Path(__file__).resolve().parents[3] / "sqlmap")
        self.process: subprocess.Popen | None = None

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def is_port_listening(self) -> bool:
        """Check if server port is accepting TCP connections."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            try:
                s.connect((self.host, self.port))
                return True
            except (ConnectionRefusedError, socket.timeout, OSError):
                return False

    def start(self, timeout: float = 10.0) -> bool:
        """
        Launch the sqlmapapi server subprocess and await readiness.
        """
        if self.is_port_listening():
            logger.info("sqlmapapi already listening on %s", self.base_url)
            return True

        api_script = self.sqlmap_dir / "sqlmapapi.py"
        if not api_script.exists():
            raise FileNotFoundError(f"sqlmapapi.py not found at {api_script}")

        cmd = [
            sys.executable,
            str(api_script),
            "-s",
            "-H",
            self.host,
            "-p",
            str(self.port),
            f"--username={self.username}",
            f"--password={self.password}",
        ]

        logger.info("Starting sqlmapapi: %s", " ".join(cmd))
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )

        # Wait for socket to become active
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.process.poll() is not None:
                _, stderr = self.process.communicate()
                self.process = None
                raise RuntimeError(f"sqlmapapi exited prematurely: {stderr}")
            if self.is_port_listening():
                logger.info("sqlmapapi successfully started at %s", self.base_url)
                return True
            time.sleep(0.1)

        self.stop()
        raise TimeoutError(f"Timed out waiting for sqlmapapi to start on {self.base_url}")

    def stop(self) -> None:
        """Terminate the sqlmapapi daemon cleanly."""
        if self.process:
            if self.process.poll() is None:
                logger.info("Stopping sqlmapapi daemon...")
                self.process.terminate()
                try:
                    self.process.wait(timeout=3.0)
                except subprocess.TimeoutExpired:
                    logger.warning("Forcing kill on sqlmapapi daemon...")
                    self.process.kill()
                    self.process.wait()
            self.process = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
