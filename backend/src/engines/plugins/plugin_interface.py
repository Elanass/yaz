from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, List

class PluginInterface(ABC):
    """
    Abstract base class for all decision engine plugins.
    """

    @abstractmethod
    def calculate_score(self, parameters: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Calculate the decision score based on parameters."""
        pass

    @abstractmethod
    def calculate_confidence(self, parameters: Dict[str, Any], recommendation: Any, context: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate confidence metrics based on parameters and context."""
        pass

    @abstractmethod
    def generate_recommendation(self, score: float, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Any:
        """Generate a primary recommendation based on the score."""
        pass

    @abstractmethod
    def generate_alternatives(self, score: float, parameters: Dict[str, Any], recommendation: Any) -> List[Any]:
        """Generate alternative recommendations."""
        pass
