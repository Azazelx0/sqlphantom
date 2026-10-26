"""
Unit tests for SQLPhantom domain models.
"""

from datetime import datetime
import pytest
from pydantic import ValidationError

from sqlphantom.domain.enums import (
    AssessmentStage,
    Confidence,
    FindingType,
    HttpMethod,
    JobStatus,
    Severity,
)
from sqlphantom.domain.models import (
    AssessmentConfig,
    Finding,
    JobResult,
    Project,
    ScopeRule,
    Session,
    Target,
)


def test_target_creation_defaults():
    target = Target(url="http://testphp.vulnweb.com/listproducts.php?cat=1")
    assert target.url == "http://testphp.vulnweb.com/listproducts.php?cat=1"
    assert target.method == HttpMethod.GET
    assert target.headers == {}
    assert target.cookies == {}
    assert target.data is None


def test_target_post_with_data():
    target = Target(
        url="https://example.com/api/login",
        method=HttpMethod.POST,
        headers={"Content-Type": "application/json"},
        data='{"user":"admin"}',
    )
    assert target.method == HttpMethod.POST
    assert target.headers["Content-Type"] == "application/json"


def test_scope_rule_defaults():
    scope = ScopeRule(allowed_domains=["example.com"])
    assert scope.allowed_domains == ["example.com"]
    assert scope.allowed_url_patterns == []
    assert scope.block_private_ips is True


def test_assessment_config_validation():
    target = Target(url="http://example.com/item?id=5")
    scope = ScopeRule(allowed_domains=["example.com"])
    config = AssessmentConfig(target=target, scope=scope, level=3, risk=2)

    assert config.level == 3
    assert config.risk == 2
    assert "BEUSTQ" in config.techniques

    # Out of range validation
    with pytest.raises(ValidationError):
        AssessmentConfig(target=target, scope=scope, level=6)

    with pytest.raises(ValidationError):
        AssessmentConfig(target=target, scope=scope, risk=0)


def test_finding_creation():
    finding = Finding(
        finding_type=FindingType.ERROR_BASED,
        severity=Severity.HIGH,
        confidence=Confidence.CONFIRMED,
        parameter="id",
        payload="id=1' AND 1=1 --",
        url="http://example.com/item?id=1",
        title="Error-based injection in parameter 'id'",
        description="Detailed description",
        evidence="MySQL error syntax",
    )
    assert finding.id is not None
    assert finding.finding_type == FindingType.ERROR_BASED
    assert isinstance(finding.discovered_at, datetime)


def test_project_and_session_serialization():
    target = Target(url="http://example.com/search")
    project = Project(name="Audit Lab", targets=[target])
    assert len(project.targets) == 1
    assert project.name == "Audit Lab"

    scope = ScopeRule(allowed_domains=["example.com"])
    config = AssessmentConfig(target=target, scope=scope)
    session = Session(project_id=project.id, config=config)

    assert session.project_id == project.id
    dumped = session.model_dump(mode="json")
    assert dumped["project_id"] == project.id
    assert "config" in dumped
