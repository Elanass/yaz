"""
Base parser interface for all domain parsers
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

import pandas as pd


class BaseParser(ABC):
    """Abstract base class for all domain parsers"""

    def __init__(self):
        self.domain = self.__class__.__name__.replace("Parser", "").lower()

    @abstractmethod
    def parse(self, data: Any) -> Dict[str, Any]:
        """Parse domain-specific data"""
        pass

    @abstractmethod
    def get_schema_patterns(self) -> List[str]:
        """Return list of header patterns that identify this domain"""
        pass

    def validate_data(self, data: Any) -> bool:
        """Validate if data belongs to this domain"""
        if isinstance(data, pd.DataFrame):
            headers = data.columns.tolist()
            patterns = self.get_schema_patterns()
            return any(
                pattern.lower() in " ".join(headers).lower() for pattern in patterns
            )
        return False


# Parser Registry
from .surgery_parser import SurgeryParser
from .logistics_parser import LogisticsParser  
from .insurance_parser import InsuranceParser


def get_parser_for_domain(domain: str) -> BaseParser:
    """
    Get the appropriate parser for a given domain
    
    Args:
        domain: The domain name (surgery, logistics, insurance, general)
        
    Returns:
        BaseParser: The appropriate parser instance
        
    Raises:
        ValueError: If domain is not supported
    """
    parsers = {
        "surgery": SurgeryParser,
        "logistics": LogisticsParser,
        "insurance": InsuranceParser,
        "general": SurgeryParser,  # Default to surgery parser for general cases
    }
    
    if domain not in parsers:
        raise ValueError(f"Unsupported domain: {domain}. Supported domains: {list(parsers.keys())}")
    
    return parsers[domain]()


def get_all_parsers() -> Dict[str, BaseParser]:
    """
    Get all available parsers
    
    Returns:
        Dict[str, BaseParser]: Dictionary of domain names to parser instances
    """
    return {
        "surgery": SurgeryParser(),
        "logistics": LogisticsParser(),
        "insurance": InsuranceParser(),
        "general": SurgeryParser(),
    }


def detect_domain_from_data(data: Any) -> str:
    """
    Attempt to automatically detect the domain from data
    
    Args:
        data: Input data to analyze
        
    Returns:
        str: Detected domain name, or "general" if no specific domain detected
    """
    parsers = get_all_parsers()
    
    # Try each parser's validation method
    for domain, parser in parsers.items():
        if domain == "general":  # Skip general as it's a fallback
            continue
            
        if parser.validate_data(data):
            return domain
    
    # If no specific domain detected, return general
    return "general"
