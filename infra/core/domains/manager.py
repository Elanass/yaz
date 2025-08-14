"""Domain plugin discovery and management system."""

import importlib
from typing import Any

import pandas as pd
from pkg_resources import iter_entry_points

from .base import DomainSpec, MultiDomainResult


class DomainManager:
    """Manages domain plugin discovery and execution."""

    def __init__(self) -> None:
        self._domains: dict[str, DomainSpec] = {}
        self._load_domains()

    def _load_domains(self) -> None:
        """Load domain plugins via entry points and direct imports."""
        # Load via entry points (from pyproject.toml)
        try:
            for ep in iter_entry_points("surge.domains"):
                try:
                    domain_factory = ep.load()
                    domain = domain_factory()
                    self._domains[domain.name] = domain
                except Exception:
                    pass
        except Exception:
            # Fallback if pkg_resources is not available
            pass

        # Load built-in domains
        self._load_builtin_domains()

    def _load_builtin_domains(self) -> None:
        """Load built-in domain plugins."""
        builtin_domains = [
            ("surgery", "surge.core.domains.surgery", "get_surgery_spec"),
            ("logistics", "surge.core.domains.logistics", "get_logistics_spec"),
            ("insurance", "surge.core.domains.insurance", "get_insurance_spec"),
        ]

        for name, module_path, factory_name in builtin_domains:
            try:
                module = importlib.import_module(module_path)
                factory = getattr(module, factory_name)
                domain = factory()
                self._domains[name] = domain
            except (ImportError, AttributeError):
                # Create mock domain if not available
                self._domains[name] = MockDomainSpec(name)

    def list_domains(self) -> list[dict[str, Any]]:
        """List all available domains."""
        return [
            {
                "name": domain.name,
                "version": domain.version,
                "description": domain.description,
                "status": "active" if hasattr(domain, "parse") else "mock",
            }
            for domain in self._domains.values()
        ]

    def detect_domain(self, headers: list[str]) -> MultiDomainResult:
        """Detect the most appropriate domain(s) for given data headers.

        Args:
            headers: List of column headers

        Returns:
            MultiDomainResult with primary domain and confidence
        """
        scores = {}

        for name, domain in self._domains.items():
            try:
                score = domain.schema_detect(headers)
                scores[name] = score
            except Exception:
                scores[name] = 0.0

        # Find primary domain (highest score)
        primary = max(scores.items(), key=lambda x: x[1])
        primary_name, primary_score = primary

        # Find secondary domains (score > 0.3 but not primary)
        secondary = [
            name
            for name, score in scores.items()
            if score > 0.3 and name != primary_name
        ]

        return MultiDomainResult(
            primary=primary_name, secondary=secondary, confidence=primary_score
        )

    def get_domain(self, name: str) -> DomainSpec | None:
        """Get domain plugin by name."""
        return self._domains.get(name)

    def parse_with_domain(self, domain_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """Parse dataframe using specified domain."""
        domain = self.get_domain(domain_name)
        if not domain:
            msg = f"Domain '{domain_name}' not found"
            raise ValueError(msg)

        return domain.parse(df)

    def validate_with_domain(
        self, domain_name: str, df: pd.DataFrame
    ) -> dict[str, Any]:
        """Validate dataframe using specified domain."""
        domain = self.get_domain(domain_name)
        if not domain:
            msg = f"Domain '{domain_name}' not found"
            raise ValueError(msg)

        return domain.validate(df)


class MockDomainSpec(DomainSpec):
    """Mock domain for testing and fallback."""

    def __init__(self, domain_name: str) -> None:
        self._name = domain_name

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return "0.1.0-mock"

    @property
    def description(self) -> str:
        return f"Mock {self._name} domain (plugin not available)"

    def schema_detect(self, headers: list[str]) -> float:
        """Mock detection based on domain name in headers."""
        header_text = " ".join(headers).lower()
        return 0.5 if self._name.lower() in header_text else 0.1

    def parse(self, df: pd.DataFrame) -> pd.DataFrame:
        """Mock parse - return dataframe unchanged."""
        return df

    def validate(self, df: pd.DataFrame) -> dict[str, Any]:
        """Mock validation."""
        return {
            "valid": True,
            "errors": [],
            "warnings": [f"Using mock {self._name} domain"],
            "row_count": len(df),
            "domain": self._name,
        }


# Global domain manager instance
domain_manager = DomainManager()
