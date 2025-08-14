"""
Health check and provider management for orchestration.
"""
import logging
from typing import Any, Dict, List, Optional, Type

from .providers.base import BaseProvider
from .providers.incus import IncusProvider
from .providers.multipass import MultipassProvider
from .utils import ProviderError, ProviderUnavailableError

logger = logging.getLogger(__name__)


class HealthChecker:
    """Health check and critical-switch logic for providers."""

    def __init__(self):
        self.providers: List[Type[BaseProvider]] = [IncusProvider, MultipassProvider]
        self._active_provider: Optional[BaseProvider] = None
        self._last_health_check: Dict[str, Any] = {}

    def get_available_providers(self) -> List[BaseProvider]:
        """Get list of available providers."""
        available = []
        for provider_class in self.providers:
            try:
                provider = provider_class()
                if provider.is_available():
                    available.append(provider)
            except Exception as e:
                logger.debug(f"Provider {provider_class.__name__} not available: {e}")
        return available

    def get_primary_provider(self, project: str = "yaz") -> BaseProvider:
        """Get the primary (best) available provider."""
        if self._active_provider:
            try:
                # Check if current provider is still healthy
                health = self._active_provider.health_check()
                if health.get("available", False):
                    return self._active_provider
                else:
                    logger.warning("Active provider became unhealthy, switching...")
                    self._active_provider = None
            except Exception as e:
                logger.warning(f"Health check failed for active provider: {e}")
                self._active_provider = None

        # Find the best available provider
        available = self.get_available_providers()
        if not available:
            raise ProviderUnavailableError("No orchestration providers available")

        # Prefer Incus, then Multipass
        for provider in available:
            if isinstance(provider, IncusProvider):
                logger.info("Using Incus as primary provider")
                if hasattr(provider, "project"):
                    provider.project = project
                self._active_provider = provider
                return provider

        # Fall back to first available
        provider = available[0]
        logger.info(f"Using {provider.__class__.__name__} as fallback provider")
        self._active_provider = provider
        return provider

    def perform_health_checks(self) -> Dict[str, Any]:
        """Perform comprehensive health checks on all providers."""
        health_report = {
            "timestamp": None,
            "overall_status": "unknown",
            "active_provider": None,
            "providers": {},
            "recommendations": [],
        }

        import time

        health_report["timestamp"] = time.time()

        try:
            # Check all providers
            for provider_class in self.providers:
                provider_name = provider_class.__name__.replace("Provider", "").lower()
                try:
                    provider = provider_class()
                    provider_health = provider.health_check()
                    health_report["providers"][provider_name] = provider_health
                except Exception as e:
                    health_report["providers"][provider_name] = {
                        "provider": provider_name,
                        "available": False,
                        "errors": [str(e)],
                    }

            # Determine overall status
            available_providers = [
                name
                for name, health in health_report["providers"].items()
                if health.get("available", False)
            ]

            if not available_providers:
                health_report["overall_status"] = "critical"
                health_report["recommendations"].append(
                    "No orchestration providers available. Install Incus or Multipass."
                )
            elif "incus" in available_providers:
                health_report["overall_status"] = "healthy"
                health_report["active_provider"] = "incus"
            elif available_providers:
                health_report["overall_status"] = "degraded"
                health_report["active_provider"] = available_providers[0]
                health_report["recommendations"].append(
                    "Incus not available, using fallback provider. Consider installing Incus."
                )

            # Add specific recommendations
            if "incus" in health_report["providers"]:
                incus_health = health_report["providers"]["incus"]
                if not incus_health.get("available", False):
                    errors = incus_health.get("errors", [])
                    if any("permission" in str(e).lower() for e in errors):
                        health_report["recommendations"].append(
                            "Incus permission issues detected. Run: sudo usermod -aG incus-admin $USER"
                        )

            self._last_health_check = health_report
            return health_report

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_report["overall_status"] = "error"
            health_report["recommendations"].append(f"Health check failed: {e}")
            return health_report

    def get_last_health_check(self) -> Dict[str, Any]:
        """Get the last health check results."""
        return self._last_health_check.copy()

    def force_provider_switch(self, provider_name: str) -> bool:
        """Force switch to a specific provider."""
        provider_map = {"incus": IncusProvider, "multipass": MultipassProvider}

        provider_class = provider_map.get(provider_name.lower())
        if not provider_class:
            logger.error(f"Unknown provider: {provider_name}")
            return False

        try:
            provider = provider_class()
            if not provider.is_available():
                logger.error(f"Provider {provider_name} is not available")
                return False

            self._active_provider = provider
            logger.info(f"Switched to provider: {provider_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to switch to {provider_name}: {e}")
            return False

    def critical_switch_check(self) -> bool:
        """Check if critical switch to fallback is needed."""
        if not self._active_provider:
            return False

        try:
            health = self._active_provider.health_check()
            return not health.get("available", False)
        except Exception:
            return True

    def auto_recover(self) -> bool:
        """Attempt automatic recovery from provider issues."""
        logger.info("Attempting automatic recovery...")

        try:
            # Try to get a working provider
            provider = self.get_primary_provider()

            # Try to ensure host setup
            if provider.ensure_host():
                logger.info("Automatic recovery successful")
                return True
            else:
                logger.error("Host setup failed during recovery")
                return False

        except Exception as e:
            logger.error(f"Automatic recovery failed: {e}")
            return False


# Global health checker instance
health_checker = HealthChecker()


def get_provider(project: str = "yaz") -> BaseProvider:
    """Get the best available provider."""
    return health_checker.get_primary_provider(project)


def health_check() -> Dict[str, Any]:
    """Perform health check on all providers."""
    return health_checker.perform_health_checks()


def switch_provider(provider_name: str) -> bool:
    """Switch to a specific provider."""
    return health_checker.force_provider_switch(provider_name)
