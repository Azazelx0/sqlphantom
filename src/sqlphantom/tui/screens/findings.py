"""
SQLPhantom TUI Findings and Evidence triage screen.
"""

from pathlib import Path
from typing import Any
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Label, Static

from sqlphantom.domain.enums import ReportFormat
from sqlphantom.domain.models import Finding
from sqlphantom.domain.aggregation import aggregate_findings
from sqlphantom.reporting.remediation import RemediationAssistant


class FindingsScreen(Static):
    """
    Master-detail triage interface for inspecting confirmed vulnerabilities,
    technical payloads, extracted evidence, defensive code guidance,
    and exporting formal reports.
    """

    def __init__(self, id: str | None = None):
        super().__init__(id=id)
        self._findings_map: dict[str, Finding] = {}
        self._selected_finding_id: str | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            # Screen Title & Export Bar
            with Horizontal(classes="card-box"):
                yield Label("Confirmed Findings & Evidence Triage", classes="card-title")
                yield Button("Export Markdown", id="btn-export-md", classes="btn-secondary")
                yield Button("Export JSON", id="btn-export-json", classes="btn-secondary")
                yield Button("Export HTML", id="btn-export-html", classes="btn-secondary")

            yield Label("", id="findings-status-label", classes="kpi-title")

            # Master-Detail Layout
            with Horizontal():
                # Left Master List (40% width)
                with Vertical(classes="card-box"):
                    yield Label("Discovered Vulnerabilities:", classes="kpi-title")
                    yield DataTable(id="findings-table")

                # Right Detail View (60% width)
                with Vertical(classes="detail-pane", id="findings-detail-pane"):
                    yield Label("Select a finding to inspect verification evidence.", id="detail-title", classes="card-title")
                    yield Label("", id="detail-severity")
                    yield Label("", id="detail-param")
                    yield Label("", id="detail-payload")
                    yield Label("", id="detail-evidence")
                    yield Label("", id="detail-remediation")

    def on_mount(self) -> None:
        table = self.query_one("#findings-table", DataTable)
        table.add_columns("Severity", "Type", "Param", "Title")
        self.refresh_findings()

    def refresh_findings(self) -> None:
        table = self.query_one("#findings-table", DataTable)
        table.clear()
        self._findings_map.clear()

        findings: list[Finding] = []

        # Check active job findings
        job_id = getattr(self.app, "active_job_id", None)
        if job_id and hasattr(self.app, "assessment_service"):
            findings.extend(self.app.assessment_service.get_findings(job_id))

        # Check repository findings
        if hasattr(self.app, "finding_repo") and self.app.finding_repo:
            repo_findings = self.app.finding_repo.list_all()
            for rf in repo_findings:
                if rf.id not in [f.id for f in findings]:
                    findings.append(rf)

        for f in findings:
            self._findings_map[f.id] = f
            table.add_row(
                str(f.severity),
                str(f.finding_type),
                f.parameter,
                f.title,
                key=f.id,
            )

        if findings:
            agg = aggregate_findings(findings)
            self.display_finding(findings[0])
            self.query_one("#findings-status-label", Label).update(
                f"Showing {len(findings)} confirmed finding(s) across {len(agg)} vulnerable parameter(s)."
            )
        else:
            self.query_one("#findings-status-label", Label).update(
                "No findings yet. Run an assessment to populate vulnerabilities."
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_key = event.row_key.value
        if row_key and row_key in self._findings_map:
            self.display_finding(self._findings_map[row_key])

    def display_finding(self, finding: Finding) -> None:
        self._selected_finding_id = finding.id
        cwe = RemediationAssistant.get_cwe_details()
        snippets = RemediationAssistant.generate_snippets(finding)

        self.query_one("#detail-title", Label).update(f"[bold #A855F7]{finding.title}[/bold #A855F7]")
        self.query_one("#detail-severity", Label).update(
            f"[bold]Severity:[/bold] [red]{finding.severity}[/red] (Confidence: {finding.confidence})"
        )
        self.query_one("#detail-param", Label).update(
            f"[bold]Target Endpoint:[/bold] {finding.url} (Param: [cyan]{finding.parameter}[/cyan])"
        )
        self.query_one("#detail-payload", Label).update(
            f"[bold]Observed Payload Pattern:[/bold]\n[yellow]{finding.payload}[/yellow]"
        )
        self.query_one("#detail-evidence", Label).update(
            f"[bold]Technical Evidence / Reflection:[/bold]\n[green]{finding.evidence or 'Payload triggered differential response.'}[/green]"
        )
        
        # Display CWE and Defensive Python snippet preview
        preview_code = snippets.get("python_sqlalchemy", "").strip().split("\n")[:6]
        preview_str = "\n".join(preview_code)
        self.query_one("#detail-remediation", Label).update(
            f"[bold]Defensive Remediation ({cwe['cwe_id']}):[/bold]\n"
            f"[cyan]{cwe['owasp_asvs']}[/cyan]\n"
            f"[dim]{preview_str}[/dim]"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        status_lbl = self.query_one("#findings-status-label", Label)
        findings = list(self._findings_map.values())

        if not findings:
            status_lbl.update("[yellow]Cannot export: no findings available[/yellow]")
            return

        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        app: Any = self.app

        if event.button.id == "btn-export-md":
            content = app.report_service.generate_report(findings, fmt=ReportFormat.MARKDOWN)
            out_file = report_dir / "assessment_report.md"
            out_file.write_text(content, encoding="utf-8")
            status_lbl.update(f"[green]Exported Markdown report to {out_file.absolute()}[/green]")

        elif event.button.id == "btn-export-json":
            content = app.report_service.generate_report(findings, fmt=ReportFormat.JSON)
            out_file = report_dir / "assessment_report.json"
            out_file.write_text(content, encoding="utf-8")
            status_lbl.update(f"[green]Exported JSON report to {out_file.absolute()}[/green]")

        elif event.button.id == "btn-export-html":
            content = app.report_service.generate_report(findings, fmt=ReportFormat.HTML)
            out_file = report_dir / "assessment_report.html"
            out_file.write_text(content, encoding="utf-8")
            status_lbl.update(f"[green]Exported HTML report to {out_file.absolute()}[/green]")
