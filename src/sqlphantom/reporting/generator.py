"""
SQLPhantom comprehensive reporting pipeline with sensitive credential redaction,
evidence normalization, and session comparison.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from sqlphantom.domain.enums import ReportFormat
from sqlphantom.domain.models import Finding, Session


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# Common patterns for sensitive values in HTTP exchanges
REDACTION_PATTERNS = [
    (re.compile(r'(?i)(authorization:\s*bearer\s+)([A-Za-z0-9_\-\.]+)', re.IGNORECASE), r'\1[REDACTED_TOKEN]'),
    (re.compile(r'(?i)(authorization:\s*basic\s+)([A-Za-z0-9+/=]+)', re.IGNORECASE), r'\1[REDACTED_CREDENTIALS]'),
    (re.compile(r'(?i)(password["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE), r'\1[REDACTED_PASSWORD]\3'),
    (re.compile(r'(?i)(api[_-]?key["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE), r'\1[REDACTED_KEY]\3'),
    (re.compile(r'(?i)(session[_-]?id["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE), r'\1[REDACTED_SESSION]\3'),
    (re.compile(r'(?i)(phpsessid|jsessionid|asp\.net_sessionid)=([^;,\s]+)', re.IGNORECASE), r'\1=[REDACTED_COOKIE]'),
]


def redact_sensitive_data(text: str) -> str:
    """
    Scrub credentials, tokens, session cookies, and API keys from raw text,
    requests, or responses prior to report export.
    """
    if not text:
        return text

    scrubbed = text
    for pattern, replacement in REDACTION_PATTERNS:
        scrubbed = pattern.sub(replacement, scrubbed)
    return scrubbed


class SessionDiff:
    """Represents differences and vulnerability drift between two assessment sessions."""

    def __init__(
        self,
        session_a_id: str,
        session_b_id: str,
        new_findings: list[Finding],
        resolved_findings: list[Finding],
        common_findings: list[Finding],
    ):
        self.session_a_id = session_a_id
        self.session_b_id = session_b_id
        self.new_findings = new_findings
        self.resolved_findings = resolved_findings
        self.common_findings = common_findings

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_baseline": self.session_a_id,
            "session_comparison": self.session_b_id,
            "new_count": len(self.new_findings),
            "resolved_count": len(self.resolved_findings),
            "common_count": len(self.common_findings),
            "new_findings": [f.model_dump(mode="json") for f in self.new_findings],
            "resolved_findings": [f.model_dump(mode="json") for f in self.resolved_findings],
            "common_findings": [f.model_dump(mode="json") for f in self.common_findings],
        }


def compare_sessions(baseline: Session, current: Session) -> SessionDiff:
    """
    Compare two assessment sessions, identifying newly introduced vulnerabilities,
    resolved issues, and persistent common findings.
    """
    base_findings = baseline.result.findings if (baseline.result and baseline.result.findings) else []
    curr_findings = current.result.findings if (current.result and current.result.findings) else []

    # Fingerprint finding by (parameter, finding_type, url)
    def fp(f: Finding) -> tuple[str, str, str]:
        return (f.parameter, str(f.finding_type), f.url)

    base_map = {fp(f): f for f in base_findings}
    curr_map = {fp(f): f for f in curr_findings}

    new_items = [curr_map[k] for k in curr_map if k not in base_map]
    resolved_items = [base_map[k] for k in base_map if k not in curr_map]
    common_items = [curr_map[k] for k in curr_map if k in base_map]

    return SessionDiff(
        session_a_id=baseline.id,
        session_b_id=current.id,
        new_findings=new_items,
        resolved_findings=resolved_items,
        common_findings=common_items,
    )


class ReportGenerator:
    """
    Generates formal security assessment reports in JSON, Markdown, and HTML formats
    with automatic sensitive credential redaction.
    """

    def generate(
        self,
        findings: list[Finding],
        title: str = "SQLPhantom Security Assessment Report",
        fmt: ReportFormat = ReportFormat.MARKDOWN,
        redact: bool = True,
    ) -> str:
        """Render findings into the requested output format."""
        processed_findings = []
        for f in findings:
            f_copy = f.model_copy()
            if redact:
                f_copy.payload = redact_sensitive_data(f_copy.payload)
                f_copy.evidence = redact_sensitive_data(f_copy.evidence)
            processed_findings.append(f_copy)

        if fmt == ReportFormat.JSON:
            return self._to_json(title, processed_findings)
        elif fmt == ReportFormat.MARKDOWN:
            return self._to_markdown(title, processed_findings)
        elif fmt == ReportFormat.HTML:
            return self._to_html(title, processed_findings)

        raise ValueError(f"Unsupported report format: {fmt}")

    def _to_json(self, title: str, findings: list[Finding]) -> str:
        data = {
            "title": title,
            "generated_at": _utc_now().isoformat(),
            "findings_count": len(findings),
            "findings": [f.model_dump(mode="json") for f in findings],
        }
        return json.dumps(data, indent=2)

    def _to_markdown(self, title: str, findings: list[Finding]) -> str:
        lines = [
            f"# {title}",
            f"**Generated:** {_utc_now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Total Findings:** {len(findings)}",
            "",
            "---",
            "",
        ]
        if not findings:
            lines.append("No security vulnerabilities were identified in the specified scope.")
        else:
            for idx, f in enumerate(findings, 1):
                lines.extend(
                    [
                        f"## {idx}. {f.title}",
                        f"- **Severity:** **{f.severity}** (Confidence: {f.confidence})",
                        f"- **Type:** `{f.finding_type}`",
                        f"- **Endpoint:** `{f.url}`",
                        f"- **Vulnerable Parameter:** `{f.parameter}`",
                        "",
                        "### Description",
                        f.description or "Automated SQL injection vulnerability detected by engine heuristics.",
                        "",
                        "### Technical Evidence & PoC",
                        f"```text\n{f.evidence or f.payload}\n```",
                        "",
                        "### Remediation Guidance",
                        f.remediation or "Ensure strict query parameterization and prepared statements.",
                        "",
                        "---",
                        "",
                    ]
                )
        return "\n".join(lines)

    def _to_html(self, title: str, findings: list[Finding]) -> str:
        logo_b64 = ""
        logo_file = Path("assets/logo.png")
        if not logo_file.exists():
            logo_file = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        if logo_file.exists():
            import base64
            logo_b64 = base64.b64encode(logo_file.read_bytes()).decode("utf-8")

        logo_img_tag = (
            f'<img src="data:image/png;base64,{logo_b64}" width="54" height="54" alt="SQLPhantom" style="border-radius: 6px;" />'
            if logo_b64
            else ""
        )

        rows = ""
        for f in findings:
            rows += f"""
            <div class="card">
                <h2>{f.title}</h2>
                <div class="tags">
                    <span class="badge {f.severity.lower()}">{f.severity}</span>
                    <span class="badge">{f.finding_type}</span>
                    <span class="badge">Param: {f.parameter}</span>
                </div>
                <p><strong>Endpoint:</strong> <code>{f.url}</code></p>
                <h3>Technical Evidence</h3>
                <pre><code>{f.evidence or f.payload}</code></pre>
                <h3>Remediation Guidance</h3>
                <p>{f.remediation or 'Ensure query parameterization.'}</p>
            </div>
            """

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0B0F19; color: #F8FAFC; padding: 2.5rem; }}
        h1 {{ color: #A855F7; margin: 0; }}
        .header {{ display: flex; align-items: center; gap: 16px; margin-bottom: 2rem; border-bottom: 1px solid #334155; padding-bottom: 1.5rem; }}
        .card {{ background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }}
        .tags {{ margin-bottom: 1rem; }}
        .badge {{ background: #334155; color: #F8FAFC; padding: 4px 8px; border-radius: 4px; font-size: 11px; margin-right: 6px; font-weight: bold; }}
        .badge.critical {{ background: #EF4444; color: #FFFFFF; }}
        .badge.high {{ background: #F97316; color: #FFFFFF; }}
        pre {{ background: #050811; border: 1px solid #334155; padding: 1rem; border-radius: 6px; color: #38BDF8; font-family: monospace; overflow-x: auto; }}
        code {{ color: #A855F7; }}
    </style>
</head>
<body>
    <div class="header">
        {logo_img_tag}
        <div>
            <h1>{title}</h1>
            <p style="margin: 4px 0 0 0; color: #94A3B8;">Generated: {_utc_now().strftime('%Y-%m-%d %H:%M:%S UTC')} | Total Findings: {len(findings)}</p>
        </div>
    </div>
    {rows if findings else "<p>No vulnerabilities identified.</p>"}
</body>
</html>"""
