"""Plugin Discovery System
Runtime plugin discovery and loading for modular medical domains.
"""

import importlib
import inspect
import pkgutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class PluginType(str, Enum):
    """Types of medical plugins."""

    SURGERY = "surgery"
    CHEMOTHERAPY = "chemotherapy"
    RADIATION = "radiation"
    DECISION_ENGINE = "decision_engine"
    ANALYTICS = "analytics"
    IMAGING = "imaging"
    PATHOLOGY = "pathology"


class DomainType(str, Enum):
    """Medical domain types."""

    SURGERY = "surgery"
    LOGISTICS = "logistics"
    INSURANCE = "insurance"
    ONCOLOGY = "oncology"
    RADIOLOGY = "radiology"
    PATHOLOGY = "pathology"


@dataclass
class PluginMetadata:
    """Plugin metadata information."""

    name: str
    version: str
    plugin_type: PluginType
    domains: list[DomainType]
    description: str
    author: str
    dependencies: list[str]
    enabled: bool = True


class BasePlugin(ABC):
    """Base class for all medical plugins."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""

    @abstractmethod
    def initialize(self, config: dict[str, Any]) -> bool:
        """Initialize plugin with configuration."""

    @abstractmethod
    def analyze(self, data: Any) -> Any:
        """Analyze medical data using plugin."""

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """Return list of plugin capabilities."""


class PluginRegistry:
    """Registry for managing medical plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, BasePlugin] = {}
        self._metadata: dict[str, PluginMetadata] = {}
        self._loaded_modules: dict[str, Any] = {}

    def discover_plugins(
        self, plugin_paths: list[str] | None = None
    ) -> list[PluginMetadata]:
        """Discover plugins in specified paths."""
        if plugin_paths is None:
            plugin_paths = ["surge.modules", "surge.plugins", "surge.extensions"]

        discovered = []

        for path in plugin_paths:
            try:
                discovered.extend(self._scan_module_path(path))
            except (ImportError, ModuleNotFoundError):
                continue  # Skip if module path doesn't exist

        return discovered

    def _scan_module_path(self, module_path: str) -> list[PluginMetadata]:
        """Scan a module path for plugins."""
        discovered = []

        try:
            # Import the module
            module = importlib.import_module(module_path)

            # Walk through submodules if it's a package
            if hasattr(module, "__path__"):
                for _importer, modname, _ispkg in pkgutil.iter_modules(
                    module.__path__, module_path + "."
                ):
                    try:
                        submodule = importlib.import_module(modname)
                        discovered.extend(
                            self._extract_plugins_from_module(submodule, modname)
                        )
                    except Exception:
                        continue
            else:
                discovered.extend(
                    self._extract_plugins_from_module(module, module_path)
                )

        except Exception:
            pass

        return discovered

    def _extract_plugins_from_module(
        self, module: Any, module_name: str
    ) -> list[PluginMetadata]:
        """Extract plugins from a module."""
        plugins = []

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and self._is_plugin_class(obj):
                try:
                    plugin_instance = obj()
                    metadata = plugin_instance.metadata
                    metadata.name = f"{module_name}.{name}"
                    plugins.append(metadata)
                    self._plugins[metadata.name] = plugin_instance
                    self._metadata[metadata.name] = metadata
                except Exception:
                    continue

        return plugins

    def _is_plugin_class(self, cls: type) -> bool:
        """Check if a class is a valid plugin."""
        return (
            inspect.isclass(cls)
            and issubclass(cls, BasePlugin)
            and cls != BasePlugin
            and not inspect.isabstract(cls)
        )

    def load_plugin(
        self, plugin_name: str, config: dict[str, Any] | None = None
    ) -> bool:
        """Load and initialize a specific plugin."""
        if plugin_name not in self._plugins:
            return False

        try:
            plugin = self._plugins[plugin_name]
            return plugin.initialize(config or {})
        except Exception:
            return False

    def get_plugin(self, plugin_name: str) -> BasePlugin | None:
        """Get a loaded plugin by name."""
        return self._plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: PluginType) -> list[BasePlugin]:
        """Get all plugins of a specific type."""
        return [
            plugin
            for name, plugin in self._plugins.items()
            if self._metadata[name].plugin_type == plugin_type
        ]

    def get_plugins_by_domain(self, domain: DomainType) -> list[BasePlugin]:
        """Get all plugins supporting a specific domain."""
        return [
            plugin
            for name, plugin in self._plugins.items()
            if domain in self._metadata[name].domains
        ]

    def list_plugins(self, enabled_only: bool = True) -> list[PluginMetadata]:
        """List all registered plugins."""
        if enabled_only:
            return [meta for meta in self._metadata.values() if meta.enabled]
        return list(self._metadata.values())

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        if plugin_name in self._metadata:
            self._metadata[plugin_name].enabled = True
            return True
        return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        if plugin_name in self._metadata:
            self._metadata[plugin_name].enabled = False
            return True
        return False


class MedicalDomainRouter:
    """Router for directing requests to appropriate domain plugins."""

    def __init__(self, registry: PluginRegistry) -> None:
        self.registry = registry

    def route_analysis(self, domain: DomainType, data: Any) -> list[Any]:
        """Route analysis request to appropriate domain plugins."""
        plugins = self.registry.get_plugins_by_domain(domain)
        enabled_plugins = [p for p in plugins if self._is_enabled(p)]

        results = []
        for plugin in enabled_plugins:
            try:
                result = plugin.analyze(data)
                results.append(
                    {"plugin": plugin.metadata.name, "result": result, "success": True}
                )
            except Exception as e:
                results.append(
                    {"plugin": plugin.metadata.name, "error": str(e), "success": False}
                )

        return results

    def get_domain_capabilities(self, domain: DomainType) -> dict[str, list[str]]:
        """Get capabilities available for a domain."""
        plugins = self.registry.get_plugins_by_domain(domain)
        capabilities = {}

        for plugin in plugins:
            if self._is_enabled(plugin):
                capabilities[plugin.metadata.name] = plugin.get_capabilities()

        return capabilities

    def _is_enabled(self, plugin: BasePlugin) -> bool:
        """Check if plugin is enabled."""
        return self.registry._metadata.get(
            plugin.metadata.name,
            PluginMetadata("", "", PluginType.SURGERY, [], "", "", []),
        ).enabled


# Plugin implementations for existing modules
class GastricSurgeryPlugin(BasePlugin):
    """Plugin wrapper for gastric surgery module."""

    def __init__(self) -> None:
        from .gastric_surgery import GastricSurgeryModule

        self.module = GastricSurgeryModule()

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="gastric_surgery",
            version="1.0.0",
            plugin_type=PluginType.SURGERY,
            domains=[DomainType.SURGERY, DomainType.ONCOLOGY],
            description="Gastric surgery analysis and gastrectomy procedures",
            author="SurgeAI Team",
            dependencies=["pydantic", "datetime"],
        )

    def initialize(self, config: dict[str, Any]) -> bool:
        try:
            self.module = GastricSurgeryModule()
            return True
        except Exception:
            return False

    def analyze(self, data: Any) -> Any:
        from .gastric_surgery import GastricSurgeryCase

        if isinstance(data, GastricSurgeryCase):
            return self.module.analyze_case(data)
        if isinstance(data, list):
            from .gastric_surgery import analyze_gastric_surgery_cohort

            return analyze_gastric_surgery_cohort(data)
        msg = "Invalid data type for gastric surgery analysis"
        raise ValueError(msg)

    def get_capabilities(self) -> list[str]:
        return [
            "case_analysis",
            "risk_assessment",
            "surgical_recommendation",
            "outcome_prediction",
            "cohort_analysis",
            "scheduling_optimization",
        ]


class ChemoFLOTPlugin(BasePlugin):
    """Plugin wrapper for FLOT chemotherapy module."""

    def __init__(self) -> None:
        from .chemo_flot import ChemoFLOTModule

        self.module = ChemoFLOTModule()

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="chemo_flot",
            version="1.0.0",
            plugin_type=PluginType.CHEMOTHERAPY,
            domains=[DomainType.ONCOLOGY],
            description="FLOT chemotherapy impact analysis and optimization",
            author="SurgeAI Team",
            dependencies=["pydantic", "datetime"],
        )

    def initialize(self, config: dict[str, Any]) -> bool:
        try:
            self.module = ChemoFLOTModule()
            return True
        except Exception:
            return False

    def analyze(self, data: Any) -> Any:
        from .chemo_flot import FLOTCase

        if isinstance(data, FLOTCase):
            return self.module.analyze_flot_case(data)
        if isinstance(data, list):
            from .chemo_flot import analyze_flot_cohort

            return analyze_flot_cohort(data)
        msg = "Invalid data type for FLOT analysis"
        raise ValueError(msg)

    def get_capabilities(self) -> list[str]:
        return [
            "treatment_analysis",
            "toxicity_assessment",
            "response_evaluation",
            "fitness_assessment",
            "protocol_optimization",
            "cohort_analysis",
        ]


class PrecisionEnginePlugin(BasePlugin):
    """Plugin wrapper for precision decision engine."""

    def __init__(self) -> None:
        from .precision_engine import PrecisionDecisionEngine

        self.engine = PrecisionDecisionEngine()

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="precision_engine",
            version="1.0.0",
            plugin_type=PluginType.DECISION_ENGINE,
            domains=[DomainType.SURGERY, DomainType.ONCOLOGY],
            description="Precision decision engine for integrated gastric cancer care",
            author="SurgeAI Team",
            dependencies=["pydantic", "datetime", "gastric_surgery", "chemo_flot"],
        )

    def initialize(self, config: dict[str, Any]) -> bool:
        try:
            self.engine = PrecisionDecisionEngine()
            return True
        except Exception:
            return False

    def analyze(self, data: Any) -> Any:
        from .precision_engine import IntegratedCase

        if isinstance(data, IntegratedCase):
            return self.engine.analyze_integrated_case(data)
        if isinstance(data, list):
            from .precision_engine import analyze_precision_decisions

            return analyze_precision_decisions(data)
        msg = "Invalid data type for precision engine analysis"
        raise ValueError(msg)

    def get_capabilities(self) -> list[str]:
        return [
            "integrated_analysis",
            "treatment_sequencing",
            "risk_stratification",
            "outcome_prediction",
            "decision_support",
            "consensus_scoring",
            "algorithm_optimization",
        ]


# Global plugin registry instance
_global_registry = None


def get_plugin_registry() -> PluginRegistry:
    """Get the global plugin registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = PluginRegistry()
        # Auto-discover and register built-in plugins
        _register_builtin_plugins(_global_registry)
    return _global_registry


def _register_builtin_plugins(registry: PluginRegistry) -> None:
    """Register built-in plugins."""
    try:
        # Register gastric surgery plugin
        gastric_plugin = GastricSurgeryPlugin()
        registry._plugins[gastric_plugin.metadata.name] = gastric_plugin
        registry._metadata[gastric_plugin.metadata.name] = gastric_plugin.metadata

        # Register FLOT plugin
        flot_plugin = ChemoFLOTPlugin()
        registry._plugins[flot_plugin.metadata.name] = flot_plugin
        registry._metadata[flot_plugin.metadata.name] = flot_plugin.metadata

        # Register precision engine plugin
        precision_plugin = PrecisionEnginePlugin()
        registry._plugins[precision_plugin.metadata.name] = precision_plugin
        registry._metadata[precision_plugin.metadata.name] = precision_plugin.metadata

    except Exception:
        pass  # Fail silently if modules aren't available


def create_domain_router() -> MedicalDomainRouter:
    """Create a medical domain router with the global registry."""
    return MedicalDomainRouter(get_plugin_registry())


# Convenience functions for plugin operations
def discover_all_plugins() -> list[PluginMetadata]:
    """Discover all available plugins."""
    registry = get_plugin_registry()
    return registry.discover_plugins()


def analyze_with_domain(domain: DomainType, data: Any) -> list[Any]:
    """Analyze data using all plugins for a specific domain."""
    router = create_domain_router()
    return router.route_analysis(domain, data)


def get_domain_capabilities(domain: DomainType) -> dict[str, list[str]]:
    """Get all capabilities available for a domain."""
    router = create_domain_router()
    return router.get_domain_capabilities(domain)
