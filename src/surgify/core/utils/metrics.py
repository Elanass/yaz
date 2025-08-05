"""
Metrics Utilities

Provides shared functions for weighted calculations and confidence estimations.
"""
from typing import Dict, List


def weighted_sum(values: Dict[str, float], weights: Dict[str, float]) -> float:
    """
    Compute the weighted sum of values with corresponding weights.

    Args:
        values: Mapping of criterion to its score.
        weights: Mapping of criterion to its weight.

    Returns:
        Weighted sum.
    """
    total = 0.0
    for key, score in values.items():
        weight = weights.get(key, 0.0)
        total += score * weight
    return total


def calculate_confidence(
    overall_scores: Dict[str, float], threshold: float = 0.2
) -> float:
    """
    Calculate confidence based on the margin between top two scores.

    Args:
        overall_scores: Mapping of alternative IDs to overall scores.
        threshold: Margin at which confidence maxes out.

    Returns:
        Confidence score between 0.0 and 1.0.
    """
    scores = sorted(overall_scores.values(), reverse=True)
    if len(scores) < 2:
        return 0.5
    margin = scores[0] - scores[1]
    return min(margin / threshold, 1.0)


def compute_confidence_interval(confidence: float, delta: float = 0.1) -> List[float]:
    """
    Compute a simple confidence interval around a point estimate.

    Args:
        confidence: Central confidence value.
        delta: Half-width of the interval.

    Returns:
        [lower_bound, upper_bound] clamped to [0.0, 1.0].
    """
    low = max(confidence - delta, 0.0)
    high = min(confidence + delta, 1.0)
    return [round(low, 3), round(high, 3)]
