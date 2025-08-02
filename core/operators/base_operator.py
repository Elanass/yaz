"""
Base Operator Class for Gastric ADCI Platform
Abstract base class for all operator implementations
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class BaseOperator(ABC):
    """
    Abstract base class for all operators in the Gastric ADCI Platform
    Provides common interface and functionality for operators
    """
    
    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self.status = "initializing"
        self.metadata: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the operator
        Returns True if initialization successful, False otherwise
        """
        pass
        
    async def cleanup(self):
        """
        Clean up operator resources
        Override in subclasses if cleanup is needed
        """
        self.status = "stopped"
        self.logger.info(f"Operator {self.name} cleaned up")
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get current operator status
        Returns status information as dictionary
        """
        return {
            "name": self.name,
            "status": self.status,
            "metadata": self.metadata
        }
        
    def set_metadata(self, key: str, value: Any):
        """Set metadata value"""
        self.metadata[key] = value
        
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)
