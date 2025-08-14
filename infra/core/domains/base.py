"""Base domain specification for plugin system."""

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class DomainSpec(ABC):
    """Abstract base class for domain plugins
    Each medical domain (surgery, logistics, insurance, etc.) implements this interface.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Domain name identifier."""

    @property
    def version(self) -> str:
        """Domain plugin version."""
        return "1.0.0"

    @property
    def description(self) -> str:
        """Human-readable description of the domain."""
        return f"{self.name} domain plugin"

    @abstractmethod
    def schema_detect(self, headers: list[str]) -> float:
        """Analyze CSV headers to determine if this domain applies.

        Args:
            headers: List of column headers from CSV

        Returns:
            float: Confidence score 0.0-1.0 indicating domain match
        """

    @abstractmethod
    def parse(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse and transform data according to domain-specific rules.

        Args:
            df: Raw dataframe from CSV

        Returns:
            pd.DataFrame: Processed dataframe with domain-specific columns
        """

    def validate(self, df: pd.DataFrame) -> dict[str, Any]:
        """Validate processed data for domain-specific quality checks.

        Args:
            df: Processed dataframe

        Returns:
            Dict containing validation results
        """
        return {"valid": True, "errors": [], "warnings": [], "row_count": len(df)}

    def get_recommended_tasks(self) -> list[str]:
        """Return list of recommended task IDs for this domain.

        Returns:
            List of task identifiers that work well with this domain
        """
        return ["basic_analysis", "generate_report"]

    def get_schema_hints(self) -> dict[str, str]:
        """Return expected column names and their descriptions.

        Returns:
            Dict mapping column names to descriptions
        """
        return {}


class MultiDomainResult:
    """Result container for multi-domain detection."""

    def __init__(self, primary: str, secondary: list[str], confidence: float) -> None:
        self.primary = primary
        self.secondary = secondary
        self.confidence = confidence
        self.suggested_pipeline = f"{primary}_processor"

    def to_dict(self) -> dict[str, Any]:
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "confidence": self.confidence,
            "suggested_pipeline": self.suggested_pipeline,
        }
