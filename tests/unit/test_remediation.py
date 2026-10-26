"""
Unit tests for the Defensive Remediation Assistant.
"""

from sqlphantom.domain.enums import FindingType, Severity, Confidence
from sqlphantom.domain.models import Finding
from sqlphantom.reporting.remediation import RemediationAssistant


def test_remediation_cwe_details():
    cwe = RemediationAssistant.get_cwe_details()
    assert cwe["cwe_id"] == "CWE-89"
    assert "A03:2021" in cwe["owasp_top_10"]
    assert "V5.3.1" in cwe["owasp_asvs"]


def test_remediation_snippets_generation():
    finding = Finding(
        finding_type=FindingType.BOOLEAN_BASED_BLIND,
        severity=Severity.CRITICAL,
        confidence=Confidence.CONFIRMED,
        parameter="user_id",
        payload="1' AND 1=1 --",
        url="https://example.com/api/profile",
        title="Boolean-based blind SQL injection in user_id",
    )

    snippets = RemediationAssistant.generate_snippets(finding)
    assert "python_psycopg" in snippets
    assert "python_sqlalchemy" in snippets
    assert "nodejs_pg" in snippets
    assert "java_jdbc" in snippets
    assert "php_pdo" in snippets
    assert "csharp_ef" in snippets

    # Verify parameterized placeholder inclusion
    assert "%s" in snippets["python_psycopg"]
    assert ":param_val" in snippets["python_sqlalchemy"]
    assert "$1" in snippets["nodejs_pg"]
    assert "?" in snippets["java_jdbc"]
    assert ":param" in snippets["php_pdo"]
    assert "FromSqlInterpolated" in snippets["csharp_ef"]
