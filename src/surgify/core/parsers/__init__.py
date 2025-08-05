"""
Base parser interface for all domain parsers
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import pandas as pd


class BaseParser(ABC):
    """Abstract base class for all domain parsers"""
    
    def __init__(self):
        self.domain = self.__class__.__name__.replace('Parser', '').lower()
    
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
            return any(pattern.lower() in ' '.join(headers).lower() for pattern in patterns)
        return False
