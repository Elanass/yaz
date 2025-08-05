"""
Universal Research Module for Surgify Platform
Extends existing functionality with domain-agnostic research capabilities
Preserves all existing APIs and workflows
"""

from .adapters.surgify_adapter import SurgifyAdapter
from .engines.cohort_analyzer import CohortAnalyzer
from .engines.outcome_predictor import OutcomePredictor
from .engines.research_generator import ResearchGenerator
from .integration.api_enhancer import ResearchAPIEnhancer

__all__ = [
    'SurgifyAdapter',
    'CohortAnalyzer', 
    'OutcomePredictor',
    'ResearchGenerator',
    'ResearchAPIEnhancer'
]
