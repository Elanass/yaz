"""
Precision Decision Engine
Combines impact analysis with statistical prediction models and MCDA methodology
"""

from typing import Dict, List, Any, Optional, Tuple
import asyncio
from datetime import datetime
import numpy as np
import logging

from core.services.logger import get_logger, audit_log
from core.utils.validation import validate_patient_data
from core.utils.metrics import weighted_sum, calculate_confidence

logger = get_logger(__name__)

class ImpactAnalyzer:
    """
    Analyzes impact of different treatment options (FLOT vs. surgery)
    """
    
    def __init__(self):
        """Initialize the impact analyzer"""
        # Default risk factors and weights
        self.risk_factors = {
            "age": {"weight": 0.2, "threshold": 70},
            "comorbidities": {"weight": 0.3, "per_item": 0.05},
            "tumor_stage": {
                "weight": 0.5,
                "values": {
                    "T1N0M0": 0.1,
                    "T2N0M0": 0.3,
                    "T3N0M0": 0.5,
                    "T1N1M0": 0.4,
                    "T2N1M0": 0.6,
                    "T3N1M0": 0.7,
                    "T4N0M0": 0.8,
                    "T4N1M0": 0.9,
                    "T*N*M1": 1.0
                }
            }
        }
    
    def calculate_base_risk(self, patient: Dict[str, Any]) -> float:
        """Calculate base risk score for a patient"""
        risk_score = 0.0
        
        # Age risk
        age = int(patient.get("age", 0))
        if age > self.risk_factors["age"]["threshold"]:
            age_factor = (age - self.risk_factors["age"]["threshold"]) / 30  # Normalize
            risk_score += age_factor * self.risk_factors["age"]["weight"]
        
        # Comorbidities risk
        comorbidities = patient.get("comorbidities", [])
        if isinstance(comorbidities, str):
            comorbidities = comorbidities.split(",")
        comorbidity_count = len(comorbidities)
        risk_score += min(comorbidity_count * self.risk_factors["comorbidities"]["per_item"], 
                          self.risk_factors["comorbidities"]["weight"])
        
        # Tumor stage risk
        tumor_stage = patient.get("tumor_stage", "T1N0M0")
        stage_risk = self.risk_factors["tumor_stage"]["values"].get(
            tumor_stage, 
            self.risk_factors["tumor_stage"]["values"].get("T*N*M1", 0.5)
        )
        risk_score += stage_risk * self.risk_factors["tumor_stage"]["weight"]
        
        return min(risk_score, 1.0)  # Cap at 1.0
    
    def analyze_surgery_impact(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze surgery impact"""
        base_risk = self.calculate_base_risk(patient)
        
        # Surgery-specific factors
        tumor_location = patient.get("tumor_location", "").lower()
        is_proximal = "proximal" in tumor_location or "cardia" in tumor_location
        
        # Adjust risk based on tumor location
        location_factor = 0.15 if is_proximal else 0.05
        surgery_risk = base_risk + location_factor
        surgery_risk = min(surgery_risk, 1.0)  # Cap at 1.0
        
        return {
            "treatment": "surgery",
            "base_risk": round(base_risk, 3),
            "adjusted_risk": round(surgery_risk, 3),
            "risk_level": "high" if surgery_risk > 0.7 else "medium" if surgery_risk > 0.4 else "low",
            "recommended": surgery_risk < 0.6,
            "confidence": 0.8 - (0.3 * surgery_risk)  # Lower confidence with higher risk
        }
    
    def analyze_flot_impact(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze FLOT chemotherapy impact"""
        base_risk = self.calculate_base_risk(patient)
        
        # FLOT-specific factors
        age = int(patient.get("age", 0))
        performance_status = int(patient.get("performance_status", 1))
        
        # Adjust risk based on age and performance status
        age_factor = 0.01 * max(0, age - 65)
        performance_factor = 0.1 * performance_status
        
        flot_risk = base_risk + age_factor + performance_factor
        flot_risk = min(flot_risk, 1.0)  # Cap at 1.0
        
        # FLOT is generally preferred for advanced stages
        tumor_stage = patient.get("tumor_stage", "T1N0M0")
        is_advanced = any(x in tumor_stage for x in ["T3", "T4", "N1", "M1"])
        
        return {
            "treatment": "FLOT",
            "base_risk": round(base_risk, 3),
            "adjusted_risk": round(flot_risk, 3),
            "risk_level": "high" if flot_risk > 0.7 else "medium" if flot_risk > 0.4 else "low",
            "recommended": is_advanced and flot_risk < 0.7,
            "confidence": 0.75 - (0.2 * flot_risk)  # Lower confidence with higher risk
        }

class PrecisionEngine:
    """
    Precision Decision Engine combining impact analysis with statistical prediction models
    """
    
    def __init__(self):
        """Initialize the precision engine"""
        self.impact_analyzer = ImpactAnalyzer()
        # Multi-Criteria Decision Analysis weights: lower risk and higher confidence
        self.criteria_weights = {"risk_score": 0.5, "confidence": 0.5}
    
    def analyze(self, patients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze a list of patients and return impact insights"""
        insights = []
        for patient in patients:
            surgery = self.impact_analyzer.analyze_surgery_impact(patient)
            flot = self.impact_analyzer.analyze_flot_impact(patient)
            # Compute MCDA score and confidence intervals for each option
            for option in (surgery, flot):
                option['mcda_score'] = round(self._compute_mcda_score(option), 3)
                lower = max(option['confidence'] - 0.1, 0)
                upper = min(option['confidence'] + 0.1, 1)
                option['confidence_interval'] = [round(lower, 3), round(upper, 3)]
            insights.append({"surgery": surgery, "flot": flot})
        return insights
    
    def _compute_mcda_score(self, option: Dict[str, Any]) -> float:
        """Compute MCDA score using shared weighted_sum"""
        values = {
            'risk_score': 1.0 - option['adjusted_risk'],
            'confidence': option['confidence']
        }
        return weighted_sum(values, self.criteria_weights)


class MCDAEngine:
    """
    Multi-Criteria Decision Analysis (MCDA) Engine for surgical decision precision
    
    This engine applies multiple decision criteria with weighted scoring to
    provide evidence-based decision support for gastric surgery cases with
    FLOT optimization, supporting the precision medicine approach.
    """
    
    def __init__(self):
        """Initialize the MCDA engine with precision criteria"""
        self.version = "1.0"
        self.criteria = {
            "clinical": {
                "weight": 0.35,
                "subcriteria": {
                    "tumor_characteristics": {"weight": 0.4},
                    "patient_comorbidities": {"weight": 0.3},
                    "response_to_flot": {"weight": 0.3}
                }
            },
            "surgical": {
                "weight": 0.3,
                "subcriteria": {
                    "technical_feasibility": {"weight": 0.4},
                    "expected_complications": {"weight": 0.3},
                    "functional_outcome": {"weight": 0.3}
                }
            },
            "oncological": {
                "weight": 0.25,
                "subcriteria": {
                    "r0_probability": {"weight": 0.5},
                    "lymph_node_yield": {"weight": 0.3},
                    "survival_benefit": {"weight": 0.2}
                }
            },
            "quality_of_life": {
                "weight": 0.1,
                "subcriteria": {
                    "short_term_impact": {"weight": 0.3},
                    "long_term_function": {"weight": 0.7}
                }
            }
        }
        logger.info(f"MCDA Engine initialized with version {self.version}")
    
    async def analyze(self, patient_data: dict, context: Optional[dict] = None) -> dict:
        """
        Analyze decision options using MCDA methodology
        
        Args:
            patient_data: Dictionary containing patient clinical data
            context: Optional context for analysis
            
        Returns:
            Dictionary with MCDA analysis including scores and recommendations
        """
        # Validate input
        is_valid, missing_fields = validate_patient_data(patient_data, "mcda")
        if not is_valid:
            raise ValueError(f"Invalid input data for MCDA Engine: missing {', '.join(missing_fields)}")
            
        # Log analysis start with audit trail
        audit_log(
            action="mcda_analysis_start",
            resource_type="patient_data",
            resource_id=patient_data.get("patient_id", "unknown"),
            details="Starting MCDA analysis"
        )
        
        # Define decision alternatives
        alternatives = self._define_alternatives(patient_data)
        
        # Evaluate alternatives against criteria
        scores = self._evaluate_alternatives(alternatives, patient_data, context)
        
        # Calculate overall scores
        overall_scores = self._calculate_overall_scores(scores)
        
        # Identify optimal alternative
        optimal = self._identify_optimal_alternative(overall_scores)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(optimal, alternatives, overall_scores, patient_data)
        
        # Compile result
        result = {
            "alternatives": alternatives,
            "criteria_scores": scores,
            "overall_scores": overall_scores,
            "optimal_alternative": optimal,
            "recommendations": recommendations,
            "confidence": self._calculate_confidence(overall_scores),
            "uncertainty": self._estimate_uncertainty(scores),
            "timestamp": datetime.utcnow().isoformat(),
            "engine_version": self.version
        }
        
        # Add overall score
        result["overall_score"] = optimal["score"]
        
        # Log analysis completion
        audit_log(
            action="mcda_analysis_complete",
            resource_type="patient_data",
            resource_id=patient_data.get("patient_id", "unknown"),
            details=f"MCDA analysis completed with recommendation: {optimal['alternative']}"
        )
        
        return result
    
    def _define_alternatives(self, patient_data: dict) -> List[Dict[str, Any]]:
        """
        Define decision alternatives based on patient data
        
        Args:
            patient_data: Patient clinical data
            
        Returns:
            List of alternative dictionaries
        """
        alternatives = []
        
        # Basic alternative set for gastric cancer with FLOT
        alternatives.append({
            "id": "alt1",
            "alternative": "Standard FLOT + Open Gastrectomy",
            "description": "Standard 4+4 FLOT cycles with open gastrectomy"
        })
        
        alternatives.append({
            "id": "alt2",
            "alternative": "Standard FLOT + Minimally Invasive Gastrectomy",
            "description": "Standard 4+4 FLOT cycles with laparoscopic/robotic approach"
        })
        
        alternatives.append({
            "id": "alt3",
            "alternative": "Extended FLOT + Open Gastrectomy",
            "description": "Extended FLOT protocol (6+2 cycles) with open gastrectomy"
        })
        
        alternatives.append({
            "id": "alt4",
            "alternative": "Extended FLOT + Minimally Invasive Gastrectomy",
            "description": "Extended FLOT protocol (6+2 cycles) with laparoscopic/robotic approach"
        })
        
        # Add patient-specific alternatives based on data
        age = patient_data.get("age", 65)
        comorbidities = patient_data.get("comorbidities", [])
        
        # For elderly or high-risk patients
        if age > 75 or len(comorbidities) >= 3:
            alternatives.append({
                "id": "alt5",
                "alternative": "Reduced FLOT + Open Gastrectomy",
                "description": "Dose-reduced FLOT with open gastrectomy for high-risk patients"
            })
        
        # For locally advanced disease
        if patient_data.get("tumor_stage", "").startswith("T4") or "N2" in patient_data.get("tumor_stage", ""):
            alternatives.append({
                "id": "alt6",
                "alternative": "Extended FLOT + Extended Lymphadenectomy",
                "description": "Extended FLOT with D2+ lymphadenectomy for advanced disease"
            })
        
        return alternatives
    
    def _evaluate_alternatives(
        self, 
        alternatives: List[Dict[str, Any]], 
        patient_data: dict,
        context: Optional[dict] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Evaluate each alternative against the criteria
        
        Args:
            alternatives: List of alternatives
            patient_data: Patient clinical data
            context: Optional context data
            
        Returns:
            Dictionary with scores for each alternative against each criterion
        """
        scores = {}
        
        for alt in alternatives:
            alt_id = alt["id"]
            scores[alt_id] = {}
            
            # Evaluate clinical criteria
            clinical_score = self._evaluate_clinical(alt, patient_data)
            scores[alt_id]["clinical"] = clinical_score
            
            # Evaluate surgical criteria
            surgical_score = self._evaluate_surgical(alt, patient_data)
            scores[alt_id]["surgical"] = surgical_score
            
            # Evaluate oncological criteria
            oncological_score = self._evaluate_oncological(alt, patient_data)
            scores[alt_id]["oncological"] = oncological_score
            
            # Evaluate quality of life criteria
            qol_score = self._evaluate_quality_of_life(alt, patient_data)
            scores[alt_id]["quality_of_life"] = qol_score
            
            # Store subcriteria scores
            scores[alt_id]["subcriteria"] = {
                "clinical": self._evaluate_clinical_subcriteria(alt, patient_data),
                "surgical": self._evaluate_surgical_subcriteria(alt, patient_data),
                "oncological": self._evaluate_oncological_subcriteria(alt, patient_data),
                "quality_of_life": self._evaluate_qol_subcriteria(alt, patient_data)
            }
        
        return scores
    
    def _evaluate_clinical(self, alternative: Dict[str, Any], patient_data: dict) -> float:
        """Evaluate alternative against clinical criteria"""
        subcriteria = self._evaluate_clinical_subcriteria(alternative, patient_data)
        
        # Weighted sum of subcriteria
        clinical_criteria = self.criteria["clinical"]["subcriteria"]
        score = sum(subcriteria[sc] * clinical_criteria[sc]["weight"] for sc in subcriteria)
        
        return score
    
    def _evaluate_clinical_subcriteria(self, alternative: Dict[str, Any], patient_data: dict) -> Dict[str, float]:
        """Evaluate clinical subcriteria"""
        scores = {}
        
        # Tumor characteristics
        tumor_score = 0.0
        if "Extended FLOT" in alternative["alternative"] and patient_data.get("tumor_stage", "").startswith(("T3", "T4")):
            tumor_score = 0.9  # Extended FLOT better for advanced tumors
        elif "Standard FLOT" in alternative["alternative"] and patient_data.get("tumor_stage", "").startswith(("T1", "T2")):
            tumor_score = 0.8  # Standard FLOT sufficient for early tumors
        else:
            tumor_score = 0.6
        scores["tumor_characteristics"] = tumor_score
        
        # Patient comorbidities
        comorbidity_score = 0.0
        comorbidities = patient_data.get("comorbidities", [])
        age = patient_data.get("age", 65)
        
        if "Reduced FLOT" in alternative["alternative"] and (len(comorbidities) >= 3 or age > 75):
            comorbidity_score = 0.9  # Reduced FLOT better for high-risk patients
        elif "Minimally Invasive" in alternative["alternative"] and len(comorbidities) >= 2:
            comorbidity_score = 0.8  # MIS better for comorbid patients
        elif "Open" in alternative["alternative"] and len(comorbidities) < 2:
            comorbidity_score = 0.7  # Open appropriate for fit patients
        else:
            comorbidity_score = 0.6
        scores["patient_comorbidities"] = comorbidity_score
        
        # Response to FLOT
        response_score = 0.0
        flot_response = patient_data.get("response_to_neoadjuvant", "")
        
        if "Extended FLOT" in alternative["alternative"] and flot_response == "good":
            response_score = 0.9  # Extended FLOT if good initial response
        elif "Standard FLOT" in alternative["alternative"] and flot_response == "moderate":
            response_score = 0.8  # Standard FLOT if moderate response
        elif "Reduced FLOT" in alternative["alternative"] and flot_response == "poor":
            response_score = 0.7  # Reduced FLOT if poor tolerance
        else:
            response_score = 0.6
        scores["response_to_flot"] = response_score
        
        return scores
    
    def _evaluate_surgical(self, alternative: Dict[str, Any], patient_data: dict) -> float:
        """Evaluate alternative against surgical criteria"""
        subcriteria = self._evaluate_surgical_subcriteria(alternative, patient_data)
        
        # Weighted sum of subcriteria
        surgical_criteria = self.criteria["surgical"]["subcriteria"]
        score = sum(subcriteria[sc] * surgical_criteria[sc]["weight"] for sc in subcriteria)
        
        return score
    
    def _evaluate_surgical_subcriteria(self, alternative: Dict[str, Any], patient_data: dict) -> Dict[str, float]:
        """Evaluate surgical subcriteria"""
        scores = {}
        
        # Technical feasibility
        technical_score = 0.0
        bmi = patient_data.get("bmi", 25)
        previous_surgeries = patient_data.get("previous_surgeries", [])
        
        if "Open" in alternative["alternative"] and (bmi > 35 or len(previous_surgeries) > 0):
            technical_score = 0.9  # Open better for obese or previously operated
        elif "Minimally Invasive" in alternative["alternative"] and bmi < 30 and len(previous_surgeries) == 0:
            technical_score = 0.9  # MIS better for non-obese without previous surgery
        else:
            technical_score = 0.7
        scores["technical_feasibility"] = technical_score
        
        # Expected complications
        complication_score = 0.0
        age = patient_data.get("age", 65)
        comorbidities = patient_data.get("comorbidities", [])
        
        if "Minimally Invasive" in alternative["alternative"] and age < 70 and len(comorbidities) <= 1:
            complication_score = 0.9  # MIS for younger, healthier patients
        elif "Open" in alternative["alternative"] and age > 75:
            complication_score = 0.7  # Open may have more complications in elderly
        elif "Reduced FLOT" in alternative["alternative"]:
            complication_score = 0.8  # Reduced FLOT for fewer complications
        else:
            complication_score = 0.6
        scores["expected_complications"] = complication_score
        
        # Functional outcome
        functional_score = 0.0
        if "Minimally Invasive" in alternative["alternative"]:
            functional_score = 0.9  # Better short-term functional outcomes
        elif "Open" in alternative["alternative"]:
            functional_score = 0.7  # Slower recovery
        else:
            functional_score = 0.6
        scores["functional_outcome"] = functional_score
        
        return scores
    
    def _evaluate_oncological(self, alternative: Dict[str, Any], patient_data: dict) -> float:
        """Evaluate alternative against oncological criteria"""
        subcriteria = self._evaluate_oncological_subcriteria(alternative, patient_data)
        
        # Weighted sum of subcriteria
        oncological_criteria = self.criteria["oncological"]["subcriteria"]
        score = sum(subcriteria[sc] * oncological_criteria[sc]["weight"] for sc in subcriteria)
        
        return score
    
    def _evaluate_oncological_subcriteria(self, alternative: Dict[str, Any], patient_data: dict) -> Dict[str, float]:
        """Evaluate oncological subcriteria"""
        scores = {}
        
        # R0 probability
        r0_score = 0.0
        tumor_stage = patient_data.get("tumor_stage", "")
        
        if "Extended FLOT" in alternative["alternative"] and tumor_stage.startswith(("T3", "T4")):
            r0_score = 0.9  # Extended FLOT better for R0 in advanced tumors
        elif "Extended Lymphadenectomy" in alternative["alternative"] and "N" in tumor_stage:
            r0_score = 0.8  # Extended lymphadenectomy for nodal disease
        elif "Standard FLOT" in alternative["alternative"] and tumor_stage.startswith(("T1", "T2")):
            r0_score = 0.9  # Standard FLOT sufficient for early tumors
        else:
            r0_score = 0.7
        scores["r0_probability"] = r0_score
        
        # Lymph node yield
        ln_score = 0.0
        if "Extended Lymphadenectomy" in alternative["alternative"]:
            ln_score = 0.9  # Highest lymph node yield
        elif "Open" in alternative["alternative"]:
            ln_score = 0.8  # Good lymph node yield
        elif "Minimally Invasive" in alternative["alternative"]:
            ln_score = 0.7  # Potentially fewer lymph nodes
        else:
            ln_score = 0.6
        scores["lymph_node_yield"] = ln_score
        
        # Survival benefit
        survival_score = 0.0
        if "Extended FLOT" in alternative["alternative"] and tumor_stage.startswith(("T3", "T4")):
            survival_score = 0.9  # Best survival for advanced disease
        elif "Standard FLOT" in alternative["alternative"] and tumor_stage.startswith(("T1", "T2")):
            survival_score = 0.8  # Good survival for early disease
        elif "Reduced FLOT" in alternative["alternative"]:
            survival_score = 0.6  # Compromised survival
        else:
            survival_score = 0.7
        scores["survival_benefit"] = survival_score
        
        return scores
    
    def _evaluate_quality_of_life(self, alternative: Dict[str, Any], patient_data: dict) -> float:
        """Evaluate alternative against quality of life criteria"""
        subcriteria = self._evaluate_qol_subcriteria(alternative, patient_data)
        
        # Weighted sum of subcriteria
        qol_criteria = self.criteria["quality_of_life"]["subcriteria"]
        score = sum(subcriteria[sc] * qol_criteria[sc]["weight"] for sc in subcriteria)
        
        return score
    
    def _evaluate_qol_subcriteria(self, alternative: Dict[str, Any], patient_data: dict) -> Dict[str, float]:
        """Evaluate quality of life subcriteria"""
        scores = {}
        
        # Short term impact
        short_term_score = 0.0
        if "Minimally Invasive" in alternative["alternative"]:
            short_term_score = 0.9  # Better short-term QoL
        elif "Reduced FLOT" in alternative["alternative"]:
            short_term_score = 0.8  # Less toxicity
        elif "Open" in alternative["alternative"]:
            short_term_score = 0.6  # More short-term impact
        else:
            short_term_score = 0.7
        scores["short_term_impact"] = short_term_score
        
        # Long term function
        long_term_score = 0.0
        if "Extended FLOT" in alternative["alternative"] and "Minimally Invasive" in alternative["alternative"]:
            long_term_score = 0.9  # Best long-term if disease controlled
        elif "Standard FLOT" in alternative["alternative"]:
            long_term_score = 0.8  # Good long-term function
        elif "Reduced FLOT" in alternative["alternative"]:
            long_term_score = 0.7  # Potential recurrence impacts QoL
        else:
            long_term_score = 0.7
        scores["long_term_function"] = long_term_score
        
        return scores
    
    def _calculate_overall_scores(self, scores: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Calculate overall scores for each alternative
        
        Args:
            scores: Dictionary with scores for each alternative against each criterion
            
        Returns:
            Dictionary with overall scores for each alternative
        """
        overall_scores = {}
        
        for alt_id, alt_scores in scores.items():
            # Calculate weighted sum
            overall_score = 0.0
            
            for criterion, score in alt_scores.items():
                # Skip subcriteria dictionary
                if criterion == "subcriteria":
                    continue
                    
                weight = self.criteria[criterion]["weight"]
                overall_score += score * weight
                
            overall_scores[alt_id] = overall_score
            
        return overall_scores
    
    def _identify_optimal_alternative(self, overall_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Identify the optimal alternative based on overall scores
        
        Args:
            overall_scores: Dictionary with overall scores for each alternative
            
        Returns:
            Dictionary with optimal alternative
        """
        # Find alternative with highest score
        optimal_id = max(overall_scores, key=overall_scores.get)
        optimal_score = overall_scores[optimal_id]
        
        # Create result object
        result = {
            "id": optimal_id,
            "score": optimal_score
        }
        
        return result
    
    def _generate_recommendations(
        self,
        optimal: Dict[str, Any],
        alternatives: List[Dict[str, Any]],
        overall_scores: Dict[str, float],
        patient_data: dict
    ) -> Dict[str, Any]:
        """
        Generate recommendations based on optimal alternative
        
        Args:
            optimal: Optimal alternative information
            alternatives: List of all alternatives
            overall_scores: Dictionary with overall scores
            patient_data: Patient clinical data
            
        Returns:
            Dictionary with recommendations
        """
        # Find optimal alternative details
        optimal_alt = next((alt for alt in alternatives if alt["id"] == optimal["id"]), None)
        
        if not optimal_alt:
            return {"error": "Optimal alternative not found"}
            
        # Create recommendation
        recommendation = {
            "primary": optimal_alt["alternative"],
            "description": optimal_alt["description"],
            "score": optimal["score"],
            "confidence": self._calculate_confidence(overall_scores),
            "justification": self._generate_justification(optimal_alt, patient_data),
            "alternatives": []
        }
        
        # Add alternative recommendations
        sorted_alts = sorted(overall_scores.items(), key=lambda x: x[1], reverse=True)
        for alt_id, score in sorted_alts[1:3]:  # Include top 2 alternatives
            alt = next((a for a in alternatives if a["id"] == alt_id), None)
            if alt:
                recommendation["alternatives"].append({
                    "alternative": alt["alternative"],
                    "description": alt["description"],
                    "score": score
                })
                
        return recommendation
    
    def _generate_justification(self, alternative: Dict[str, Any], patient_data: dict) -> str:
        """Generate justification for recommendation"""
        # Simple justification for MVP
        tumor_stage = patient_data.get("tumor_stage", "unknown")
        age = patient_data.get("age", "unknown")
        comorbidities = len(patient_data.get("comorbidities", []))
        
        justification = f"Based on tumor stage {tumor_stage}, patient age {age}, "
        justification += f"and {comorbidities} comorbidities, the recommended approach is {alternative['alternative']}. "
        
        if "Extended FLOT" in alternative["alternative"]:
            justification += "Extended FLOT protocol provides optimal tumor control for this case. "
        elif "Standard FLOT" in alternative["alternative"]:
            justification += "Standard FLOT protocol is appropriate for disease stage and patient condition. "
        elif "Reduced FLOT" in alternative["alternative"]:
            justification += "Reduced FLOT protocol balances treatment efficacy with patient tolerance. "
            
        if "Minimally Invasive" in alternative["alternative"]:
            justification += "Minimally invasive approach is feasible and may reduce postoperative complications. "
        elif "Open" in alternative["alternative"]:
            justification += "Open approach provides optimal access for complex resection. "
            
        if "Extended Lymphadenectomy" in alternative["alternative"]:
            justification += "Extended lymphadenectomy is recommended for nodal staging and clearance. "
            
        return justification
    
    def _calculate_confidence(self, overall_scores: Dict[str, float]) -> float:
        """Calculate confidence using shared calculate_confidence"""
        return calculate_confidence(overall_scores)
    
    def _estimate_uncertainty(self, scores: Dict[str, Dict[str, float]]) -> float:
        """
        Estimate uncertainty in the analysis
        
        Args:
            scores: Dictionary with scores
            
        Returns:
            Uncertainty score between 0 and 1
        """
        # Simple implementation for MVP - to be enhanced
        # Higher variation in subcriteria scores indicates more uncertainty
        variations = []
        
        for alt_id, alt_scores in scores.items():
            if "subcriteria" in alt_scores:
                for criterion, subcriteria in alt_scores["subcriteria"].items():
                    if subcriteria:
                        variation = np.std(list(subcriteria.values()))
                        variations.append(variation)
                        
        if not variations:
            return 0.5
            
        # Average variation normalized to 0-1 scale
        # Higher variation means more uncertainty
        uncertainty = min(np.mean(variations) * 2, 1.0)
        
        return uncertainty
