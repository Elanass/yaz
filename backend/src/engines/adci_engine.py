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


class ADCIEngine:
    """
    Adaptive Decision Confidence Index Engine
    
    This engine provides evidence-based treatment recommendations
    with confidence scoring and uncertainty quantification.
    """
    
    def __init__(self):
        self.version = "2.1.0"
        self.name = "adci"
        self.settings = get_settings()
        
        # ADCI parameters and weights
        self.parameter_weights = {
            "tumor_stage": 0.25,
            "histology": 0.15,
            "biomarkers": 0.20,
            "performance_status": 0.15,
            "comorbidities": 0.10,
            "patient_preferences": 0.10,
            "molecular_profile": 0.05
        }
        
        # Confidence modifiers
        self.confidence_modifiers = {
            "data_completeness": 0.3,
            "evidence_strength": 0.4,
            "guideline_alignment": 0.3
        }
    
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
            adci_score, score_breakdown = await self._calculate_adci_score(parameters)
            
            # Generate primary recommendation
            primary_recommendation = await self._generate_recommendation(
                adci_score, parameters, context
            )
            
            # Calculate confidence metrics
            confidence_metrics = await self._calculate_confidence(
                parameters, primary_recommendation, context
            )
            
            # Generate alternative options if requested
            alternatives = []
            if include_alternatives:
                alternatives = await self._generate_alternatives(
                    adci_score, parameters, primary_recommendation
                )
            
            # Assess risks and contraindications
            risk_assessment = await self._assess_risks(parameters, primary_recommendation)
            
            # Generate evidence summary
            evidence_summary = await self._generate_evidence_summary(
                parameters, primary_recommendation
            )
            
            # Create reasoning chain
            reasoning_chain = self._build_reasoning_chain(
                parameters, adci_score, score_breakdown, confidence_metrics
            )
            
            # Generate monitoring recommendations
            monitoring = await self._generate_monitoring_recommendations(
                primary_recommendation, parameters
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Compile result
            result = {
                "engine_name": self.name,
                "engine_version": self.version,
                "adci_score": float(adci_score),
                "score_breakdown": score_breakdown,
                "recommendation": primary_recommendation,
                "confidence_score": float(confidence_metrics["overall_confidence"]),
                "confidence_level": self._get_confidence_level(confidence_metrics["overall_confidence"]),
                "confidence_metrics": confidence_metrics,
                "alternative_options": alternatives,
                "risk_assessment": risk_assessment,
                "evidence_summary": evidence_summary,
                "reasoning_chain": reasoning_chain,
                "monitoring_recommendations": monitoring,
                "warnings": self._generate_warnings(parameters, risk_assessment),
                "data_completeness": self._calculate_data_completeness(parameters),
                "processing_time_seconds": processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"ADCI decision processed for patient {patient_id}: score={adci_score:.3f}, confidence={confidence_metrics['overall_confidence']:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"ADCI engine error for patient {patient_id}: {str(e)}")
            raise
    
    async def _calculate_adci_score(self, parameters: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Calculate the core ADCI score"""
        
        scores = {}
        weighted_sum = 0.0
        total_weight = 0.0
        
        # Tumor stage scoring
        if "tumor_stage" in parameters:
            stage_score = self._score_tumor_stage(parameters["tumor_stage"])
            scores["tumor_stage"] = stage_score
            weighted_sum += stage_score * self.parameter_weights["tumor_stage"]
            total_weight += self.parameter_weights["tumor_stage"]
        
        # Histology scoring
        if "histology" in parameters:
            hist_score = self._score_histology(parameters["histology"])
            scores["histology"] = hist_score
            weighted_sum += hist_score * self.parameter_weights["histology"]
            total_weight += self.parameter_weights["histology"]
        
        # Biomarker scoring
        if "biomarkers" in parameters:
            bio_score = await self._score_biomarkers(parameters["biomarkers"])
            scores["biomarkers"] = bio_score
            weighted_sum += bio_score * self.parameter_weights["biomarkers"]
            total_weight += self.parameter_weights["biomarkers"]
        
        # Performance status scoring
        if "performance_status" in parameters:
            ps_score = self._score_performance_status(parameters["performance_status"])
            scores["performance_status"] = ps_score
            weighted_sum += ps_score * self.parameter_weights["performance_status"]
            total_weight += self.parameter_weights["performance_status"]
        
        # Comorbidities scoring
        if "comorbidities" in parameters:
            comorbid_score = self._score_comorbidities(parameters["comorbidities"])
            scores["comorbidities"] = comorbid_score
            weighted_sum += comorbid_score * self.parameter_weights["comorbidities"]
            total_weight += self.parameter_weights["comorbidities"]
        
        # Patient preferences scoring
        if "patient_preferences" in parameters:
            pref_score = self._score_patient_preferences(parameters["patient_preferences"])
            scores["patient_preferences"] = pref_score
            weighted_sum += pref_score * self.parameter_weights["patient_preferences"]
            total_weight += self.parameter_weights["patient_preferences"]
        
        # Calculate final ADCI score
        if total_weight > 0:
            adci_score = weighted_sum / total_weight
        else:
            adci_score = 0.5  # Neutral score if no parameters
        
        # Normalize to 0-1 range
        adci_score = max(0.0, min(1.0, adci_score))
        
        return adci_score, scores
    
    def _score_tumor_stage(self, stage: str) -> float:
        """Score tumor stage (T1-T4, N0-N3, M0-M1)"""
        stage_scores = {
            "T1N0M0": 0.9,  # Early stage, excellent prognosis
            "T1N1M0": 0.8,
            "T2N0M0": 0.8,
            "T2N1M0": 0.7,
            "T3N0M0": 0.7,
            "T3N1M0": 0.6,
            "T3N2M0": 0.5,
            "T4N0M0": 0.5,
            "T4N1M0": 0.4,
            "T4N2M0": 0.3,
            "T4N3M0": 0.2,
            # Metastatic disease
            "M1": 0.1
        }
        
        # Handle various stage formats
        stage_clean = stage.upper().replace(" ", "")
        
        if "M1" in stage_clean:
            return 0.1
        
        return stage_scores.get(stage_clean, 0.5)  # Default to medium score
    
    def _score_histology(self, histology: str) -> float:
        """Score histological type"""
        histology_scores = {
            "intestinal": 0.7,     # Better prognosis
            "diffuse": 0.4,        # Worse prognosis
            "mixed": 0.55,         # Intermediate
            "signet_ring": 0.3,    # Poor prognosis
            "mucinous": 0.6,       # Variable prognosis
            "papillary": 0.8,      # Good prognosis
            "tubular": 0.7,        # Good prognosis
        }
        
        histology_clean = histology.lower().replace(" ", "_")
        return histology_scores.get(histology_clean, 0.5)
    
    async def _score_biomarkers(self, biomarkers: Dict[str, Any]) -> float:
        """Score biomarker profile"""
        score = 0.5  # Base score
        
        # HER2 status
        if "her2" in biomarkers:
            if biomarkers["her2"] == "positive":
                score += 0.2  # HER2+ has targeted therapy options
            elif biomarkers["her2"] == "negative":
                score -= 0.1
        
        # MSI status
        if "msi" in biomarkers:
            if biomarkers["msi"] == "high":
                score += 0.3  # MSI-H responds well to immunotherapy
            elif biomarkers["msi"] == "stable":
                score -= 0.1
        
        # PD-L1 expression
        if "pdl1" in biomarkers:
            pdl1_score = biomarkers["pdl1"]
            if isinstance(pdl1_score, (int, float)):
                if pdl1_score >= 10:  # High expression
                    score += 0.2
                elif pdl1_score >= 1:  # Low expression
                    score += 0.1
        
        # KRAS status
        if "kras" in biomarkers:
            if biomarkers["kras"] == "mutant":
                score -= 0.1  # Generally worse prognosis
        
        # Normalize to 0-1 range
        return max(0.0, min(1.0, score))
    
    def _score_performance_status(self, ps: Dict[str, Any]) -> float:
        """Score performance status (ECOG, Karnofsky)"""
        score = 0.5
        
        if "ecog" in ps:
            ecog = ps["ecog"]
            if ecog == 0:
                score = 0.9  # Excellent performance
            elif ecog == 1:
                score = 0.7  # Good performance
            elif ecog == 2:
                score = 0.5  # Fair performance
            elif ecog == 3:
                score = 0.3  # Poor performance
            elif ecog >= 4:
                score = 0.1  # Very poor performance
        
        elif "karnofsky" in ps:
            karnofsky = ps["karnofsky"]
            score = karnofsky / 100.0  # Direct conversion
        
        return max(0.0, min(1.0, score))
    
    def _score_comorbidities(self, comorbidities: List[str]) -> float:
        """Score comorbidity burden"""
        if not comorbidities:
            return 0.9  # No comorbidities = high score
        
        # Comorbidity severity weights
        severity_weights = {
            "cardiovascular": 0.3,
            "pulmonary": 0.25,
            "hepatic": 0.35,
            "renal": 0.3,
            "diabetes": 0.2,
            "previous_cancer": 0.25,
            "immunocompromised": 0.4
        }
        
        total_burden = 0.0
        for comorbidity in comorbidities:
            comorbidity_clean = comorbidity.lower()
            for key, weight in severity_weights.items():
                if key in comorbidity_clean:
                    total_burden += weight
                    break
            else:
                total_burden += 0.15  # Default weight for unlisted comorbidities
        
        # Convert burden to score (inverse relationship)
        score = max(0.1, 1.0 - (total_burden / 2.0))
        return min(1.0, score)
    
    def _score_patient_preferences(self, preferences: Dict[str, Any]) -> float:
        """Score patient preferences alignment"""
        score = 0.5  # Neutral starting point
        
        # Treatment aggressiveness preference
        if "treatment_intensity" in preferences:
            intensity = preferences["treatment_intensity"].lower()
            if intensity == "aggressive":
                score += 0.2
            elif intensity == "conservative":
                score -= 0.1
            elif intensity == "moderate":
                score += 0.1
        
        # Quality of life priorities
        if "qol_priority" in preferences:
            qol = preferences["qol_priority"]
            if isinstance(qol, (int, float)):
                if qol >= 8:  # High QoL priority
                    score -= 0.1  # May prefer less aggressive treatment
                elif qol <= 5:  # Lower QoL priority
                    score += 0.1  # May accept more aggressive treatment
        
        return max(0.0, min(1.0, score))
    
    async def _calculate_confidence(
        self,
        parameters: Dict[str, Any],
        recommendation: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate confidence metrics"""
        
        # Data completeness
        data_completeness = self._calculate_data_completeness(parameters)
        
        # Evidence strength (simulated - would integrate with evidence database)
        evidence_strength = await self._assess_evidence_strength(recommendation)
        
        # Guideline alignment
        guideline_alignment = await self._assess_guideline_alignment(recommendation)
        
        # Overall confidence calculation
        overall_confidence = (
            data_completeness * self.confidence_modifiers["data_completeness"] +
            evidence_strength * self.confidence_modifiers["evidence_strength"] +
            guideline_alignment * self.confidence_modifiers["guideline_alignment"]
        )
        
        return {
            "overall_confidence": overall_confidence,
            "data_completeness": data_completeness,
            "evidence_strength": evidence_strength,
            "guideline_alignment": guideline_alignment
        }
    
    def _calculate_data_completeness(self, parameters: Dict[str, Any]) -> float:
        """Calculate how complete the input data is"""
        required_fields = [
            "tumor_stage", "histology", "performance_status"
        ]
        
        important_fields = [
            "biomarkers", "comorbidities", "patient_preferences"
        ]
        
        present_required = sum(1 for field in required_fields if field in parameters)
        present_important = sum(1 for field in important_fields if field in parameters)
        
        required_score = present_required / len(required_fields)
        important_score = present_important / len(important_fields)
        
        # Weight required fields more heavily
        completeness = (required_score * 0.7) + (important_score * 0.3)
        
        return max(0.0, min(1.0, completeness))
    
    async def _assess_evidence_strength(self, recommendation: Dict[str, Any]) -> float:
        """Assess strength of evidence for recommendation"""
        # Simulated evidence assessment
        # In production, this would query the evidence database
        
        treatment_type = recommendation.get("type", "unknown")
        
        evidence_scores = {
            "surgery": 0.9,
            "chemotherapy": 0.8,
            "immunotherapy": 0.7,
            "targeted_therapy": 0.8,
            "radiation": 0.7,
            "supportive_care": 0.6
        }
        
        return evidence_scores.get(treatment_type, 0.5)
    
    async def _assess_guideline_alignment(self, recommendation: Dict[str, Any]) -> float:
        """Assess alignment with clinical guidelines"""
        # Simulated guideline alignment assessment
        # In production, this would check against guideline databases
        
        return 0.85  # Placeholder high alignment score
    
    def _get_confidence_level(self, confidence_score: float) -> str:
        """Convert confidence score to level"""
        if confidence_score >= 0.85:
            return "very_high"
        elif confidence_score >= 0.7:
            return "high"
        elif confidence_score >= 0.5:
            return "medium"
        else:
            return "low"
    
    async def _generate_recommendation(
        self,
        adci_score: float,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate primary treatment recommendation"""
        
        # Extract key clinical parameters
        stage = parameters.get("tumor_stage", "unknown")
        ps = parameters.get("performance_status", {})
        biomarkers = parameters.get("biomarkers", {})
        
        # Decision logic based on ADCI score and clinical parameters
        if adci_score >= 0.8:
            # High score - aggressive curative treatment
            return {
                "type": "multimodal_curative",
                "components": {
                    "surgery": {
                        "type": "gastrectomy",
                        "approach": "minimally_invasive",
                        "timing": "after_neoadjuvant"
                    },
                    "chemotherapy": {
                        "regimen": "FLOT",
                        "cycles_neoadjuvant": 4,
                        "cycles_adjuvant": 4
                    }
                },
                "intent": "curative",
                "timeline": "6_months",
                "rationale": "High ADCI score supports aggressive multimodal therapy"
            }
        
        elif adci_score >= 0.6:
            # Moderate score - standard treatment
            return {
                "type": "standard_therapy",
                "components": {
                    "surgery": {
                        "type": "gastrectomy",
                        "approach": "open_or_laparoscopic",
                        "timing": "primary"
                    },
                    "chemotherapy": {
                        "regimen": "adjuvant_only",
                        "cycles": 6
                    }
                },
                "intent": "curative",
                "timeline": "4_months",
                "rationale": "Moderate ADCI score supports standard therapy approach"
            }
        
        elif adci_score >= 0.4:
            # Lower score - conservative treatment
            return {
                "type": "conservative_therapy",
                "components": {
                    "surgery": {
                        "type": "limited_resection",
                        "approach": "endoscopic_or_surgical",
                        "timing": "primary"
                    },
                    "chemotherapy": {
                        "regimen": "reduced_intensity",
                        "cycles": 4
                    }
                },
                "intent": "curative_with_qol_focus",
                "timeline": "3_months",
                "rationale": "Lower ADCI score suggests conservative approach"
            }
        
        else:
            # Low score - palliative care
            return {
                "type": "palliative_care",
                "components": {
                    "symptom_management": True,
                    "supportive_care": True,
                    "palliative_chemotherapy": {
                        "regimen": "single_agent",
                        "intensity": "low"
                    }
                },
                "intent": "palliative",
                "timeline": "ongoing",
                "rationale": "Low ADCI score indicates focus on quality of life"
            }
    
    async def _generate_alternatives(
        self,
        adci_score: float,
        parameters: Dict[str, Any],
        primary_recommendation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate alternative treatment options"""
        
        alternatives = []
        
        # Always include watch and wait as an option for early stage
        stage = parameters.get("tumor_stage", "")
        if "T1" in stage:
            alternatives.append({
                "type": "active_surveillance",
                "description": "Close monitoring with endoscopy",
                "rationale": "Appropriate for very early stage tumors",
                "confidence": 0.7
            })
        
        # Include immunotherapy if applicable
        biomarkers = parameters.get("biomarkers", {})
        if biomarkers.get("msi") == "high" or biomarkers.get("pdl1", 0) >= 1:
            alternatives.append({
                "type": "immunotherapy",
                "description": "PD-1/PD-L1 inhibitor therapy",
                "rationale": "MSI-H or PD-L1 positive tumor",
                "confidence": 0.8
            })
        
        # Include targeted therapy if HER2 positive
        if biomarkers.get("her2") == "positive":
            alternatives.append({
                "type": "targeted_therapy",
                "description": "HER2-targeted therapy (trastuzumab)",
                "rationale": "HER2 positive tumor",
                "confidence": 0.85
            })
        
        return alternatives
    
    async def _assess_risks(
        self,
        parameters: Dict[str, Any],
        recommendation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess treatment risks and contraindications"""
        
        risks = {
            "surgical_risk": "low",
            "chemotherapy_toxicity": "moderate",
            "contraindications": [],
            "risk_factors": []
        }
        
        # Assess surgical risk
        ps = parameters.get("performance_status", {})
        comorbidities = parameters.get("comorbidities", [])
        
        if ps.get("ecog", 0) >= 3:
            risks["surgical_risk"] = "high"
            risks["contraindications"].append("Poor performance status")
        
        if any("cardiovascular" in c.lower() for c in comorbidities):
            risks["surgical_risk"] = "moderate"
            risks["risk_factors"].append("Cardiovascular comorbidity")
        
        # Assess chemotherapy risks
        if any("renal" in c.lower() for c in comorbidities):
            risks["chemotherapy_toxicity"] = "high"
            risks["risk_factors"].append("Renal impairment")
        
        return risks
    
    async def _generate_evidence_summary(
        self,
        parameters: Dict[str, Any],
        recommendation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate evidence summary for the recommendation"""
        
        # Simulated evidence summary
        # In production, this would query the evidence database
        
        evidence = [
            {
                "source": "FLOT4 Trial",
                "evidence_level": "1A",
                "finding": "Perioperative FLOT improves overall survival",
                "relevance": "high",
                "strength": "strong"
            },
            {
                "source": "NCCN Guidelines 2024",
                "evidence_level": "1",
                "finding": "Multimodal therapy for resectable gastric cancer",
                "relevance": "high",
                "strength": "strong"
            }
        ]
        
        return evidence
    
    def _build_reasoning_chain(
        self,
        parameters: Dict[str, Any],
        adci_score: float,
        score_breakdown: Dict[str, float],
        confidence_metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Build reasoning chain for decision"""
        
        reasoning = [
            {
                "step": 1,
                "description": "Clinical parameter assessment",
                "details": f"Evaluated {len(parameters)} clinical parameters",
                "impact": "foundational"
            },
            {
                "step": 2,
                "description": "ADCI score calculation",
                "details": f"Calculated ADCI score: {adci_score:.3f}",
                "impact": "primary"
            },
            {
                "step": 3,
                "description": "Confidence assessment",
                "details": f"Overall confidence: {confidence_metrics['overall_confidence']:.3f}",
                "impact": "qualifying"
            },
            {
                "step": 4,
                "description": "Recommendation generation",
                "details": "Generated treatment recommendation based on ADCI score",
                "impact": "outcome"
            }
        ]
        
        return reasoning
    
    async def _generate_monitoring_recommendations(
        self,
        recommendation: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate monitoring recommendations"""
        
        monitoring = {
            "imaging": {
                "modality": "CT chest/abdomen/pelvis",
                "frequency": "every_3_months",
                "duration": "2_years"
            },
            "laboratory": {
                "tests": ["CBC", "CMP", "tumor_markers"],
                "frequency": "monthly_during_treatment"
            },
            "clinical_assessment": {
                "frequency": "every_visit",
                "focus": ["performance_status", "toxicity", "symptoms"]
            },
            "quality_of_life": {
                "instruments": ["EORTC_QLQ_C30", "EORTC_QLQ_STO22"],
                "frequency": "every_cycle"
            }
        }
        
        return monitoring
    
    def _generate_warnings(
        self,
        parameters: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate clinical warnings"""
        
        warnings = []
        
        if risk_assessment.get("surgical_risk") == "high":
            warnings.append("High surgical risk - consider thorough preoperative evaluation")
        
        if risk_assessment.get("chemotherapy_toxicity") == "high":
            warnings.append("High chemotherapy toxicity risk - consider dose modifications")
        
        if len(parameters.get("comorbidities", [])) > 3:
            warnings.append("Multiple comorbidities present - multidisciplinary evaluation recommended")
        
        return warnings
    
    async def get_parameter_schema(self) -> Dict[str, Any]:
        """Get parameter schema for the engine"""
        
        schema = {
            "tumor_stage": {
                "type": "string",
                "description": "TNM staging (e.g., T2N1M0)",
                "required": True,
                "validation": "TNM_format"
            },
            "histology": {
                "type": "string",
                "description": "Histological type",
                "required": True,
                "options": ["intestinal", "diffuse", "mixed", "signet_ring", "mucinous"]
            },
            "biomarkers": {
                "type": "object",
                "description": "Biomarker profile",
                "required": False,
                "properties": {
                    "her2": {"type": "string", "options": ["positive", "negative", "unknown"]},
                    "msi": {"type": "string", "options": ["high", "stable", "unknown"]},
                    "pdl1": {"type": "number", "range": [0, 100]}
                }
            },
            "performance_status": {
                "type": "object",
                "description": "Performance status assessment",
                "required": True,
                "properties": {
                    "ecog": {"type": "integer", "range": [0, 4]},
                    "karnofsky": {"type": "integer", "range": [0, 100]}
                }
            },
            "comorbidities": {
                "type": "array",
                "description": "List of comorbidities",
                "required": False,
                "items": {"type": "string"}
            },
            "patient_preferences": {
                "type": "object",
                "description": "Patient treatment preferences",
                "required": False,
                "properties": {
                    "treatment_intensity": {"type": "string", "options": ["aggressive", "moderate", "conservative"]},
                    "qol_priority": {"type": "number", "range": [1, 10]}
                }
            }
        }
        
        return schema
    
    def get_required_fields(self) -> List[str]:
        """Get list of required fields"""
        return ["tumor_stage", "histology", "performance_status"]
    
    def get_optional_fields(self) -> List[str]:
        """Get list of optional fields"""
        return ["biomarkers", "comorbidities", "patient_preferences"]
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules for parameters"""
        return {
            "tumor_stage": {
                "pattern": r"^T[1-4][a-c]?N[0-3][a-c]?M[0-1][a-c]?$",
                "message": "Must be valid TNM format (e.g., T2N1M0)"
            },
            "performance_status.ecog": {
                "range": [0, 4],
                "message": "ECOG score must be 0-4"
            },
            "performance_status.karnofsky": {
                "range": [0, 100],
                "message": "Karnofsky score must be 0-100"
            }
        }
    
    def _validate_parameters(self, parameters: Dict[str, Any]):
        """Validate input parameters"""
        required_fields = self.get_required_fields()
        
        for field in required_fields:
            if field not in parameters:
                raise ValueError(f"Required field missing: {field}")
        
        # Additional validation logic can be added here
        pass
