"""
FLOT (5-FU, Leucovorin, Oxaliplatin, Docetaxel) Protocol Analyzer
for Gastric Cancer Treatment Decision Support.

This module provides comprehensive analysis of FLOT protocol implementation
including eligibility assessment, dosing calculations, toxicity monitoring,
and outcome prediction using the ADCI framework.
"""

import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field

from core.services.logger import get_logger
from features.decisions.base_decision_engine import BaseDecisionEngine
from services.event_logger.service import event_logger, EventCategory, EventSeverity

logger = get_logger(__name__)


class FLOTEligibility(Enum):
    """FLOT protocol eligibility status."""
    ELIGIBLE = "eligible"
    NOT_ELIGIBLE = "not_eligible"
    RELATIVE_CONTRAINDICATION = "relative_contraindication"
    REQUIRES_MODIFICATION = "requires_modification"


class FLOTPhase(Enum):
    """FLOT treatment phases."""
    PREOPERATIVE = "preoperative"
    POSTOPERATIVE = "postoperative"
    BOTH = "both"


class PatientCharacteristics(BaseModel):
    """Patient characteristics for FLOT analysis."""
    age: int
    performance_status: int  # ECOG 0-4
    creatinine_clearance: float  # ml/min
    bilirubin: float  # mg/dL
    cardiac_function: str  # normal, mild_impairment, moderate_impairment, severe_impairment
    hearing_function: str  # normal, mild_loss, moderate_loss, severe_loss
    neuropathy_grade: int  # 0-4
    previous_chemotherapy: bool = False
    allergies: List[str] = []


class TumorCharacteristics(BaseModel):
    """Tumor characteristics for FLOT analysis."""
    histology: str  # adenocarcinoma, signet_ring, mixed
    grade: str  # well_differentiated, moderately_differentiated, poorly_differentiated
    clinical_stage: str  # T1-4, N0-3, M0-1
    her2_status: str  # positive, negative, unknown
    msi_status: str  # high, stable, unknown
    resectable: bool = True
    locally_advanced: bool = False


class FLOTDoseReduction(BaseModel):
    """FLOT dose reduction recommendations."""
    reduction_percentage: int  # 0, 25, 50, 75
    modified_drugs: List[str]  # which drugs to reduce
    reason: str
    monitoring_requirements: List[str]


class FLOTAnalysisResult(BaseModel):
    """Comprehensive FLOT analysis result."""
    eligibility: FLOTEligibility
    eligibility_score: float  # 0-100
    eligibility_reasons: List[str]
    recommended_phase: FLOTPhase
    dose_modifications: Optional[FLOTDoseReduction] = None
    predicted_benefit: float  # 0-100
    toxicity_risk: float  # 0-100
    monitoring_plan: List[str]
    contraindications: List[str]
    alternatives: List[str]
    confidence_level: float  # ADCI confidence score
    analysis_date: datetime.datetime = Field(default_factory=datetime.datetime.now)


class FLOTAnalyzer(BaseDecisionEngine):
    """FLOT Protocol Decision Support Analyzer."""
    
    def __init__(self):
        super().__init__()
        self.protocol_name = "FLOT"
        self.version = "2.0"
        
        # FLOT eligibility criteria weights
        self.eligibility_weights = {
            "age": 0.15,
            "performance_status": 0.20,
            "organ_function": 0.25,
            "tumor_stage": 0.20,
            "resectability": 0.20
        }
        
        # Dose modification thresholds
        self.dose_thresholds = {
            "creatinine_clearance": {"mild": 50, "moderate": 30, "severe": 15},
            "bilirubin": {"mild": 1.5, "moderate": 3.0, "severe": 5.0},
            "neuropathy": {"mild": 1, "moderate": 2, "severe": 3},
            "age": {"elderly": 70, "very_elderly": 80}
        }
    
    async def analyze_flot_eligibility(
        self, 
        patient: PatientCharacteristics, 
        tumor: TumorCharacteristics,
        treatment_intent: str = "curative"
    ) -> FLOTAnalysisResult:
        """
        Comprehensive FLOT protocol eligibility and optimization analysis.
        
        Args:
            patient: Patient characteristics
            tumor: Tumor characteristics  
            treatment_intent: curative, palliative, neoadjuvant
            
        Returns:
            FLOTAnalysisResult with comprehensive analysis
        """
        try:
            await event_logger.log_event(
                category=EventCategory.CLINICAL_DECISION,
                severity=EventSeverity.INFO,
                message="FLOT analysis initiated",
                metadata={
                    "patient_age": patient.age,
                    "tumor_stage": tumor.clinical_stage,
                    "treatment_intent": treatment_intent
                }
            )
            
            # Calculate eligibility components
            age_score = self._assess_age_eligibility(patient.age)
            performance_score = self._assess_performance_status(patient.performance_status)
            organ_function_score = self._assess_organ_function(patient)
            tumor_score = self._assess_tumor_suitability(tumor)
            resectability_score = self._assess_resectability(tumor)
            
            # Calculate weighted eligibility score
            eligibility_score = (
                age_score * self.eligibility_weights["age"] +
                performance_score * self.eligibility_weights["performance_status"] +
                organ_function_score * self.eligibility_weights["organ_function"] +
                tumor_score * self.eligibility_weights["tumor_stage"] +
                resectability_score * self.eligibility_weights["resectability"]
            ) * 100
            
            # Determine eligibility status
            eligibility = self._determine_eligibility_status(eligibility_score, patient, tumor)
            
            # Assess dose modifications
            dose_modifications = self._assess_dose_modifications(patient)
            
            # Calculate predicted benefit and toxicity risk
            predicted_benefit = self._calculate_predicted_benefit(patient, tumor, eligibility_score)
            toxicity_risk = self._calculate_toxicity_risk(patient, dose_modifications)
            
            # Generate recommendations
            monitoring_plan = self._generate_monitoring_plan(patient, dose_modifications)
            contraindications = self._identify_contraindications(patient, tumor)
            alternatives = self._suggest_alternatives(eligibility, contraindications)
            
            # Determine recommended treatment phase
            recommended_phase = self._determine_treatment_phase(tumor, treatment_intent)
            
            # Calculate ADCI confidence level
            confidence_level = await self._calculate_confidence_level(
                eligibility_score, predicted_benefit, toxicity_risk
            )
            
            # Generate eligibility reasons
            eligibility_reasons = self._generate_eligibility_reasons(
                age_score, performance_score, organ_function_score, 
                tumor_score, resectability_score
            )
            
            result = FLOTAnalysisResult(
                eligibility=eligibility,
                eligibility_score=eligibility_score,
                eligibility_reasons=eligibility_reasons,
                recommended_phase=recommended_phase,
                dose_modifications=dose_modifications,
                predicted_benefit=predicted_benefit,
                toxicity_risk=toxicity_risk,
                monitoring_plan=monitoring_plan,
                contraindications=contraindications,
                alternatives=alternatives,
                confidence_level=confidence_level
            )
            
            await event_logger.log_event(
                category=EventCategory.CLINICAL_DECISION,
                severity=EventSeverity.INFO,
                message="FLOT analysis completed",
                metadata={
                    "eligibility": eligibility.value,
                    "eligibility_score": eligibility_score,
                    "confidence_level": confidence_level
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"FLOT analysis error: {str(e)}")
            await event_logger.log_event(
                category=EventCategory.SYSTEM_ERROR,
                severity=EventSeverity.ERROR,
                message=f"FLOT analysis failed: {str(e)}",
                metadata={"error": str(e)}
            )
            raise
    
    def _assess_age_eligibility(self, age: int) -> float:
        """Assess age-based eligibility (0-1 score)."""
        if age < 18:
            return 0.0  # Pediatric - different protocols
        elif age <= 65:
            return 1.0  # Optimal age
        elif age <= 75:
            return 0.8  # Elderly but suitable
        elif age <= 80:
            return 0.6  # Very elderly - careful consideration
        else:
            return 0.3  # Very high risk
    
    def _assess_performance_status(self, ps: int) -> float:
        """Assess ECOG performance status eligibility."""
        ps_scores = {0: 1.0, 1: 0.9, 2: 0.5, 3: 0.2, 4: 0.0}
        return ps_scores.get(ps, 0.0)
    
    def _assess_organ_function(self, patient: PatientCharacteristics) -> float:
        """Assess organ function eligibility."""
        scores = []
        
        # Renal function
        if patient.creatinine_clearance >= 60:
            scores.append(1.0)
        elif patient.creatinine_clearance >= 30:
            scores.append(0.7)
        elif patient.creatinine_clearance >= 15:
            scores.append(0.4)
        else:
            scores.append(0.1)
        
        # Hepatic function  
        if patient.bilirubin <= 1.5:
            scores.append(1.0)
        elif patient.bilirubin <= 3.0:
            scores.append(0.6)
        elif patient.bilirubin <= 5.0:
            scores.append(0.3)
        else:
            scores.append(0.1)
        
        # Cardiac function
        cardiac_scores = {
            "normal": 1.0,
            "mild_impairment": 0.8,
            "moderate_impairment": 0.5,
            "severe_impairment": 0.2
        }
        scores.append(cardiac_scores.get(patient.cardiac_function, 0.5))
        
        return sum(scores) / len(scores)
    
    def _assess_tumor_suitability(self, tumor: TumorCharacteristics) -> float:
        """Assess tumor characteristics for FLOT suitability."""
        score = 1.0
        
        # Histology suitability
        if tumor.histology == "adenocarcinoma":
            score *= 1.0
        elif tumor.histology == "signet_ring":
            score *= 0.8  # May be less responsive
        else:
            score *= 0.6
        
        # Stage appropriateness
        if tumor.locally_advanced and tumor.resectable:
            score *= 1.0  # Primary indication
        elif not tumor.locally_advanced and tumor.resectable:
            score *= 0.7  # May benefit but not primary indication
        elif not tumor.resectable:
            score *= 0.5  # Palliative setting
        
        return score
    
    def _assess_resectability(self, tumor: TumorCharacteristics) -> float:
        """Assess tumor resectability for FLOT protocol."""
        if tumor.resectable:
            return 1.0
        elif tumor.locally_advanced:
            return 0.6  # May become resectable
        else:
            return 0.2  # Palliative intent
    
    def _determine_eligibility_status(
        self, 
        score: float, 
        patient: PatientCharacteristics, 
        tumor: TumorCharacteristics
    ) -> FLOTEligibility:
        """Determine overall eligibility status."""
        if score >= 80:
            return FLOTEligibility.ELIGIBLE
        elif score >= 60:
            return FLOTEligibility.REQUIRES_MODIFICATION
        elif score >= 40:
            return FLOTEligibility.RELATIVE_CONTRAINDICATION
        else:
            return FLOTEligibility.NOT_ELIGIBLE
    
    def _assess_dose_modifications(self, patient: PatientCharacteristics) -> Optional[FLOTDoseReduction]:
        """Assess need for dose modifications."""
        modifications = []
        reduction_percentage = 0
        reasons = []
        
        # Age-based modifications
        if patient.age >= 75:
            reduction_percentage = max(reduction_percentage, 25)
            modifications.extend(["docetaxel", "oxaliplatin"])
            reasons.append("Advanced age (≥75 years)")
        
        # Renal function modifications
        if patient.creatinine_clearance < 50:
            reduction_percentage = max(reduction_percentage, 25)
            modifications.extend(["oxaliplatin"])
            reasons.append("Impaired renal function")
        
        # Hepatic function modifications
        if patient.bilirubin > 1.5:
            reduction_percentage = max(reduction_percentage, 25)
            modifications.extend(["docetaxel"])
            reasons.append("Elevated bilirubin")
        
        # Neuropathy modifications
        if patient.neuropathy_grade >= 2:
            reduction_percentage = max(reduction_percentage, 50)
            modifications.extend(["oxaliplatin"])
            reasons.append("Pre-existing neuropathy")
        
        if reduction_percentage > 0:
            monitoring_requirements = self._generate_modification_monitoring(modifications)
            
            return FLOTDoseReduction(
                reduction_percentage=reduction_percentage,
                modified_drugs=list(set(modifications)),
                reason="; ".join(reasons),
                monitoring_requirements=monitoring_requirements
            )
        
        return None
    
    def _calculate_predicted_benefit(
        self, 
        patient: PatientCharacteristics, 
        tumor: TumorCharacteristics,
        eligibility_score: float
    ) -> float:
        """Calculate predicted treatment benefit."""
        base_benefit = 75.0  # Base FLOT benefit from literature
        
        # Adjust for patient factors
        if patient.age <= 65:
            age_factor = 1.0
        elif patient.age <= 75:
            age_factor = 0.9
        else:
            age_factor = 0.7
        
        # Adjust for tumor factors
        if tumor.locally_advanced and tumor.resectable:
            tumor_factor = 1.0
        elif tumor.resectable:
            tumor_factor = 0.8
        else:
            tumor_factor = 0.5
        
        # Adjust for performance status
        ps_factor = 1.0 - (patient.performance_status * 0.1)
        
        predicted_benefit = base_benefit * age_factor * tumor_factor * ps_factor * (eligibility_score / 100)
        
        return min(predicted_benefit, 95.0)  # Cap at 95%
    
    def _calculate_toxicity_risk(
        self, 
        patient: PatientCharacteristics, 
        dose_modifications: Optional[FLOTDoseReduction]
    ) -> float:
        """Calculate predicted toxicity risk."""
        base_risk = 30.0  # Base FLOT toxicity risk
        
        # Age-related risk increase
        if patient.age >= 75:
            base_risk += 20
        elif patient.age >= 65:
            base_risk += 10
        
        # Performance status risk
        base_risk += patient.performance_status * 10
        
        # Organ function risk
        if patient.creatinine_clearance < 50:
            base_risk += 15
        if patient.bilirubin > 1.5:
            base_risk += 15
        
        # Dose modification benefit
        if dose_modifications:
            reduction_benefit = dose_modifications.reduction_percentage * 0.3
            base_risk -= reduction_benefit
        
        return min(max(base_risk, 5.0), 90.0)  # Keep between 5-90%
    
    def _generate_monitoring_plan(
        self, 
        patient: PatientCharacteristics, 
        dose_modifications: Optional[FLOTDoseReduction]
    ) -> List[str]:
        """Generate monitoring plan."""
        monitoring = [
            "Complete blood count before each cycle",
            "Comprehensive metabolic panel before each cycle",
            "Performance status assessment",
            "Toxicity evaluation using CTCAE criteria"
        ]
        
        if patient.age >= 65:
            monitoring.append("Geriatric assessment")
        
        if patient.creatinine_clearance < 60:
            monitoring.append("Weekly renal function monitoring")
        
        if dose_modifications and "oxaliplatin" in dose_modifications.modified_drugs:
            monitoring.append("Neuropathy assessment before each cycle")
        
        if patient.cardiac_function != "normal":
            monitoring.append("Cardiac function monitoring")
        
        return monitoring
    
    def _identify_contraindications(
        self, 
        patient: PatientCharacteristics, 
        tumor: TumorCharacteristics
    ) -> List[str]:
        """Identify absolute contraindications."""
        contraindications = []
        
        if patient.performance_status >= 3:
            contraindications.append("Poor performance status (ECOG ≥3)")
        
        if patient.creatinine_clearance < 30:
            contraindications.append("Severe renal impairment")
        
        if patient.bilirubin > 3.0:
            contraindications.append("Severe hepatic impairment")
        
        if patient.cardiac_function == "severe_impairment":
            contraindications.append("Severe cardiac dysfunction")
        
        if "docetaxel" in patient.allergies:
            contraindications.append("Docetaxel allergy")
        
        if "oxaliplatin" in patient.allergies:
            contraindications.append("Oxaliplatin allergy")
        
        return contraindications
    
    def _suggest_alternatives(
        self, 
        eligibility: FLOTEligibility, 
        contraindications: List[str]
    ) -> List[str]:
        """Suggest alternative treatment options."""
        alternatives = []
        
        if eligibility in [FLOTEligibility.NOT_ELIGIBLE, FLOTEligibility.RELATIVE_CONTRAINDICATION]:
            alternatives.extend([
                "ECF/ECX (Epirubicin, Cisplatin, 5-FU/Capecitabine)",
                "MAGIC protocol",
                "Single-agent chemotherapy",
                "Best supportive care"
            ])
        
        if eligibility == FLOTEligibility.REQUIRES_MODIFICATION:
            alternatives.extend([
                "Modified FLOT with dose reductions",
                "Sequential rather than combination therapy",
                "Two-drug combinations (e.g., oxaliplatin + 5-FU)"
            ])
        
        if any("allergy" in c.lower() for c in contraindications):
            alternatives.extend([
                "FLOT modification with alternative agents",
                "Carboplatin-based regimens",
                "Paclitaxel-based regimens"
            ])
        
        return alternatives
    
    def _determine_treatment_phase(
        self, 
        tumor: TumorCharacteristics, 
        treatment_intent: str
    ) -> FLOTPhase:
        """Determine recommended FLOT treatment phase."""
        if treatment_intent == "neoadjuvant":
            return FLOTPhase.PREOPERATIVE
        elif treatment_intent == "adjuvant":
            return FLOTPhase.POSTOPERATIVE
        elif tumor.locally_advanced and tumor.resectable:
            return FLOTPhase.BOTH  # Perioperative
        else:
            return FLOTPhase.PREOPERATIVE
    
    async def _calculate_confidence_level(
        self, 
        eligibility_score: float, 
        predicted_benefit: float, 
        toxicity_risk: float
    ) -> float:
        """Calculate ADCI confidence level for the recommendation."""
        # Base confidence on eligibility score
        base_confidence = eligibility_score
        
        # Adjust for benefit-risk ratio
        benefit_risk_ratio = predicted_benefit / max(toxicity_risk, 1.0)
        if benefit_risk_ratio > 2.0:
            confidence_adjustment = 10
        elif benefit_risk_ratio > 1.5:
            confidence_adjustment = 5
        elif benefit_risk_ratio > 1.0:
            confidence_adjustment = 0
        else:
            confidence_adjustment = -10
        
        confidence = min(base_confidence + confidence_adjustment, 95.0)
        return max(confidence, 5.0)  # Minimum 5% confidence
    
    def _generate_eligibility_reasons(
        self, 
        age_score: float, 
        performance_score: float, 
        organ_function_score: float,
        tumor_score: float, 
        resectability_score: float
    ) -> List[str]:
        """Generate human-readable eligibility reasons."""
        reasons = []
        
        if age_score >= 0.8:
            reasons.append("Appropriate age for intensive chemotherapy")
        elif age_score >= 0.6:
            reasons.append("Advanced age requires careful monitoring")
        elif age_score < 0.6:
            reasons.append("Advanced age limits treatment intensity")
        
        if performance_score >= 0.8:
            reasons.append("Good performance status")
        elif performance_score >= 0.5:
            reasons.append("Fair performance status")
        else:
            reasons.append("Poor performance status limits treatment options")
        
        if organ_function_score >= 0.8:
            reasons.append("Adequate organ function")
        elif organ_function_score >= 0.6:
            reasons.append("Mild organ dysfunction - dose modifications may be needed")
        else:
            reasons.append("Significant organ dysfunction limits treatment")
        
        if tumor_score >= 0.8:
            reasons.append("Tumor characteristics favor FLOT protocol")
        elif tumor_score >= 0.6:
            reasons.append("Tumor characteristics moderately suitable for FLOT")
        else:
            reasons.append("Tumor characteristics less favorable for FLOT")
        
        if resectability_score >= 0.8:
            reasons.append("Resectable disease - optimal for perioperative therapy")
        else:
            reasons.append("Resectability concerns affect treatment planning")
        
        return reasons
    
    def _generate_modification_monitoring(self, modified_drugs: List[str]) -> List[str]:
        """Generate monitoring requirements for dose modifications."""
        monitoring = []
        
        if "oxaliplatin" in modified_drugs:
            monitoring.extend([
                "Neuropathy assessment before each cycle",
                "Audiology if hearing concerns"
            ])
        
        if "docetaxel" in modified_drugs:
            monitoring.extend([
                "Liver function tests",
                "Fluid retention assessment"
            ])
        
        return monitoring


# Global analyzer instance
flot_analyzer = FLOTAnalyzer()
