"""Finding Deduplication and Aggregation Module for SQLPhantom.

Groups individual technique findings by (target_url, http_method, parameter)
into consolidated findings with composite severity, combined techniques, and
unified remediation guidance.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Sequence, Any
from pydantic import BaseModel, Field

from sqlphantom.domain.enums import Severity, FindingType
from sqlphantom.domain.models import Finding


class AggregatedFinding(BaseModel):
    """A consolidated vulnerability finding combining multiple injection techniques on the same parameter."""

    target_url: str
    parameter: str
    http_method: str = "GET"
    highest_severity: Severity = Severity.CRITICAL
    techniques: list[str] = Field(default_factory=list)
    finding_ids: list[str] = Field(default_factory=list)
    dbms: str | None = None
    titles: list[str] = Field(default_factory=list)
    remediation: str = ""
    findings: list[Finding] = Field(default_factory=list)

    @property
    def technique_summary(self) -> str:
        """Formatted comma-separated list of technique tags (e.g., 'Boolean, Error-based, UNION')."""
        return ", ".join(self.techniques) if self.techniques else "SQL Injection"


_SEVERITY_ORDER = {
    Severity.CRITICAL: 5,
    Severity.HIGH: 4,
    Severity.MEDIUM: 3,
    Severity.LOW: 2,
    Severity.INFORMATIONAL: 1,
}


def _get_sev_weight(s: Any) -> int:
    if isinstance(s, Severity):
        return _SEVERITY_ORDER.get(s, 0)
    s_str = str(s).lower()
    for sev_enum, weight in _SEVERITY_ORDER.items():
        if sev_enum.value.lower() == s_str or sev_enum.name.lower() == s_str:
            return weight
    return 0


_FINDING_TYPE_TAGS: dict[Any, str] = {
    FindingType.BOOLEAN_BASED_BLIND: "Boolean-based blind",
    FindingType.ERROR_BASED: "Error-based",
    FindingType.UNION_BASED: "UNION query",
    FindingType.TIME_BASED_BLIND: "Time-based blind",
    FindingType.STACKED_QUERIES: "Stacked queries",
    FindingType.OUT_OF_BAND: "Out-of-band",
    FindingType.BLIND_SQL_INJECTION: "Blind SQLi",
    FindingType.SQL_INJECTION: "Generic SQLi",
    "boolean_based_blind": "Boolean-based blind",
    "error_based": "Error-based",
    "union_based": "UNION query",
    "time_based_blind": "Time-based blind",
    "stacked_queries": "Stacked queries",
    "out_of_band": "Out-of-band",
    "blind_sql_injection": "Blind SQLi",
    "sql_injection": "Generic SQLi",
}


def aggregate_findings(findings: Sequence[Finding]) -> list[AggregatedFinding]:
    """Aggregate a collection of findings by (url, parameter).

    Consolidates techniques, identifies the highest severity, and links
    individual findings for unified triage.
    """
    if not findings:
        return []

    groups: dict[tuple[str, str], list[Finding]] = defaultdict(list)
    for f in findings:
        key = (f.url, f.parameter or "")
        groups[key].append(f)

    aggregated: list[AggregatedFinding] = []

    for (url, param), item_list in groups.items():
        # Compute highest severity
        highest_sev = max(
            item_list,
            key=lambda x: _get_sev_weight(x.severity),
        ).severity

        # Collect distinct technique tags
        technique_set: list[str] = []
        for item in item_list:
            ft = item.finding_type
            tag = _FINDING_TYPE_TAGS.get(ft)
            if not tag:
                if hasattr(ft, "value"):
                    tag = _FINDING_TYPE_TAGS.get(ft.value, str(ft.value))
                else:
                    tag = str(ft)

            if tag not in technique_set:
                technique_set.append(tag)

        # Collect DBMS
        dbms = next((item.dbms for item in item_list if item.dbms), None)

        # Collect titles
        titles = [item.title for item in item_list if item.title]

        # Remediation
        remediation = next((item.remediation for item in item_list if item.remediation), "")

        aggregated.append(
            AggregatedFinding(
                target_url=url,
                parameter=param,
                highest_severity=highest_sev,
                techniques=technique_set,
                finding_ids=[item.id for item in item_list],
                dbms=dbms,
                titles=titles,
                remediation=remediation,
                findings=list(item_list),
            )
        )

    # Sort by severity descending
    aggregated.sort(key=lambda x: _get_sev_weight(x.highest_severity), reverse=True)
    return aggregated
