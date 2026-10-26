"""
SQLPhantom plugin registry managing extension discovery, validation, and safe execution.
"""

import logging
import threading
from typing import Any, Callable

from sqlphantom.plugins.base import (
    BasePlugin,
    FindingEnricherPlugin,
    PluginCategory,
    PluginMetadata,
    ReportExporterPlugin,
)

logger = logging.getLogger(__name__)


class PluginRegistry:
    """
    Central repository of loaded plugins with metadata validation
    and resilient error-isolated execution.
    """

    def __init__(self) -> None:
        self._plugins: dict[str, BasePlugin] = {}
        self._lock = threading.RLock()

    def register(self, plugin: BasePlugin) -> bool:
        """
        Validate and register a plugin instance.
        Ensures name uniqueness and executes initialize().
        """
        meta = plugin.metadata
        if not meta or not meta.name or not meta.name.strip():
            logger.error("Failed to register plugin: missing valid metadata name")
            return False

        with self._lock:
            if meta.name in self._plugins:
                logger.warning("Plugin '%s' already registered, overwriting", meta.name)

            try:
                if not plugin.initialize():
                    logger.error("Plugin '%s' initialization returned False", meta.name)
                    return False
            except Exception as exc:
                logger.error("Exception initializing plugin '%s': %s", meta.name, exc, exc_info=True)
                return False

            self._plugins[meta.name] = plugin
            logger.info("Registered plugin: %s v%s (%s)", meta.name, meta.version, meta.category)
            return True

    def unregister(self, name: str) -> bool:
        """Shutdown and remove a registered plugin."""
        with self._lock:
            plugin = self._plugins.pop(name, None)
            if not plugin:
                return False

            try:
                plugin.shutdown()
            except Exception as exc:
                logger.error("Exception shutting down plugin '%s': %s", name, exc, exc_info=True)
            return True

    def get(self, name: str) -> BasePlugin | None:
        """Retrieve a registered plugin by name."""
        with self._lock:
            return self._plugins.get(name)

    def list_plugins(self) -> list[PluginMetadata]:
        """Return metadata for all active plugins."""
        with self._lock:
            return [p.metadata for p in self._plugins.values()]

    def get_exporters(self) -> list[ReportExporterPlugin]:
        """Return all registered report exporter plugins."""
        with self._lock:
            return [p for p in self._plugins.values() if isinstance(p, ReportExporterPlugin)]

    def get_enrichers(self) -> list[FindingEnricherPlugin]:
        """Return all registered finding enricher plugins."""
        with self._lock:
            return [p for p in self._plugins.values() if isinstance(p, FindingEnricherPlugin)]

    def execute_safely(self, fn: Callable[..., Any], *args: Any, default_return: Any = None, **kwargs: Any) -> Any:
        """
        Execute a plugin function inside an exception sandbox, preventing
        third-party extension errors from terminating core operations.
        """
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            logger.error("Plugin execution error in %s: %s", getattr(fn, "__name__", "unknown"), exc, exc_info=True)
            return default_return
