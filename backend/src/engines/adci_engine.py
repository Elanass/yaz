"""
ADCI (Adaptive Decision Confidence Index) Engine
Core decision engine for gastric cancer treatment recommendations
Enhanced with <150ms response time optimization and Surgify UI integration
"""

import time
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


class BaseDecisionEngine:
    """Base class for decision engines with performance optimization"""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.cache = {}
        self.last_cache_clear = time.time()
    
    def clear_cache_if_needed(self):
        """Clear cache every 5 minutes for fresh data"""
        if time.time() - self.last_cache_clear > 300:
            self.cache = {}
            self.last_cache_clear = time.time()


class ADCIEngine(BaseDecisionEngine):
    """
    Adaptive Decision Confidence Index Engine
    Enhanced for Surgify UI integration with real-time metrics
    Optimized for <150ms response time with intelligent caching
    """
    
    def __init__(self):
        super().__init__("ADCI Engine", "2.1.0")
        
        # Parameter weights for ADCI calculation
        self.parameter_weights = {
            "tumor_stage": 0.25,
            "histology": 0.15,
            "biomarkers": 0.20,
            "performance_status": 0.15,
            "comorbidities": 0.10,
            "patient_preferences": 0.10,
            "molecular_profile": 0.05
        }
        
        # Confidence calculation modifiers
        self.confidence_modifiers = {
            "data_completeness": 0.3,
            "evidence_strength": 0.4,
            "guideline_alignment": 0.3
        }
        
        # Performance monitoring
        self.response_times = []
        self.cache_hits = 0
        self.cache_misses = 0
    
    async def process_decision(
        self,
        patient_id: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        include_alternatives: bool = True,
        confidence_threshold: float = 0.75
    ) -> Dict[str, Any]:
        """
        Process ADCI decision for gastric cancer treatment
        Optimized for <150ms response time
        """
        start_time = time.time()
        self.clear_cache_if_needed()
        
        # Check cache first for performance optimization
        cache_key = self._generate_cache_key(patient_id, parameters)
        if cache_key in self.cache:
            self.cache_hits += 1
            cached_result = self.cache[cache_key].copy()
            cached_result["cached"] = True
            cached_result["processing_time"] = time.time() - start_time
            return cached_result
        
        self.cache_misses += 1
        
        try:
            # Validate input parameters
            self._validate_parameters(parameters)
            
            # Calculate ADCI score with optimized algorithm
            adci_score, score_breakdown = await self._calculate_adci_score(parameters)
            
            # Generate primary recommendation
            primary_recommendation = await self._generate_recommendation(
                adci_score, parameters, context
            )
            
            # Calculate confidence metrics
            confidence_metrics = await self._calculate_confidence_metrics(
                parameters, primary_recommendation, context
            )
            
            # Generate alternative options if requested
            alternatives = []
            if include_alternatives and adci_score < confidence_threshold:
                alternatives = await self._generate_alternatives(
                    adci_score, parameters, primary_recommendation
                )
            
            # Real-time UI metrics for Surgify integration
            ui_metrics = self._generate_ui_metrics(adci_score, confidence_metrics)
            
            result = {
                "patient_id": patient_id,
                "adci_score": round(adci_score, 3),
                "score_breakdown": score_breakdown,
                "primary_recommendation": primary_recommendation,
                "confidence_metrics": confidence_metrics,
                "alternatives": alternatives,
                "ui_metrics": ui_metrics,
                "cached": False,
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache result for performance
            self.cache[cache_key] = result.copy()
            
            # Track performance
            self.response_times.append(result["processing_time"])
            if len(self.response_times) > 100:  # Keep only last 100 measurements
                self.response_times.pop(0)
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "patient_id": patient_id,
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _calculate_adci_score(self, parameters: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Calculate ADCI score with optimized performance"""
        score = 0.0
        breakdown = {}
        
        for param, weight in self.parameter_weights.items():
            if param in parameters:
                param_score = self._normalize_parameter_value(param, parameters[param])
                weighted_score = param_score * weight
                score += weighted_score
                breakdown[param] = {
                    "raw_value": parameters[param],
                    "normalized_score": round(param_score, 3),
                    "weight": weight,
                    "weighted_score": round(weighted_score, 3)
                }
        
        return min(score, 1.0), breakdown
    
    async def _calculate_confidence_metrics(
        self, 
        parameters: Dict[str, Any], 
        recommendation: Dict[str, Any], 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate confidence metrics for the decision"""
        
        # Data completeness score
        completeness = len(parameters) / len(self.parameter_weights)
        
        # Evidence strength (simulated based on parameters)
        evidence_strength = self._calculate_evidence_strength(parameters)
        
        # Guideline alignment (simulated)
        guideline_alignment = self._calculate_guideline_alignment(recommendation)
        
        # Overall confidence
        confidence = (
            completeness * self.confidence_modifiers["data_completeness"] +
            evidence_strength * self.confidence_modifiers["evidence_strength"] +
            guideline_alignment * self.confidence_modifiers["guideline_alignment"]
        )
        
        return {
            "overall_confidence": round(confidence, 3),
            "data_completeness": round(completeness, 3),
            "evidence_strength": round(evidence_strength, 3),
            "guideline_alignment": round(guideline_alignment, 3),
            "confidence_level": self._get_confidence_level(confidence)
        }
    
    def _normalize_parameter_value(self, param: str, value: Any) -> float:
        """Normalize parameter values to 0-1 scale"""
        # Simulated normalization logic
        if isinstance(value, (int, float)):
            return min(max(value / 100.0, 0.0), 1.0)
        elif isinstance(value, str):
            # Simple hash-based normalization for string values
            return (hash(value.lower()) % 100) / 100.0
        elif isinstance(value, bool):
            return 1.0 if value else 0.0
        else:
            return 0.5  # Default for unknown types
    
    def _calculate_evidence_strength(self, parameters: Dict[str, Any]) -> float:
        """Calculate evidence strength based on available parameters"""
        # Simulated evidence strength calculation
        strong_evidence_params = ["biomarkers", "molecular_profile", "histology"]
        strength = 0.5  # Base strength
        
        for param in strong_evidence_params:
            if param in parameters and parameters[param]:
                strength += 0.15
        
        return min(strength, 1.0)
    
    def _calculate_guideline_alignment(self, recommendation: Dict[str, Any]) -> float:
        """Calculate alignment with clinical guidelines"""
        # Simulated guideline alignment calculation
        return 0.85 + random.uniform(-0.1, 0.1)  # 75-95% alignment
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert numerical confidence to categorical level"""
        if confidence >= 0.9:
            return "Very High"
        elif confidence >= 0.75:
            return "High"
        elif confidence >= 0.6:
            return "Moderate"
        elif confidence >= 0.4:
            return "Low"
        else:
            return "Very Low"
    
    def _generate_ui_metrics(self, adci_score: float, confidence_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate UI-specific metrics for Surgify integration"""
        return {
            "confidence_color": self._get_confidence_color(confidence_metrics["overall_confidence"]),
            "recommendation_strength": "Strong" if adci_score > 0.8 else "Moderate" if adci_score > 0.6 else "Weak",
            "ui_priority": "high" if confidence_metrics["overall_confidence"] > 0.8 else "medium",
            "display_alerts": confidence_metrics["overall_confidence"] < 0.6,
            "progress_percentage": int(adci_score * 100),
            "confidence_percentage": int(confidence_metrics["overall_confidence"] * 100)
        }
    
    def _get_confidence_color(self, confidence: float) -> str:
        """Get color coding for confidence level"""
        if confidence >= 0.8:
            return "#22c55e"  # Green
        elif confidence >= 0.6:
            return "#eab308"  # Yellow
        else:
            return "#ef4444"  # Red
    
    def _generate_cache_key(self, patient_id: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key for results"""
        import hashlib
        param_str = str(sorted(parameters.items()))
        return hashlib.md5(f"{patient_id}:{param_str}".encode()).hexdigest()
    
    def _validate_parameters(self, parameters: Dict[str, Any]):
        """Validate input parameters"""
        required_params = ["tumor_stage", "histology"]
        missing = [p for p in required_params if p not in parameters]
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")
    
    async def _generate_recommendation(
        self, 
        adci_score: float, 
        parameters: Dict[str, Any], 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate primary treatment recommendation"""
        
        # Simulate recommendation logic based on ADCI score
        if adci_score >= 0.8:
            recommendation_type = "Surgical Resection"
            treatment_plan = "Proceed with laparoscopic gastrectomy"
            urgency = "High"
        elif adci_score >= 0.6:
            recommendation_type = "Neoadjuvant Therapy"
            treatment_plan = "FLOT protocol followed by surgical evaluation"
            urgency = "Medium"
        else:
            recommendation_type = "Further Evaluation"
            treatment_plan = "Additional staging and multidisciplinary review"
            urgency = "Low"
        
        return {
            "type": recommendation_type,
            "plan": treatment_plan,
            "urgency": urgency,
            "adci_score": adci_score,
            "rationale": f"Based on ADCI score of {adci_score:.3f} and available parameters",
            "next_steps": self._generate_next_steps(recommendation_type),
            "contraindications": self._check_contraindications(parameters)
        }
    
    async def _generate_alternatives(
        self, 
        adci_score: float, 
        parameters: Dict[str, Any], 
        primary_recommendation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate alternative treatment options"""
        alternatives = []
        
        # Conservative alternative
        alternatives.append({
            "type": "Conservative Management",
            "plan": "Active surveillance with regular monitoring",
            "confidence": max(0.3, adci_score - 0.2),
            "rationale": "Lower risk approach with close monitoring"
        })
        
        # Aggressive alternative
        if adci_score < 0.8:
            alternatives.append({
                "type": "Extended Surgical Approach",
                "plan": "Total gastrectomy with extended lymphadenectomy",
                "confidence": min(0.9, adci_score + 0.15),
                "rationale": "More comprehensive surgical intervention"
            })
        
        return alternatives
    
    def _generate_next_steps(self, recommendation_type: str) -> List[str]:
        """Generate next steps based on recommendation"""
        steps_map = {
            "Surgical Resection": [
                "Schedule pre-operative assessment",
                "Anesthesia consultation",
                "Nutritional optimization",
                "Surgical team coordination"
            ],
            "Neoadjuvant Therapy": [
                "Oncology consultation",
                "FLOT protocol initiation",
                "Response monitoring schedule",
                "Surgical re-evaluation timeline"
            ],
            "Further Evaluation": [
                "Additional staging studies",
                "Multidisciplinary team review",
                "Second opinion consideration",
                "Patient counseling session"
            ]
        }
        return steps_map.get(recommendation_type, ["Standard follow-up"])
    
    def _check_contraindications(self, parameters: Dict[str, Any]) -> List[str]:
        """Check for treatment contraindications"""
        contraindications = []
        
        if parameters.get("performance_status", 100) < 60:
            contraindications.append("Poor performance status")
        
        if parameters.get("comorbidities", []):
            contraindications.append("Significant comorbidities present")
        
        return contraindications
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get engine performance statistics"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "average_response_time": round(avg_response_time, 4),
            "cache_hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
            "total_decisions": self.cache_hits + self.cache_misses,
            "cache_size": len(self.cache),
            "target_met": avg_response_time < 0.15  # <150ms target
        }
