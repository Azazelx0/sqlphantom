"""
Unit tests for SQLPhantom reporting engine, redaction, and session comparison.
"""

from sqlphantom.domain.enums import Confidence, FindingType, ReportFormat, Severity
from sqlphantom.domain.models import (
    AssessmentConfig,
    Finding,
    JobResult,
    ScopeRule,
    Session,
    Target,
)
from sqlphantom.reporting.generator import (
    ReportGenerator,
    compare_sessions,
    redact_sensitive_data,
)


def test_redact_sensitive_data():
    raw_text = (
        "Authorization: Bearer secret_jwt_token_12345\n"
        "Cookie: PHPSESSID=d9a8f7e6c5b4; session_id=sess_9999\n"
        '{"api_key": "prod_key_xyz", "password": "SuperSecretPassword123"}'
    )
    redacted = redact_sensitive_data(raw_text)

    assert "secret_jwt_token_12345" not in redacted
    assert "[REDACTED_TOKEN]" in redacted
    assert "d9a8f7e6c5b4" not in redacted
    assert "[REDACTED_COOKIE]" in redacted
    assert "SuperSecretPassword123" not in redacted
    assert "[REDACTED_PASSWORD]" in redacted
    assert "prod_key_xyz" not in redacted


def test_report_generator_formats():
    gen = ReportGenerator()
    finding = Finding(
        finding_type=FindingType.ERROR_BASED,
        severity=Severity.CRITICAL,
        confidence=Confidence.CONFIRMED,
        parameter="user_id",
        payload="user_id=1' AND (SELECT 1 FROM (SELECT(SLEEP(5)))a)--",
        url="http://vulnweb.com/profile?user_id=1",
        title="Critical Error-based SQL Injection",
        description="Leaked query syntax error",
        evidence="Authorization: Bearer secret_key_test",
        remediation="Use prepared statements",
    )

    # Test Markdown
    md = gen.generate([finding], fmt=ReportFormat.MARKDOWN, redact=True)
    assert "# SQLPhantom Security Assessment Report" in md
    assert "Critical Error-based SQL Injection" in md
    assert "secret_key_test" not in md
    assert "[REDACTED_TOKEN]" in md

    # Test JSON
    json_out = gen.generate([finding], fmt=ReportFormat.JSON, redact=True)
    assert '"findings_count": 1' in json_out
    assert "secret_key_test" not in json_out

    # Test HTML
    html_out = gen.generate([finding], fmt=ReportFormat.HTML, redact=True)
    assert "<!DOCTYPE html>" in html_out
    assert "Critical Error-based SQL Injection" in html_out


def test_compare_sessions():
    target = Target(url="http://vulnweb.com/item?id=1")
    scope = ScopeRule(allowed_domains=["vulnweb.com"])
    config = AssessmentConfig(target=target, scope=scope)

    f_common = Finding(
        finding_type=FindingType.BOOLEAN_BASED_BLIND,
        severity=Severity.HIGH,
        parameter="id",
        payload="id=1 AND 1=1",
        url="http://vulnweb.com/item?id=1",
        title="Boolean Blind",
    )
    f_resolved = Finding(
        finding_type=FindingType.TIME_BASED_BLIND,
        severity=Severity.MEDIUM,
        parameter="cat",
        payload="cat=1 SLEEP(5)",
        url="http://vulnweb.com/item?id=1",
        title="Time Blind",
    )
    f_new = Finding(
        finding_type=FindingType.UNION_BASED,
        severity=Severity.CRITICAL,
        parameter="sort",
        payload="sort=UNION SELECT 1,2",
        url="http://vulnweb.com/item?id=1",
        title="Union Injection",
    )

    baseline_result = JobResult(job_id="j-base", findings=[f_common, f_resolved])
    current_result = JobResult(job_id="j-curr", findings=[f_common, f_new])

    sess_a = Session(id="sess-a", project_id="p-1", config=config, result=baseline_result)
    sess_b = Session(id="sess-b", project_id="p-1", config=config, result=current_result)

    diff = compare_sessions(sess_a, sess_b)

    assert len(diff.new_findings) == 1
    assert diff.new_findings[0].title == "Union Injection"

    assert len(diff.resolved_findings) == 1
    assert diff.resolved_findings[0].title == "Time Blind"

    assert len(diff.common_findings) == 1
    assert diff.common_findings[0].title == "Boolean Blind"
