"""
Integration tests for sqlmapapi subprocess supervisor, REST client, and engine adapter.
"""

import time
import pytest

from sqlphantom.domain.enums import HttpMethod
from sqlphantom.domain.models import AssessmentConfig, ScopeRule, Target
from sqlphantom.engine.client import SqlmapApiClient
from sqlphantom.engine.process import SqlmapProcessSupervisor, find_free_port
from sqlphantom.engine.sqlmap_adapter import SqlmapEngineAdapter


def test_free_port_finder():
    port = find_free_port()
    assert port > 1024
    assert port < 65535


def test_sqlmapapi_supervisor_and_client_lifecycle():
    """Verify sqlmapapi server can be launched, queried via REST client, and cleanly stopped."""
    supervisor = SqlmapProcessSupervisor(host="127.0.0.1")
    try:
        started = supervisor.start(timeout=10.0)
        assert started is True
        assert supervisor.is_port_listening() is True

        client = SqlmapApiClient(
            base_url=supervisor.base_url,
            username=supervisor.username,
            password=supervisor.password,
        )

        # 1. Create task
        task_id = client.new_task()
        assert task_id is not None
        assert len(task_id) > 0

        # 2. Check task status
        status = client.get_status(task_id)
        assert status.get("status") in ("not running", "running", "terminated")

        # 3. Delete task
        deleted = client.delete_task(task_id)
        assert deleted is True

    finally:
        supervisor.stop()
        assert supervisor.process is None


def test_sqlmap_engine_adapter_options_translation():
    """Verify AssessmentConfig converts cleanly into sqlmap options dictionary."""
    target = Target(
        url="http://testphp.vulnweb.com/listproducts.php?cat=1",
        method=HttpMethod.POST,
        data="cat=1&mode=search",
        cookies={"auth": "secret_cookie"},
        headers={"User-Agent": "SQLPhantom-Tester"},
    )
    scope = ScopeRule(allowed_domains=["vulnweb.com"])
    config = AssessmentConfig(
        target=target,
        scope=scope,
        level=3,
        risk=2,
        threads=4,
        dbms="PostgreSQL",
        tamper_scripts=["space2comment", "randomcase"],
    )

    adapter = SqlmapEngineAdapter()
    opts = adapter._translate_config(config)

    assert opts["url"] == "http://testphp.vulnweb.com/listproducts.php?cat=1"
    assert opts["method"] == "POST"
    assert opts["data"] == "cat=1&mode=search"
    assert opts["level"] == 3
    assert opts["risk"] == 2
    assert opts["threads"] == 4
    assert opts["dbms"] == "PostgreSQL"
    assert "space2comment,randomcase" in opts["tamper"]
    assert "auth=secret_cookie" in opts["cookie"]
    assert "User-Agent: SQLPhantom-Tester" in opts["headers"]
