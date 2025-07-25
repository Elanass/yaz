from typing import Dict, Any, Tuple

class ADCICore:
    """
    Core logic for Adaptive Decision Confidence Index (ADCI).
    """

    def __init__(self, parameter_weights: Dict[str, float], confidence_modifiers: Dict[str, float]):
        self.parameter_weights = parameter_weights
        self.confidence_modifiers = confidence_modifiers

    def calculate_score(self, parameters: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Calculate the decision score based on parameter weights."""
        score = 0.0
        breakdown = {}
        for key, weight in self.parameter_weights.items():
            value = parameters.get(key, 0)
            score += value * weight
            breakdown[key] = value * weight
        return score, breakdown

    def calculate_confidence(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate confidence metrics based on modifiers."""
        confidence = 0.0
        for key, modifier in self.confidence_modifiers.items():
            value = context.get(key, 0)
            confidence += value * modifier
        return confidence
