"""
Gastrectomy Protocol Decision Engine
Surgical approach and technique recommendations for gastric cancer
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from decimal import Decimal
import structlog

logger = structlog.get_logger(__name__)

class GastrectomyEngine:
    """
    Gastrectomy Protocol Engine for surgical approach recommendations
    
    Provides evidence-based surgical recommendations including:
    - Surgical approach (open, laparoscopic, robotic)
    - Extent of resection (subtotal, total)
    - Lymph node dissection (D1, D1+, D2)
    - Reconstruction method
    """
    
    def __init__(self):
        self.engine_name = "gastrectomy"
        self.engine_version = "1.2.0"
        self.evidence_base = "JGCA 2024, IGCA Guidelines"
        
    async def process_decision(
        self,
        patient_id: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        include_alternatives: bool = True,
        confidence_threshold: float = 0.75
    ) -> Dict[str, Any]:
        """Process gastrectomy decision for gastric cancer surgery"""
        
        start_time = datetime.now()
        
        try:
            # Validate input parameters
            self._validate_parameters(parameters)
            
            # Analyze surgical factors
            surgical_score, surgical_breakdown = await self._analyze_surgical_factors(parameters)
            
            # Generate primary surgical recommendation
            primary_recommendation = await self._generate_surgical_recommendation(
                surgical_score, parameters, context
            )
            
            # Calculate confidence metrics
            confidence_metrics = await self._calculate_confidence(
                parameters, primary_recommendation, context
            )
            
            # Generate alternative surgical options if requested
            alternatives = []
            if include_alternatives:
                alternatives = await self._generate_surgical_alternatives(
                    surgical_score, parameters, confidence_threshold
                )
            
            # Generate evidence summary
            evidence_summary = await self._generate_evidence_summary(
                primary_recommendation, parameters
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "engine_name": self.engine_name,
                "engine_version": self.engine_version,
                "patient_id": patient_id,
                "recommendation": primary_recommendation,
                "confidence_score": float(confidence_metrics["overall_confidence"]),
                "confidence_level": self._get_confidence_level(confidence_metrics["overall_confidence"]),
                "surgical_score": float(surgical_score),
                "surgical_breakdown": surgical_breakdown,
                "alternatives": alternatives,
                "evidence_summary": evidence_summary,
                "risk_assessment": await self._assess_surgical_risks(parameters),
                "monitoring_recommendations": await self._generate_monitoring_plan(primary_recommendation),
                "warnings": await self._check_warnings(parameters),
                "data_completeness": self._calculate_data_completeness(parameters),
                "processing_time_ms": processing_time,
                "confidence_metrics": confidence_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Error in gastrectomy decision processing", 
                        patient_id=patient_id, error=str(e))
            raise

    async def _analyze_surgical_factors(self, parameters: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Analyze surgical factors for gastrectomy recommendation"""
        
        factors = {}
        
        # Tumor location scoring
        tumor_location = parameters.get("tumor_location", "unknown")
        factors["tumor_location"] = self._score_tumor_location(tumor_location)
        
        # Tumor size and depth
        tumor_size = parameters.get("tumor_size_cm", 0)
        factors["tumor_size"] = self._score_tumor_size(tumor_size)
        
        # T stage scoring
        t_stage = parameters.get("tumor_stage", "").split("N")[0] if "N" in parameters.get("tumor_stage", "") else parameters.get("tumor_stage", "")
        factors["t_stage"] = self._score_t_stage(t_stage)
        
        # N stage scoring
        n_stage = "N" + parameters.get("tumor_stage", "").split("N")[1].split("M")[0] if "N" in parameters.get("tumor_stage", "") else "N0"
        factors["n_stage"] = self._score_n_stage(n_stage)
        
        # Patient factors
        age = parameters.get("age", 70)
        factors["age"] = self._score_age_for_surgery(age)
        
        ecog_score = parameters.get("ecog_score", 2)
        factors["performance_status"] = self._score_performance_status(ecog_score)
        
        # Comorbidities
        comorbidities = parameters.get("comorbidities", [])
        factors["comorbidity_burden"] = self._score_comorbidities(comorbidities)
        
        # Previous abdominal surgery
        prior_surgery = parameters.get("prior_abdominal_surgery", False)
        factors["surgical_history"] = 0.7 if prior_surgery else 1.0
        
        # Calculate weighted score
        weights = {
            "tumor_location": 0.20,
            "tumor_size": 0.15,
            "t_stage": 0.20,
            "n_stage": 0.15,
            "age": 0.10,
            "performance_status": 0.10,
            "comorbidity_burden": 0.08,
            "surgical_history": 0.02
        }
        
        surgical_score = sum(factors[factor] * weights[factor] for factor in factors)
        
        return surgical_score, factors

    def _score_tumor_location(self, location: str) -> float:
        """Score based on tumor location in stomach"""
        location_scores = {
            "antrum": 0.9,      # Easier surgical access
            "pylorus": 0.85,    # Good for subtotal gastrectomy
            "body": 0.7,        # May require total gastrectomy
            "fundus": 0.6,      # Requires total gastrectomy
            "cardia": 0.5,      # Complex, requires extended resection
            "linitis_plastica": 0.3,  # Extensive disease
            "multifocal": 0.4,  # Multiple locations
            "gej": 0.5,         # Gastroesophageal junction
            "unknown": 0.5
        }
        return location_scores.get(location.lower(), 0.5)

    def _score_tumor_size(self, size_cm: float) -> float:
        """Score based on tumor size"""
        if size_cm <= 2:
            return 0.9
        elif size_cm <= 4:
            return 0.8
        elif size_cm <= 6:
            return 0.7
        elif size_cm <= 8:
            return 0.6
        elif size_cm <= 10:
            return 0.5
        else:
            return 0.4

    def _score_t_stage(self, t_stage: str) -> float:
        """Score based on T stage"""
        t_scores = {
            "T1": 0.95,   # Mucosa/submucosa
            "T1a": 0.95,  # Mucosa
            "T1b": 0.9,   # Submucosa
            "T2": 0.8,    # Muscularis propria
            "T3": 0.6,    # Subserosa
            "T4": 0.4,    # Serosa/adjacent organs
            "T4a": 0.45,  # Serosa
            "T4b": 0.3,   # Adjacent organs
            "TX": 0.5
        }
        return t_scores.get(t_stage.upper(), 0.5)

    def _score_n_stage(self, n_stage: str) -> float:
        """Score based on N stage"""
        n_scores = {
            "N0": 0.9,    # No lymph nodes
            "N1": 0.8,    # 1-2 lymph nodes
            "N2": 0.6,    # 3-6 lymph nodes
            "N3": 0.4,    # 7+ lymph nodes
            "N3a": 0.45,  # 7-15 lymph nodes
            "N3b": 0.35,  # 16+ lymph nodes
            "NX": 0.5
        }
        return n_scores.get(n_stage.upper(), 0.5)

    def _score_age_for_surgery(self, age: int) -> float:
        """Score based on age for surgical risk"""
        if age < 50:
            return 0.95
        elif age < 65:
            return 0.9
        elif age < 75:
            return 0.8
        elif age < 80:
            return 0.7
        else:
            return 0.6

    def _score_performance_status(self, ecog: int) -> float:
        """Score based on ECOG performance status"""
        ecog_scores = {
            0: 0.95,  # Fully active
            1: 0.85,  # Restricted strenuous activity
            2: 0.65,  # Ambulatory, self-care
            3: 0.45,  # Limited self-care
            4: 0.25   # Completely disabled
        }
        return ecog_scores.get(ecog, 0.5)

    def _score_comorbidities(self, comorbidities: List[str]) -> float:
        """Score based on comorbidity burden"""
        if not comorbidities:
            return 1.0
        
        high_risk_conditions = {
            "heart_failure", "coronary_artery_disease", "severe_copd",
            "cirrhosis", "chronic_kidney_disease", "diabetes_uncontrolled"
        }
        
        moderate_risk_conditions = {
            "diabetes", "hypertension", "mild_copd", "previous_mi"
        }
        
        high_risk_count = sum(1 for c in comorbidities if c.lower() in high_risk_conditions)
        moderate_risk_count = sum(1 for c in comorbidities if c.lower() in moderate_risk_conditions)
        
        # Calculate score based on comorbidity burden
        score = 1.0 - (high_risk_count * 0.2) - (moderate_risk_count * 0.1)
        return max(score, 0.3)  # Minimum score of 0.3

    async def _generate_surgical_recommendation(
        self, 
        surgical_score: float, 
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate primary surgical recommendation"""
        
        tumor_location = parameters.get("tumor_location", "").lower()
        tumor_stage = parameters.get("tumor_stage", "")
        tumor_size = parameters.get("tumor_size_cm", 0)
        ecog_score = parameters.get("ecog_score", 2)
        
        # Determine surgical approach
        if surgical_score >= 0.8 and ecog_score <= 1:
            approach = "laparoscopic"
            approach_rationale = "High surgical score and good performance status favor minimally invasive approach"
        elif surgical_score >= 0.6:
            approach = "open"
            approach_rationale = "Moderate surgical complexity recommends open approach for optimal oncologic outcomes"
        else:
            approach = "open"
            approach_rationale = "Complex case requires open approach for adequate resection"
        
        # Determine extent of resection
        if tumor_location in ["antrum", "pylorus"] and "T1" in tumor_stage:
            extent = "subtotal_gastrectomy"
            extent_rationale = "Distal location and early stage allow organ-sparing resection"
        elif tumor_location in ["fundus", "cardia", "body"] or tumor_size > 4:
            extent = "total_gastrectomy"
            extent_rationale = "Tumor location/size requires total gastrectomy for adequate margins"
        else:
            extent = "subtotal_gastrectomy"
            extent_rationale = "Subtotal resection appropriate based on tumor characteristics"
        
        # Determine lymphadenectomy extent
        if "N0" in tumor_stage and "T1" in tumor_stage:
            lymphadenectomy = "D1+"
            lymph_rationale = "Early stage disease allows limited lymphadenectomy"
        elif surgical_score >= 0.7:
            lymphadenectomy = "D2"
            lymph_rationale = "Standard D2 lymphadenectomy for optimal oncologic outcomes"
        else:
            lymphadenectomy = "D1+"
            lymph_rationale = "Modified lymphadenectomy considering patient factors"
        
        # Determine reconstruction
        if extent == "subtotal_gastrectomy":
            reconstruction = "Billroth_II"
            recon_rationale = "Standard reconstruction after subtotal gastrectomy"
        else:
            reconstruction = "Roux_en_Y"
            recon_rationale = "Roux-en-Y reconstruction after total gastrectomy"
        
        return {
            "surgical_approach": approach,
            "approach_rationale": approach_rationale,
            "extent_of_resection": extent,
            "extent_rationale": extent_rationale,
            "lymphadenectomy": lymphadenectomy,
            "lymphadenectomy_rationale": lymph_rationale,
            "reconstruction": reconstruction,
            "reconstruction_rationale": recon_rationale,
            "estimated_duration_hours": self._estimate_duration(approach, extent),
            "expected_recovery_days": self._estimate_recovery(approach, extent, parameters)
        }

    def _estimate_duration(self, approach: str, extent: str) -> float:
        """Estimate surgical duration"""
        base_times = {
            ("open", "subtotal_gastrectomy"): 3.5,
            ("open", "total_gastrectomy"): 4.5,
            ("laparoscopic", "subtotal_gastrectomy"): 4.0,
            ("laparoscopic", "total_gastrectomy"): 5.5
        }
        return base_times.get((approach, extent), 4.0)

    def _estimate_recovery(self, approach: str, extent: str, parameters: Dict[str, Any]) -> int:
        """Estimate recovery time"""
        base_recovery = {
            ("open", "subtotal_gastrectomy"): 8,
            ("open", "total_gastrectomy"): 10,
            ("laparoscopic", "subtotal_gastrectomy"): 6,
            ("laparoscopic", "total_gastrectomy"): 8
        }
        
        base_days = base_recovery.get((approach, extent), 8)
        
        # Adjust for patient factors
        age = parameters.get("age", 70)
        if age > 75:
            base_days += 2
        
        comorbidities = parameters.get("comorbidities", [])
        if len(comorbidities) > 2:
            base_days += 1
        
        return base_days

    async def _generate_surgical_alternatives(
        self, 
        surgical_score: float, 
        parameters: Dict[str, Any], 
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Generate alternative surgical options"""
        
        alternatives = []
        
        # Alternative approaches
        tumor_location = parameters.get("tumor_location", "").lower()
        tumor_stage = parameters.get("tumor_stage", "")
        
        if surgical_score >= 0.7:
            alternatives.append({
                "approach": "robotic_gastrectomy",
                "confidence": min(surgical_score * 0.9, 0.95),
                "rationale": "Robotic approach for enhanced precision and recovery",
                "advantages": ["Enhanced dexterity", "Better visualization", "Faster recovery"],
                "considerations": ["Higher cost", "Learning curve", "Equipment availability"]
            })
        
        if "T1" in tumor_stage and tumor_location in ["antrum", "pylorus"]:
            alternatives.append({
                "approach": "endoscopic_resection",
                "confidence": min(surgical_score * 0.85, 0.9),
                "rationale": "Endoscopic resection for early-stage tumors",
                "advantages": ["Minimal invasive", "Organ preservation", "Faster recovery"],
                "considerations": ["Limited to early stage", "Risk of incomplete resection"]
            })
        
        # Conservative options for high-risk patients
        if surgical_score < 0.5:
            alternatives.append({
                "approach": "palliative_bypass",
                "confidence": 0.6,
                "rationale": "Palliative procedure for high-risk patients",
                "advantages": ["Lower operative risk", "Symptom relief"],
                "considerations": ["Non-curative", "Limited survival benefit"]
            })
        
        return [alt for alt in alternatives if alt["confidence"] >= threshold]

    async def _calculate_confidence(
        self,
        parameters: Dict[str, Any],
        recommendation: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """Calculate confidence metrics for surgical recommendation"""
        
        # Data completeness factor
        required_fields = ["tumor_location", "tumor_stage", "age", "ecog_score"]
        available_fields = sum(1 for field in required_fields if parameters.get(field) is not None)
        data_completeness = available_fields / len(required_fields)
        
        # Evidence strength factor
        evidence_strength = 0.85  # Based on JGCA guidelines
        
        # Clinical consistency factor
        clinical_consistency = self._assess_clinical_consistency(parameters, recommendation)
        
        # Patient suitability factor
        patient_suitability = self._assess_patient_suitability(parameters)
        
        # Calculate overall confidence
        confidence_factors = {
            "data_completeness": data_completeness,
            "evidence_strength": evidence_strength,
            "clinical_consistency": clinical_consistency,
            "patient_suitability": patient_suitability
        }
        
        # Weighted combination
        weights = {
            "data_completeness": 0.25,
            "evidence_strength": 0.35,
            "clinical_consistency": 0.25,
            "patient_suitability": 0.15
        }
        
        overall_confidence = sum(
            confidence_factors[factor] * weights[factor] 
            for factor in confidence_factors
        )
        
        confidence_factors["overall_confidence"] = overall_confidence
        
        return confidence_factors

    def _assess_clinical_consistency(self, parameters: Dict[str, Any], recommendation: Dict[str, Any]) -> float:
        """Assess clinical consistency of recommendation"""
        consistency_score = 0.8  # Base consistency
        
        # Check for logical consistency
        tumor_stage = parameters.get("tumor_stage", "")
        approach = recommendation.get("surgical_approach", "")
        extent = recommendation.get("extent_of_resection", "")
        
        # Early stage with extensive surgery should reduce confidence
        if "T1" in tumor_stage and extent == "total_gastrectomy":
            consistency_score -= 0.1
        
        # Advanced stage with minimal surgery should reduce confidence
        if ("T3" in tumor_stage or "T4" in tumor_stage) and extent == "subtotal_gastrectomy":
            consistency_score -= 0.2
        
        return max(consistency_score, 0.3)

    def _assess_patient_suitability(self, parameters: Dict[str, Any]) -> float:
        """Assess patient suitability for recommended surgery"""
        age = parameters.get("age", 70)
        ecog_score = parameters.get("ecog_score", 2)
        comorbidities = parameters.get("comorbidities", [])
        
        suitability = 1.0
        
        # Age factor
        if age > 80:
            suitability -= 0.2
        elif age > 75:
            suitability -= 0.1
        
        # Performance status factor
        if ecog_score >= 3:
            suitability -= 0.3
        elif ecog_score == 2:
            suitability -= 0.1
        
        # Comorbidity factor
        if len(comorbidities) > 3:
            suitability -= 0.2
        elif len(comorbidities) > 1:
            suitability -= 0.1
        
        return max(suitability, 0.3)

    async def _assess_surgical_risks(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Assess surgical risks"""
        age = parameters.get("age", 70)
        ecog_score = parameters.get("ecog_score", 2)
        comorbidities = parameters.get("comorbidities", [])
        
        # Calculate risk scores
        operative_risk = self._calculate_operative_risk(age, ecog_score, comorbidities)
        morbidity_risk = self._calculate_morbidity_risk(age, comorbidities)
        mortality_risk = self._calculate_mortality_risk(age, ecog_score, comorbidities)
        
        return {
            "operative_risk": operative_risk,
            "morbidity_risk": morbidity_risk,
            "mortality_risk": mortality_risk,
            "anastomotic_leak_risk": self._calculate_anastomotic_risk(parameters),
            "recovery_complications": self._assess_recovery_risks(parameters)
        }

    def _calculate_operative_risk(self, age: int, ecog: int, comorbidities: List[str]) -> str:
        """Calculate operative risk level"""
        risk_score = 0
        
        if age > 75:
            risk_score += 2
        elif age > 65:
            risk_score += 1
        
        if ecog >= 2:
            risk_score += 2
        elif ecog == 1:
            risk_score += 1
        
        if len(comorbidities) > 2:
            risk_score += 2
        elif len(comorbidities) > 0:
            risk_score += 1
        
        if risk_score <= 1:
            return "low"
        elif risk_score <= 3:
            return "moderate"
        else:
            return "high"

    def _calculate_morbidity_risk(self, age: int, comorbidities: List[str]) -> str:
        """Calculate morbidity risk"""
        if age > 80 or len(comorbidities) > 3:
            return "high"
        elif age > 70 or len(comorbidities) > 1:
            return "moderate"
        else:
            return "low"

    def _calculate_mortality_risk(self, age: int, ecog: int, comorbidities: List[str]) -> str:
        """Calculate mortality risk"""
        if age > 85 or ecog >= 3 or len(comorbidities) > 4:
            return "high"
        elif age > 75 or ecog == 2 or len(comorbidities) > 2:
            return "moderate"
        else:
            return "low"

    def _calculate_anastomotic_risk(self, parameters: Dict[str, Any]) -> str:
        """Calculate anastomotic leak risk"""
        age = parameters.get("age", 70)
        diabetes = "diabetes" in parameters.get("comorbidities", [])
        smoking = "smoking" in parameters.get("comorbidities", [])
        
        risk_factors = sum([age > 75, diabetes, smoking])
        
        if risk_factors >= 2:
            return "high"
        elif risk_factors == 1:
            return "moderate"
        else:
            return "low"

    def _assess_recovery_risks(self, parameters: Dict[str, Any]) -> List[str]:
        """Assess recovery-related risks"""
        risks = []
        
        age = parameters.get("age", 70)
        comorbidities = parameters.get("comorbidities", [])
        
        if age > 75:
            risks.append("Delayed mobilization")
        
        if "diabetes" in comorbidities:
            risks.append("Wound healing complications")
        
        if "copd" in comorbidities or "smoking" in comorbidities:
            risks.append("Pulmonary complications")
        
        if "heart_failure" in comorbidities:
            risks.append("Cardiac complications")
        
        return risks

    async def _generate_monitoring_plan(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate post-operative monitoring plan"""
        approach = recommendation.get("surgical_approach", "open")
        extent = recommendation.get("extent_of_resection", "subtotal")
        
        return {
            "immediate_postop": {
                "vitals_frequency": "Every 15 minutes x 4 hours, then hourly",
                "drainage_monitoring": "Output and character every 4 hours",
                "pain_assessment": "Every 2 hours with PCA monitoring"
            },
            "first_24_hours": {
                "lab_monitoring": "CBC, CMP, lactate every 8 hours",
                "imaging": "CXR immediately post-op and PRN",
                "mobility": "HOB elevation, log rolling every 2 hours"
            },
            "first_week": {
                "anastomosis_assessment": "Upper GI study on POD 5-7 if total gastrectomy",
                "nutrition": "TPN initiation, gradual diet advancement",
                "complications": "Daily assessment for leak, bleeding, infection"
            },
            "follow_up": {
                "clinic_visits": "2 weeks, 6 weeks, 3 months, 6 months",
                "imaging_schedule": "CT every 6 months for 2 years",
                "lab_monitoring": "Vitamin B12, iron studies every 3 months",
                "nutrition_counseling": "Ongoing with registered dietitian"
            }
        }

    async def _generate_evidence_summary(
        self, 
        recommendation: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate evidence summary supporting the recommendation"""
        
        evidence = []
        
        approach = recommendation.get("surgical_approach", "")
        extent = recommendation.get("extent_of_resection", "")
        
        if approach == "laparoscopic":
            evidence.append({
                "evidence_id": "JGCA_2024_LAP",
                "level": "1",
                "description": "Laparoscopic gastrectomy shows equivalent oncologic outcomes with reduced morbidity",
                "citation": "Japanese Gastric Cancer Association Guidelines 2024",
                "strength": "strong",
                "applicability": "high"
            })
        
        if "D2" in recommendation.get("lymphadenectomy", ""):
            evidence.append({
                "evidence_id": "D2_META_2023",
                "level": "1",
                "description": "D2 lymphadenectomy improves long-term survival in advanced gastric cancer",
                "citation": "Meta-analysis of D1 vs D2 lymphadenectomy, Surgery 2023",
                "strength": "strong",
                "applicability": "high"
            })
        
        evidence.append({
            "evidence_id": "MULTIMODAL_2024",
            "level": "2",
            "description": "Enhanced recovery protocols reduce length of stay and complications",
            "citation": "Enhanced Recovery After Surgery Guidelines 2024",
            "strength": "moderate",
            "applicability": "high"
        })
        
        return evidence

    async def _check_warnings(self, parameters: Dict[str, Any]) -> List[str]:
        """Check for clinical warnings"""
        warnings = []
        
        age = parameters.get("age", 70)
        ecog_score = parameters.get("ecog_score", 2)
        comorbidities = parameters.get("comorbidities", [])
        
        if age > 85:
            warnings.append("Advanced age increases operative risk - consider multidisciplinary evaluation")
        
        if ecog_score >= 3:
            warnings.append("Poor performance status - consider non-operative management")
        
        if "cirrhosis" in comorbidities:
            warnings.append("Liver disease significantly increases operative risk")
        
        if "heart_failure" in comorbidities:
            warnings.append("Cardiac optimization required before surgery")
        
        tumor_stage = parameters.get("tumor_stage", "")
        if "M1" in tumor_stage:
            warnings.append("Metastatic disease - surgery for palliation only")
        
        return warnings

    def _validate_parameters(self, parameters: Dict[str, Any]):
        """Validate input parameters"""
        required_fields = ["tumor_stage", "age"]
        
        for field in required_fields:
            if field not in parameters:
                raise ValueError(f"Missing required parameter: {field}")
        
        # Validate age
        age = parameters.get("age")
        if not isinstance(age, (int, float)) or age < 0 or age > 120:
            raise ValueError("Age must be between 0 and 120")
        
        # Validate ECOG score
        ecog_score = parameters.get("ecog_score")
        if ecog_score is not None and ecog_score not in [0, 1, 2, 3, 4]:
            raise ValueError("ECOG score must be 0, 1, 2, 3, or 4")

    def _get_confidence_level(self, confidence_score: float) -> str:
        """Convert confidence score to level"""
        if confidence_score >= 0.9:
            return "very_high"
        elif confidence_score >= 0.8:
            return "high"
        elif confidence_score >= 0.6:
            return "medium"
        else:
            return "low"

    def _calculate_data_completeness(self, parameters: Dict[str, Any]) -> float:
        """Calculate data completeness score"""
        important_fields = [
            "tumor_stage", "tumor_location", "tumor_size_cm", "age", 
            "ecog_score", "comorbidities", "prior_abdominal_surgery"
        ]
        
        available_fields = sum(1 for field in important_fields if parameters.get(field) is not None)
        return available_fields / len(important_fields)
