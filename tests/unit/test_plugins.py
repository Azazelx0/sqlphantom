"""
Unit tests for SQLPhantom plugin contracts and registry.
"""

from sqlphantom.domain.enums import FindingType, Severity
from sqlphantom.domain.models import Finding
from sqlphantom.plugins.base import (
    FindingEnricherPlugin,
    PluginCategory,
    PluginMetadata,
    ReportExporterPlugin,
)
from sqlphantom.plugins.registry import PluginRegistry


class MockExporterPlugin(ReportExporterPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="mock_exporter",
            version="1.0.0",
            author="SQLPhantom Dev",
            description="Exports findings to custom CSV",
            category=PluginCategory.REPORT_EXPORTER,
        )

    def export(self, findings: list[Finding], title: str = "") -> str:
        lines = ["id,severity,parameter,title"]
        for f in findings:
            lines.append(f"{f.id},{f.severity},{f.parameter},{f.title}")
        return "\n".join(lines)


class MockEnricherPlugin(FindingEnricherPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="mock_enricher",
            version="1.0.0",
            author="SQLPhantom Dev",
            description="Adds CWE and CVSS scoring",
            category=PluginCategory.FINDING_ENRICHER,
        )

    def enrich(self, finding: Finding) -> Finding:
        f_copy = finding.model_copy()
        f_copy.description = f"{f_copy.description} [CWE-89 CVSS:9.8]"
        return f_copy


class FailingPlugin(FindingEnricherPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="failing_plugin",
            version="0.1.0",
            author="Tester",
            description="Always raises an exception",
            category=PluginCategory.FINDING_ENRICHER,
        )

    def enrich(self, finding: Finding) -> Finding:
        raise RuntimeError("Plugin intentional crash")


def test_plugin_registration_and_discovery():
    reg = PluginRegistry()
    exporter = MockExporterPlugin()
    enricher = MockEnricherPlugin()

    assert reg.register(exporter) is True
    assert reg.register(enricher) is True

    assert len(reg.list_plugins()) == 2
    assert reg.get("mock_exporter") is exporter
    assert len(reg.get_exporters()) == 1
    assert len(reg.get_enrichers()) == 1


def test_exporter_plugin_execution():
    reg = PluginRegistry()
    exporter = MockExporterPlugin()
    reg.register(exporter)

    finding = Finding(
        finding_type=FindingType.ERROR_BASED,
        severity=Severity.HIGH,
        parameter="user",
        payload="user=1'",
        url="http://example.com/test",
        title="Error SQLi",
    )

    csv_data = exporter.export([finding])
    assert "id,severity,parameter,title" in csv_data
    assert "HIGH,user,Error SQLi" in csv_data


def test_enricher_plugin_and_sandboxing():
    reg = PluginRegistry()
    enricher = MockEnricherPlugin()
    failing = FailingPlugin()

    reg.register(enricher)
    reg.register(failing)

    finding = Finding(
        finding_type=FindingType.BOOLEAN_BASED_BLIND,
        severity=Severity.MEDIUM,
        parameter="cat",
        payload="cat=1 AND 1=1",
        url="http://example.com/cat",
        title="Blind SQLi",
        description="Original desc",
    )

    enriched = enricher.enrich(finding)
    assert "[CWE-89 CVSS:9.8]" in enriched.description

    # Test sandboxed execution on failing plugin
    safe_result = reg.execute_safely(failing.enrich, finding, default_return=finding)
    assert safe_result == finding  # Safely fell back to default return without crashing!
