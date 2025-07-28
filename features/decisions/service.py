"""
Decision Engines Feature Module
Centralized decision support functionality
"""

import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from core.config.settings import get_feature_config
from core.models.base import BaseEntity, ConfidenceLevel, DecisionStatus
from core.services.base import BaseService, CacheService
from core.utils.helpers import HashUtils


# Schemas
class DecisionRequest(BaseModel):
    """Decision analysis request"""
    
    engine_type: str = Field(..., description="Decision engine type")
    patient_data: Dict[str, Any] = Field(..., description="Patient clinical data")
    tumor_data: Dict[str, Any] = Field(..., description="Tumor characteristics")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    class Config:
        schema_extra = {
            "example": {
                "engine_type": "adci",
                "patient_data": {
                    "age": 65,
                    "performance_status": 1,
                    "comorbidities": ["hypertension"]
                },
                "tumor_data": {
                    "stage": "T3N1M0",
                    "location": "antrum",
                    "histology": "adenocarcinoma"
                }
            }
        }


class DecisionResponse(BaseModel):
    """Decision analysis response"""
    
    decision_id: str
    engine_type: str
    status: DecisionStatus
    recommendation: Dict[str, Any]
    confidence_score: float
    confidence_level: ConfidenceLevel
    reasoning: List[str]
    evidence: List[Dict[str, Any]]
    warnings: List[str]
    created_at: datetime
    processing_time_ms: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "decision_id": "decision_123",
                "engine_type": "adci",
                "status": "completed",
                "recommendation": {
                    "treatment": "neoadjuvant_chemotherapy",
                    "urgency": "standard"
                },
                "confidence_score": 0.85,
                "confidence_level": "high",
                "reasoning": [
                    "T3N1M0 staging suggests locally advanced disease",
                    "Patient age and performance status support treatment"
                ],
                "evidence": [
                    {"source": "clinical_guidelines", "strength": "strong"}
                ],
                "warnings": [],
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


# Models
class Decision(BaseEntity):
    """Decision analysis record"""
    
    engine_type: str
    patient_data: Dict[str, Any]
    tumor_data: Dict[str, Any]
    context: Dict[str, Any]
    status: DecisionStatus = DecisionStatus.PENDING
    recommendation: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    confidence_level: Optional[ConfidenceLevel] = None
    reasoning: List[str] = []
    evidence: List[Dict[str, Any]] = []
    warnings: List[str] = []
    processing_time_ms: Optional[int] = None
    user_id: Optional[str] = None


# Base Decision Engine
class BaseDecisionEngine(ABC):
    """Base class for all decision engines"""
    
    def __init__(self, engine_type: str):
        self.engine_type = engine_type
        self.config = get_feature_config("decisions")
    
    @abstractmethod
    async def analyze(
        self,
        patient_data: Dict[str, Any],
        tumor_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform decision analysis"""
        pass
    
    def validate_input(self, patient_data: Dict[str, Any], tumor_data: Dict[str, Any]) -> List[str]:
        """Validate input data"""
        errors = []
        
        # Basic validation
        if not patient_data.get("age"):
            errors.append("Patient age is required")
        
        if not tumor_data.get("stage"):
            errors.append("Tumor stage is required")
        
        return errors
    
    def calculate_confidence(self, factors: Dict[str, float]) -> float:
        """Calculate overall confidence score"""
        if not factors:
            return 0.5
        
        weights = {
            "data_completeness": 0.3,
            "evidence_strength": 0.4,
            "guideline_support": 0.3
        }
        
        weighted_sum = sum(
            factors.get(factor, 0.5) * weight
            for factor, weight in weights.items()
        )
        
        return min(max(weighted_sum, 0.0), 1.0)


# ADCI Decision Engine
class ADCIEngine(BaseDecisionEngine):
    """Adaptive Decision Confidence Index Engine"""
    
    def __init__(self):
        super().__init__("adci")
    
    async def analyze(
        self,
        patient_data: Dict[str, Any],
        tumor_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform ADCI analysis"""
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Extract key parameters
        age = patient_data.get("age", 65)
        ps = patient_data.get("performance_status", 1)
        stage = tumor_data.get("stage", "T2N0M0")
        location = tumor_data.get("location", "antrum")
        
        # Decision logic based on clinical guidelines
        recommendation = self._determine_treatment(age, ps, stage, location)
        reasoning = self._generate_reasoning(age, ps, stage, location, recommendation)
        
        # Calculate confidence
        confidence_factors = {
            "data_completeness": self._assess_data_completeness(patient_data, tumor_data),
            "evidence_strength": self._assess_evidence_strength(stage),
            "guideline_support": self._assess_guideline_support(recommendation)
        }
        
        confidence_score = self.calculate_confidence(confidence_factors)
        
        return {
            "recommendation": recommendation,
            "confidence_score": confidence_score,
            "confidence_level": ConfidenceLevel.from_score(confidence_score),
            "reasoning": reasoning,
            "evidence": [
                {
                    "source": "NCCN Guidelines",
                    "strength": "strong",
                    "description": "National Comprehensive Cancer Network Guidelines for Gastric Cancer"
                },
                {
                    "source": "ESMO Guidelines", 
                    "strength": "strong",
                    "description": "European Society for Medical Oncology Guidelines"
                }
            ],
            "confidence_factors": confidence_factors
        }
    
    def _determine_treatment(self, age: int, ps: int, stage: str, location: str) -> Dict[str, Any]:
        """Determine treatment recommendation"""
        
        # Early stage (T1)
        if stage.startswith("T1"):
            if "N0" in stage:
                return {
                    "primary_treatment": "endoscopic_resection",
                    "alternative": "surgical_resection",
                    "urgency": "elective"
                }
            else:
                return {
                    "primary_treatment": "surgical_resection",
                    "alternative": "multimodal_therapy",
                    "urgency": "standard"
                }
        
        # Locally advanced (T2-T4, N+)
        elif any(x in stage for x in ["T2", "T3", "T4"]) or "N" in stage:
            if age < 75 and ps <= 2:
                return {
                    "primary_treatment": "multimodal_therapy",
                    "sequence": "neoadjuvant_surgery_adjuvant",
                    "urgency": "standard"
                }
            else:
                return {
                    "primary_treatment": "palliative_care",
                    "alternative": "limited_surgery",
                    "urgency": "standard"
                }
        
        # Default
        return {
            "primary_treatment": "multidisciplinary_evaluation",
            "urgency": "standard"
        }
    
    def _generate_reasoning(self, age: int, ps: int, stage: str, location: str, recommendation: Dict[str, Any]) -> List[str]:
        """Generate clinical reasoning"""
        
        reasoning = []
        
        reasoning.append(f"Patient age {age} years with performance status {ps}")
        reasoning.append(f"Tumor staging {stage} indicates {self._stage_description(stage)}")
        reasoning.append(f"Primary tumor location: {location}")
        
        if recommendation["primary_treatment"] == "multimodal_therapy":
            reasoning.append("Multimodal therapy recommended for locally advanced disease")
            reasoning.append("Neoadjuvant approach may improve resectability")
        
        if age >= 75:
            reasoning.append("Advanced age considered in treatment selection")
        
        if ps > 2:
            reasoning.append("Performance status limits treatment options")
        
        return reasoning
    
    def _stage_description(self, stage: str) -> str:
        """Get stage description"""
        if "T1" in stage and "N0" in stage:
            return "early-stage disease"
        elif "T2" in stage or "T3" in stage:
            return "locally advanced disease"
        elif "T4" in stage:
            return "advanced local disease"
        elif "M1" in stage:
            return "metastatic disease"
        else:
            return "intermediate-stage disease"
    
    def _assess_data_completeness(self, patient_data: Dict[str, Any], tumor_data: Dict[str, Any]) -> float:
        """Assess completeness of input data"""
        
        required_fields = ["age", "performance_status"]
        patient_completeness = sum(1 for field in required_fields if patient_data.get(field)) / len(required_fields)
        
        required_tumor_fields = ["stage", "location", "histology"]
        tumor_completeness = sum(1 for field in required_tumor_fields if tumor_data.get(field)) / len(required_tumor_fields)
        
        return (patient_completeness + tumor_completeness) / 2
    
    def _assess_evidence_strength(self, stage: str) -> float:
        """Assess strength of evidence for this case"""
        
        # Strong evidence for common stages
        if any(x in stage for x in ["T1N0", "T2N0", "T3N1"]):
            return 0.9
        elif any(x in stage for x in ["T4", "N2", "N3"]):
            return 0.7
        else:
            return 0.6
    
    def _assess_guideline_support(self, recommendation: Dict[str, Any]) -> float:
        """Assess guideline support for recommendation"""
        
        treatment = recommendation.get("primary_treatment")
        
        if treatment in ["surgical_resection", "multimodal_therapy"]:
            return 0.9
        elif treatment in ["endoscopic_resection", "palliative_care"]:
            return 0.8
        else:
            return 0.6


# Gastrectomy Engine
class GastrectomyEngine(BaseDecisionEngine):
    """Gastrectomy surgical decision engine"""
    
    def __init__(self):
        super().__init__("gastrectomy")
    
    async def analyze(
        self,
        patient_data: Dict[str, Any],
        tumor_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform gastrectomy analysis"""
        
        await asyncio.sleep(0.1)
        
        # Extract parameters
        age = patient_data.get("age", 65)
        bmi = patient_data.get("bmi", 24)
        asa_score = patient_data.get("asa_score", 2)
        
        tumor_location = tumor_data.get("location", "antrum")
        tumor_size = tumor_data.get("size_cm", 3.0)
        
        # Determine surgical approach
        approach = self._determine_surgical_approach(tumor_location, tumor_size, age, bmi)
        reasoning = self._generate_surgical_reasoning(approach, tumor_location, tumor_size, age)
        
        confidence_score = self._calculate_surgical_confidence(age, bmi, asa_score, tumor_size)
        
        return {
            "recommendation": approach,
            "confidence_score": confidence_score,
            "confidence_level": ConfidenceLevel.from_score(confidence_score),
            "reasoning": reasoning,
            "evidence": [
                {
                    "source": "Surgical Guidelines",
                    "strength": "strong",
                    "description": "International guidelines for gastric surgery"
                }
            ]
        }
    
    def _determine_surgical_approach(self, location: str, size: float, age: int, bmi: float) -> Dict[str, Any]:
        """Determine surgical approach"""
        
        # Location-based decisions
        if location in ["antrum", "pylorus"]:
            if size < 4.0 and age < 75:
                return {
                    "procedure": "distal_gastrectomy",
                    "approach": "laparoscopic",
                    "lymphadenectomy": "D2"
                }
            else:
                return {
                    "procedure": "distal_gastrectomy", 
                    "approach": "open",
                    "lymphadenectomy": "D2"
                }
        
        elif location in ["fundus", "cardia"]:
            return {
                "procedure": "proximal_gastrectomy",
                "approach": "laparoscopic" if age < 70 and bmi < 30 else "open",
                "lymphadenectomy": "D2"
            }
        
        else:  # body or multiple locations
            return {
                "procedure": "total_gastrectomy",
                "approach": "open",
                "lymphadenectomy": "D2"
            }
    
    def _generate_surgical_reasoning(self, approach: Dict[str, Any], location: str, size: float, age: int) -> List[str]:
        """Generate surgical reasoning"""
        
        reasoning = []
        
        reasoning.append(f"Tumor location ({location}) determines surgical approach")
        reasoning.append(f"Tumor size {size}cm considered in procedure selection")
        
        if approach["approach"] == "laparoscopic":
            reasoning.append("Laparoscopic approach preferred for reduced morbidity")
        else:
            reasoning.append("Open approach recommended for optimal exposure")
        
        reasoning.append(f"D2 lymphadenectomy recommended for oncological adequacy")
        
        return reasoning
    
    def _calculate_surgical_confidence(self, age: int, bmi: float, asa_score: int, tumor_size: float) -> float:
        """Calculate confidence in surgical recommendation"""
        
        confidence = 0.8  # Base confidence
        
        # Age factor
        if age < 65:
            confidence += 0.1
        elif age > 75:
            confidence -= 0.2
        
        # BMI factor
        if bmi > 30:
            confidence -= 0.1
        
        # ASA score factor
        if asa_score > 3:
            confidence -= 0.2
        
        # Tumor size factor
        if tumor_size > 5.0:
            confidence -= 0.1
        
        return min(max(confidence, 0.0), 1.0)
    
    def validate_input(self, patient_data: Dict[str, Any], tumor_data: Dict[str, Any]) -> List[str]:
        """Validate input data for gastrectomy analysis"""
        errors = []
        
        # Basic validation for gastrectomy
        if not patient_data.get("age"):
            errors.append("Patient age is required")
        
        if not tumor_data.get("location"):
            errors.append("Tumor location is required for surgical planning")
        
        return errors


# FLOT Engine
class FLOTEngine(BaseDecisionEngine):
    """FLOT (Fluorouracil, Leucovorin, Oxaliplatin, Docetaxel) Protocol Engine"""
    
    def __init__(self):
        super().__init__("flot")
        self.engine_version = "1.8.0"
        self.evidence_base = "FLOT4-AIO Trial, ESMO Guidelines 2023"
        
        # Standard FLOT dosing (per cycle)
        self.standard_dosing = {
            "fluorouracil": "2600 mg/m2 IV continuous infusion 24h",
            "leucovorin": "200 mg/m2 IV over 2h",
            "oxaliplatin": "85 mg/m2 IV over 2h",
            "docetaxel": "50 mg/m2 IV over 1h"
        }
    
    async def analyze(
        self,
        patient_data: Dict[str, Any],
        tumor_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform FLOT protocol analysis"""
        
        await asyncio.sleep(0.1)
        
        # Extract parameters
        age = patient_data.get("age", 70)
        ecog_score = patient_data.get("performance_status", 2)
        comorbidities = patient_data.get("comorbidities", [])
        
        tumor_stage = tumor_data.get("stage", "T2N0M0")
        histology = tumor_data.get("histology", "adenocarcinoma")
        
        # Assess FLOT eligibility
        eligibility_score = self._assess_flot_eligibility(age, ecog_score, tumor_stage, comorbidities)
        
        # Generate recommendation
        recommendation = self._generate_flot_recommendation(eligibility_score, age, ecog_score, tumor_stage)
        reasoning = self._generate_flot_reasoning(eligibility_score, age, ecog_score, tumor_stage, recommendation)
        
        # Calculate confidence
        confidence_factors = {
            "data_completeness": self._assess_data_completeness(patient_data, tumor_data),
            "evidence_strength": self._assess_flot_evidence_strength(tumor_stage, histology),
            "guideline_support": self._assess_guideline_support(recommendation)
        }
        
        confidence_score = self.calculate_confidence(confidence_factors)
        
        return {
            "recommendation": recommendation,
            "confidence_score": confidence_score,
            "confidence_level": ConfidenceLevel.from_score(confidence_score),
            "reasoning": reasoning,
            "evidence": [
                {
                    "source": "FLOT4-AIO Trial",
                    "strength": "strong",
                    "description": "Phase III trial demonstrating superiority of FLOT over ECF/ECX"
                },
                {
                    "source": "ESMO Guidelines 2023",
                    "strength": "strong",
                    "description": "European Society for Medical Oncology Clinical Practice Guidelines"
                }
            ],
            "confidence_factors": confidence_factors,
            "eligibility_score": eligibility_score
        }
    
    def _assess_flot_eligibility(self, age: int, ecog_score: int, tumor_stage: str, comorbidities: List[str]) -> float:
        """Assess FLOT protocol eligibility"""
        
        eligibility = 1.0
        
        # Stage assessment
        if any(x in tumor_stage for x in ["T3", "T4", "N1", "N2", "N3"]):
            eligibility += 0.2  # Strong indication for locally advanced
        elif "M1" in tumor_stage:
            eligibility -= 0.6  # Metastatic disease
        elif "T1N0" in tumor_stage:
            eligibility -= 0.4  # Early stage
        
        # Age factor
        if age >= 75:
            eligibility -= 0.3
        elif age >= 70:
            eligibility -= 0.1
        
        # Performance status
        if ecog_score >= 3:
            eligibility -= 0.8  # Poor PS
        elif ecog_score == 2:
            eligibility -= 0.3
        elif ecog_score == 1:
            eligibility -= 0.05
        
        # Comorbidities
        high_risk_conditions = ["severe_heart_failure", "severe_copd", "cirrhosis", "active_infection"]
        if any(condition in comorbidities for condition in high_risk_conditions):
            eligibility -= 0.4
        
        moderate_risk_conditions = ["diabetes", "hypertension", "mild_copd", "chronic_kidney_disease"]
        moderate_count = sum(1 for condition in comorbidities if condition in moderate_risk_conditions)
        eligibility -= moderate_count * 0.1
        
        return max(min(eligibility, 1.0), 0.0)
    
    def _generate_flot_recommendation(self, eligibility_score: float, age: int, ecog_score: int, tumor_stage: str) -> Dict[str, Any]:
        """Generate FLOT protocol recommendation"""
        
        if eligibility_score >= 0.8:
            status = "strongly_recommended"
            rationale = "Excellent candidate for FLOT protocol"
            cycles_preop = 4
            cycles_postop = 4
        elif eligibility_score >= 0.6:
            status = "recommended"
            rationale = "Good candidate for FLOT protocol"
            cycles_preop = 4
            cycles_postop = 4
        elif eligibility_score >= 0.4:
            status = "consider_with_caution"
            rationale = "Borderline candidate - consider dose modifications"
            cycles_preop = 3
            cycles_postop = 3
        else:
            status = "not_recommended"
            rationale = "Poor candidate - consider alternative approaches"
            cycles_preop = 0
            cycles_postop = 0
        
        # Determine treatment intent
        if "M1" in tumor_stage:
            treatment_intent = "palliative"
            cycles_preop = 0
            cycles_postop = 6
        elif eligibility_score >= 0.7:
            treatment_intent = "perioperative"
        else:
            treatment_intent = "adjuvant_only"
            cycles_preop = 0
            cycles_postop = 6
        
        return {
            "status": status,
            "rationale": rationale,
            "treatment_intent": treatment_intent,
            "cycles_preoperative": cycles_preop,
            "cycles_postoperative": cycles_postop,
            "cycle_frequency": "every_2_weeks",
            "total_duration_weeks": (cycles_preop + cycles_postop) * 2,
            "dosing": self.standard_dosing,
            "monitoring_required": self._get_monitoring_requirements(eligibility_score, age),
            "contraindications": self._assess_contraindications(age, ecog_score, tumor_stage)
        }
    
    def _generate_flot_reasoning(self, eligibility_score: float, age: int, ecog_score: int, tumor_stage: str, recommendation: Dict[str, Any]) -> List[str]:
        """Generate FLOT reasoning"""
        
        reasoning = []
        
        reasoning.append(f"Patient age {age} years with ECOG performance status {ecog_score}")
        reasoning.append(f"Tumor staging {tumor_stage} assessed for FLOT eligibility")
        reasoning.append(f"FLOT eligibility score: {eligibility_score:.2f}")
        
        if recommendation["status"] == "strongly_recommended":
            reasoning.append("Strong indication for perioperative FLOT protocol")
        elif recommendation["status"] == "recommended":
            reasoning.append("FLOT protocol recommended with standard monitoring")
        elif recommendation["status"] == "consider_with_caution":
            reasoning.append("FLOT may be considered with dose modifications and enhanced monitoring")
        else:
            reasoning.append("FLOT not recommended - consider alternative treatment approaches")
        
        if "M1" in tumor_stage:
            reasoning.append("Metastatic disease limits treatment to palliative intent")
        
        if age >= 75:
            reasoning.append("Advanced age increases toxicity risk - enhanced monitoring required")
        
        return reasoning
    
    def _assess_flot_evidence_strength(self, tumor_stage: str, histology: str) -> float:
        """Assess evidence strength for FLOT in this case"""
        
        # Strong evidence for locally advanced adenocarcinoma
        if any(x in tumor_stage for x in ["T3", "T4", "N1", "N2"]) and "adenocarcinoma" in histology.lower():
            return 0.95
        elif any(x in tumor_stage for x in ["T2N1", "T2N2"]):
            return 0.85
        elif "M1" in tumor_stage:
            return 0.6  # Limited evidence for metastatic
        else:
            return 0.7  # Moderate evidence
    
    def _get_monitoring_requirements(self, eligibility_score: float, age: int) -> List[str]:
        """Get monitoring requirements for FLOT"""
        
        requirements = [
            "Complete blood count before each cycle",
            "Comprehensive metabolic panel before each cycle",
            "Performance status assessment each visit",
            "Neuropathy assessment using CTCAE grading"
        ]
        
        if eligibility_score < 0.6 or age >= 70:
            requirements.extend([
                "Enhanced toxicity monitoring",
                "Dose modification guidelines",
                "Cardiology consultation if indicated"
            ])
        
        if age >= 75:
            requirements.append("Geriatric assessment and nutritional support")
        
        return requirements
    
    def _assess_contraindications(self, age: int, ecog_score: int, tumor_stage: str) -> List[str]:
        """Assess contraindications and warnings"""
        
        warnings = []
        
        if ecog_score >= 3:
            warnings.append("ECOG PS ≥3 is contraindication to FLOT")
        
        if age >= 80:
            warnings.append("Age ≥80 years - very high toxicity risk")
        
        if "M1" in tumor_stage:
            warnings.append("Metastatic disease - palliative intent only")
        
        return warnings


# Decision Service
class DecisionService(BaseService):
    """Main decision service coordinating all engines"""
    
    def __init__(self):
        super().__init__()
        self.cache = CacheService()
        self.config = get_feature_config("decisions")
        self.engines = {
            "adci": ADCIEngine(),
            "gastrectomy": GastrectomyEngine(),
            "flot": FLOTEngine()
        }
        self.decisions: Dict[str, Decision] = {}  # In-memory store for MVP
    
    async def create_decision(
        self,
        request: DecisionRequest,
        user_id: Optional[str] = None
    ) -> DecisionResponse:
        """Create new decision analysis"""
        
        start_time = asyncio.get_event_loop().time()
        
        # Create decision record
        decision = Decision(
            engine_type=request.engine_type,
            patient_data=request.patient_data,
            tumor_data=request.tumor_data,
            context=request.context or {},
            user_id=user_id
        )
        
        decision_id = str(decision.id)
        self.decisions[decision_id] = decision
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_result = await self.cache.get(cache_key)
            
            if cached_result:
                self.logger.info(f"Cache hit for decision {decision_id}")
                result = cached_result
            else:
                # Get engine
                engine = self.engines.get(request.engine_type)
                if not engine:
                    raise ValueError(f"Unknown engine type: {request.engine_type}")
                
                # Validate input
                errors = engine.validate_input(request.patient_data, request.tumor_data)
                if errors:
                    decision.status = DecisionStatus.FAILED
                    decision.warnings = errors
                    raise ValueError(f"Validation errors: {'; '.join(errors)}")
                
                # Process decision
                decision.status = DecisionStatus.PROCESSING
                
                result = await engine.analyze(
                    request.patient_data,
                    request.tumor_data,
                    request.context
                )
                
                # Cache result
                await self.cache.set(cache_key, result, ttl=self.config.get("cache_ttl", 3600))
            
            # Update decision record
            decision.status = DecisionStatus.COMPLETED
            decision.recommendation = result["recommendation"]
            decision.confidence_score = result["confidence_score"]
            decision.confidence_level = result["confidence_level"]
            decision.reasoning = result["reasoning"]
            decision.evidence = result.get("evidence", [])
            decision.processing_time_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            
            self.logger.info(f"Decision {decision_id} completed in {decision.processing_time_ms}ms")
            
            return self._create_response(decision)
            
        except Exception as e:
            decision.status = DecisionStatus.FAILED
            decision.warnings = [str(e)]
            self.logger.error(f"Decision {decision_id} failed: {e}")
            raise
    
    async def get_decision(self, decision_id: str) -> Optional[DecisionResponse]:
        """Get decision by ID"""
        
        decision = self.decisions.get(decision_id)
        if not decision:
            return None
        
        return self._create_response(decision)
    
    async def list_decisions(
        self,
        user_id: Optional[str] = None,
        engine_type: Optional[str] = None,
        status: Optional[DecisionStatus] = None
    ) -> List[DecisionResponse]:
        """List decisions with filters"""
        
        decisions = list(self.decisions.values())
        
        # Apply filters
        if user_id:
            decisions = [d for d in decisions if d.user_id == user_id]
        
        if engine_type:
            decisions = [d for d in decisions if d.engine_type == engine_type]
        
        if status:
            decisions = [d for d in decisions if d.status == status]
        
        # Sort by creation time (newest first)
        decisions.sort(key=lambda d: d.created_at, reverse=True)
        
        return [self._create_response(d) for d in decisions]
    
    def _generate_cache_key(self, request: DecisionRequest) -> str:
        """Generate cache key for request"""
        
        key_data = {
            "engine_type": request.engine_type,
            "patient_data": request.patient_data,
            "tumor_data": request.tumor_data
        }
        
        return HashUtils.generate_cache_key(key_data)
    
    def _create_response(self, decision: Decision) -> DecisionResponse:
        """Create response from decision"""
        
        return DecisionResponse(
            decision_id=str(decision.id),
            engine_type=decision.engine_type,
            status=decision.status,
            recommendation=decision.recommendation or {},
            confidence_score=decision.confidence_score or 0.0,
            confidence_level=decision.confidence_level or ConfidenceLevel.VERY_LOW,
            reasoning=decision.reasoning,
            evidence=decision.evidence,
            warnings=decision.warnings,
            created_at=decision.created_at,
            processing_time_ms=decision.processing_time_ms
        )
