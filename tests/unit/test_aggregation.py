"""
Unit tests for Finding Deduplication and Aggregation.
"""

from sqlphantom.domain.enums import FindingType, Severity, Confidence
from sqlphantom.domain.models import Finding
from sqlphantom.domain.aggregation import aggregate_findings


def test_aggregate_empty_findings():
    assert aggregate_findings([]) == []


def test_aggregate_multi_technique_same_parameter():
    f1 = Finding(
        finding_type=FindingType.BOOLEAN_BASED_BLIND,
        severity=Severity.HIGH,
        confidence=Confidence.CONFIRMED,
        parameter="account_id",
        payload="1' AND 1=1 --",
        url="https://app.test/items",
        title="Boolean injection",
    )
    f2 = Finding(
        finding_type=FindingType.ERROR_BASED,
        severity=Severity.CRITICAL,
        confidence=Confidence.CONFIRMED,
        parameter="account_id",
        payload="1' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT @@version),0x3a,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.TABLES GROUP BY x)a) --",
        url="https://app.test/items",
        title="Error-based injection",
    )
    f3 = Finding(
        finding_type=FindingType.TIME_BASED_BLIND,
        severity=Severity.MEDIUM,
        confidence=Confidence.FIRM,
        parameter="category",
        payload="test' WAITFOR DELAY '0:0:5' --",
        url="https://app.test/items",
        title="Time-based injection in category",
    )

    aggregated = aggregate_findings([f1, f2, f3])
    assert len(aggregated) == 2

    # First aggregated group should be account_id because highest severity is CRITICAL
    account_agg = next(a for a in aggregated if a.parameter == "account_id")
    assert account_agg.highest_severity == Severity.CRITICAL
    assert len(account_agg.findings) == 2
    assert "Boolean-based blind" in account_agg.techniques
    assert "Error-based" in account_agg.techniques

    # Second group is category
    cat_agg = next(a for a in aggregated if a.parameter == "category")
    assert cat_agg.highest_severity == Severity.MEDIUM
    assert len(cat_agg.findings) == 1
    assert "Time-based blind" in cat_agg.techniques
