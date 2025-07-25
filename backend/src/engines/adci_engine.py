"""
ADCI (Adaptive Decision Confidence Index) Engine
Core decision engine for gastric cancer treatment recommendations
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from loguru import logger

from ..core.config import get_settings
from ..services.evidence_service import EvidenceService
from .plugins.plugin_interface import PluginInterface


class BaseDecisionEngine:
    """
    Base class for decision engines to provide modular and reusable logic.
    """

    def __init__(self, name: str, version: str, parameter_weights: Dict[str, float], confidence_modifiers: Dict[str, float]):
        self.name = name
        self.version = version
        self.parameter_weights = parameter_weights
        self.confidence_modifiers = confidence_modifiers

    async def calculate_score(self, parameters: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Calculate the decision score based on parameter weights."""
        score = 0.0
        breakdown = {}
        for key, weight in self.parameter_weights.items():
            value = parameters.get(key, 0)
            score += value * weight
            breakdown[key] = value * weight
        return score, breakdown

    async def calculate_confidence(self, parameters: Dict[str, Any], recommendation: Any, context: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate confidence metrics based on modifiers."""
        confidence = 0.0
        for key, modifier in self.confidence_modifiers.items():
            value = context.get(key, 0) if context else 0
            confidence += value * modifier
        return {"confidence": confidence}

class ADCIEngine(BaseDecisionEngine, PluginInterface):
    """
    Adaptive Decision Confidence Index Engine
    
    This engine provides evidence-based treatment recommendations
    with confidence scoring and uncertainty quantification.
    """
    
    def __init__(self):
        super().__init__(
            name="adci",
            version="2.1.0",
            parameter_weights={
                "tumor_stage": 0.25,
                "histology": 0.15,
                "biomarkers": 0.20,
                "performance_status": 0.15,
                "comorbidities": 0.10,
                "patient_preferences": 0.10,
                "molecular_profile": 0.05
            },
            confidence_modifiers={
                "data_completeness": 0.3,
                "evidence_strength": 0.4,
                "guideline_alignment": 0.3
            }
        )
    
    async def process_decision(
        self,
        patient_id: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        include_alternatives: bool = True,
        confidence_threshold: float = 0.75
    ) -> Dict[str, Any]:
        """Process ADCI decision for gastric cancer treatment"""
        
        start_time = datetime.now()
        
        try:
            # Validate input parameters
            self._validate_parameters(parameters)
            
            # Calculate ADCI score
            adci_score, score_breakdown = await self.calculate_score(parameters)
            
            # Generate primary recommendation
            primary_recommendation = await self._generate_recommendation(
                adci_score, parameters, context
            )
            
            # Calculate confidence metrics
            confidence_metrics = await self.calculate_confidence(
                parameters, primary_recommendation, context
            )
            
            # Generate alternative options if requested
            alternatives = []
            if include_alternatives:
                alternatives = await self._generate_alternatives(
                    adci_score, parameters, primary_recommendation
                )
            
            return {
                "adci_score": adci_score,
                "score_breakdown": score_breakdown,
                "primary_recommendation": primary_recommendation,
                "confidence_metrics": confidence_metrics,
                "alternatives": alternatives,
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Error processing decision: {e}")
            raise
    
    def _validate_parameters(self, parameters: Dict[str, Any]):
        """Validate input parameters."""
        required_keys = set(self.parameter_weights.keys())
        missing_keys = required_keys - parameters.keys()
        if missing_keys:
            raise ValueError(f"Missing required parameters: {missing_keys}")
    
    async def _generate_recommendation(self, score: float, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Any:
        """Generate a primary recommendation based on the score."""
        # Placeholder for domain-specific logic
        return {"recommendation": "Standard Treatment", "score": score}
    
    async def _generate_alternatives(self, score: float, parameters: Dict[str, Any], recommendation: Any) -> List[Any]:
        """Generate alternative recommendations."""
        # Placeholder for domain-specific logic
        return [{"recommendation": "Alternative Treatment", "score": score - 0.1}]
