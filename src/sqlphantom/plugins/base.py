"""
SQLPhantom plugin contracts and extension base interfaces.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from sqlphantom.domain.models import Finding


class PluginCategory(str, Enum):
    REPORT_EXPORTER = "REPORT_EXPORTER"
    FINDING_ENRICHER = "FINDING_ENRICHER"
    NOTIFICATION = "NOTIFICATION"
    UTILITY = "UTILITY"


@dataclass(frozen=True)
class PluginMetadata:
    """Metadata describing an extension plugin."""
    name: str
    version: str
    author: str
    description: str
    category: PluginCategory
    min_sqlphantom_version: str = "0.1.0"


class BasePlugin(ABC):
    """Base interface for all SQLPhantom extensions."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return the plugin's metadata specification."""
        pass

    def initialize(self) -> bool:
        """Lifecycle hook executed upon plugin activation."""
        return True

    def shutdown(self) -> None:
        """Lifecycle hook executed when the plugin is deactivated."""
        pass


class ReportExporterPlugin(BasePlugin):
    """Extension contract for formatting and exporting assessment findings."""

    @abstractmethod
    def export(self, findings: list[Finding], title: str = "") -> str:
        """Export findings to a customized output string."""
        pass


class FindingEnricherPlugin(BasePlugin):
    """Extension contract for annotating findings with external intelligence."""

    @abstractmethod
    def enrich(self, finding: Finding) -> Finding:
        """Enrich finding with CVSS scores, remediation notes, or threat intelligence."""
        pass
