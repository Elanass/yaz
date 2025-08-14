"""Domain Plugin System for Surge
Runtime-discoverable domain parsers for medical data processing.
"""

import importlib.metadata
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass
class DomainSpec(ABC):
    """Base specification for domain plugins."""

    name: str
    description: str
    version: str = "1.0.0"

    @abstractmethod
    def schema_detect(self, columns: list[str]) -> float:
        """Detect if dataset matches this domain schema.

        Args:
            columns: List of column names from the dataset

        Returns:
            Confidence score 0.0-1.0 for domain match
        """

    @abstractmethod
    def parse(self, df: pd.DataFrame) -> dict[str, Any]:
        """Parse and validate domain-specific data.

        Args:
            df: Raw pandas DataFrame

        Returns:
            Structured domain data dictionary
        """

    @abstractmethod
    def stats(self, df: pd.DataFrame) -> dict[str, Any]:
        """Generate domain-specific statistics.

        Args:
            df: Parsed DataFrame

        Returns:
            Statistical summary dictionary
        """

    @abstractmethod
    def insights(self, df: pd.DataFrame) -> list[str]:
        """Generate domain-specific insights.

        Args:
            df: Parsed DataFrame

        Returns:
            List of insight strings
        """

    @abstractmethod
    def deliverables(self, df: pd.DataFrame, audience: str) -> dict[str, Any]:
        """Generate audience-specific deliverables.

        Args:
            df: Parsed DataFrame
            audience: Target audience (practitioner, researcher, community)

        Returns:
            Deliverable content dictionary with templates and data
        """


class DomainRegistry:
    """Registry for domain plugins with auto-discovery."""

    def __init__(self) -> None:
        self._domains: dict[str, DomainSpec] = {}
        self._load_plugins()

    def _load_plugins(self) -> None:
        """Load domain plugins from entry points."""
        try:
            entry_points = importlib.metadata.entry_points(group="surge.domains")
            for entry_point in entry_points:
                try:
                    domain_class = entry_point.load()
                    domain_instance = domain_class()
                    self._domains[domain_instance.name] = domain_instance
                except Exception:
                    pass
        except Exception:
            pass

    def register(self, domain: DomainSpec) -> None:
        """Manually register a domain."""
        self._domains[domain.name] = domain

    def get_domain(self, name: str) -> DomainSpec | None:
        """Get domain by name."""
        return self._domains.get(name)

    def list_domains(self) -> list[DomainSpec]:
        """List all registered domains."""
        return list(self._domains.values())

    def detect_domain(self, columns: list[str]) -> DomainSpec | None:
        """Detect best matching domain for given columns."""
        best_domain = None
        best_score = 0.0

        for domain in self._domains.values():
            score = domain.schema_detect(columns)
            if score > best_score:
                best_score = score
                best_domain = domain

        return best_domain if best_score > 0.3 else None


# Global domain registry
domain_registry = DomainRegistry()
