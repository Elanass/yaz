"""
Event Correlation Engine for clinical event pattern analysis.

This package provides tools for identifying patterns, anomalies, and correlations
in clinical events, helping to detect protocol deviations, security incidents,
and workflow optimizations.
"""

from .service import (
    correlation_engine,
    EventCorrelationEngine,
    CorrelationRule,
    CorrelatedEvent,
    start_background_processing
)

__all__ = [
    'correlation_engine',
    'EventCorrelationEngine',
    'CorrelationRule',
    'CorrelatedEvent',
    'start_background_processing'
]
