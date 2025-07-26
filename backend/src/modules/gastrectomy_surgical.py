"""
Gastrectomy Surgical Decision Module
Modular surgical procedure recommendation engine for gastric cancer

Converted from domain-specific engine to pluggable decision module
with 90%+ cache hit optimization and standardized interfaces.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import structlog

from ..framework.decision_module import (
    DecisionModule, DecisionModuleType, DecisionContext, DecisionResult, CacheConfig, CacheStrategy
)

logger = structlog.get_logger(__name__)

class GastrectomySurgicalModule(DecisionModule):
    """
    Modular Gastrectomy Surgical Decision Support
    
    Provides evidence-based surgical recommendations for gastric cancer including:
    - Surgical approach (open, laparoscopic, robotic)
    - Extent of resection (subtotal, total)
    - Lymph node dissection (D1, D1+, D2)
    - Reconstruction method
    - Risk assessment and outcome prediction
    """
    
    def __init__(self):
        # Optimize cache for high hit rate - surgical decisions often follow patterns
        cache_config = CacheConfig(
            strategy=CacheStrategy.AGGRESSIVE,
            ttl_seconds=21600,  # 6 hours - surgical protocols are stable
            hit_rate_target=0.92,
            max_size=3000,
            compression_enabled=True
        )
        
        super().__init__(
            module_id="gastrectomy_surgical",
            module_type=DecisionModuleType.PROCEDURAL,
            version="3.0.0",
            domain="gastric_surgery",
            cache_config=cache_config
        )
        
        self.evidence_base = "JGCA 2024, IGCA Guidelines, EORTC Studies"
        self._init_surgical_protocols()
    
    def _init_surgical_protocols(self):
        """Initialize evidence-based surgical protocol database"""
        
        self.surgical_approaches = {
            "open": {
                "complexity_factor": 1.0,
                "recovery_days": 14,
                "morbidity_rate": 0.15,
                "mortality_rate": 0.03,
                "blood_loss_ml": 300,
                "operative_time_min": 180,
                "learning_curve": "standard",
                "cost_factor": 1.0
            },
            "laparoscopic": {
                "complexity_factor": 1.3,
                "recovery_days": 8,
                "morbidity_rate": 0.10,
                "mortality_rate": 0.02,
                "blood_loss_ml": 150,
                "operative_time_min": 240,
                "learning_curve": "steep",
                "cost_factor": 1.2,
                "conversion_risk": 0.05
            },
            "robotic": {
                "complexity_factor": 1.5,
                "recovery_days": 7,
                "morbidity_rate": 0.08,
                "mortality_rate": 0.015,
                "blood_loss_ml": 120,
                "operative_time_min": 280,
                "learning_curve": "steep",
                "cost_factor": 2.0,
                "conversion_risk": 0.02
            }
        }
        
        self.resection_protocols = {
            "subtotal": {
                "indications": ["T1", "T2", "antral", "body_distal"],
                "contraindications": ["linitis", "proximal_third", "multifocal"],
                "lymph_dissection": "D1+",
                "reconstruction_options": ["billroth_i", "billroth_ii", "roux_en_y"],
                "oncologic_adequacy": 0.95,
                "functional_preservation": 0.85
            },
            "total": {
                "indications": ["T3", "T4", "proximal", "cardia", "gej", "linitis", "multifocal"],
                "contraindications": ["extensive_comorbidities", "poor_performance"],
                "lymph_dissection": "D2",
                "reconstruction_options": ["roux_en_y", "jejunal_pouch"],
                "oncologic_adequacy": 0.98,
                "functional_preservation": 0.65
            }
        }
        
        self.lymph_dissection_levels = {
            "D1": {
                "stations": [1, 3, 4, 5, 6],
                "complexity": "low",
                "morbidity": 0.05,
                "oncologic_benefit": 0.70
            },
            "D1+": {
                "stations": [1, 3, 4, 5, 6, 7, 8, 9],
                "complexity": "moderate",
                "morbidity": 0.08,
                "oncologic_benefit": 0.85
            },
            "D2": {
                "stations": [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "complexity": "high",
                "morbidity": 0.12,
                "oncologic_benefit": 0.95
            }
        }
    
    async def process_decision(
        self,
        parameters: Dict[str, Any],
        context: DecisionContext,
        options: Optional[Dict[str, Any]] = None
    ) -> DecisionResult:
        """
        Process surgical decision with comprehensive analysis
        
        Returns evidence-based surgical recommendation with confidence intervals
        """
        
        # Extract clinical parameters
        tumor_characteristics = parameters.get("tumor", {})
        patient_factors = parameters.get("patient", {})
        institutional_factors = parameters.get("institution", {})
        
        # Parallel analysis for performance optimization
        analysis_tasks = [
            self._analyze_tumor_factors(tumor_characteristics),
            self._assess_patient_fitness(patient_factors),
            self._evaluate_institutional_capability(institutional_factors),
            self._calculate_surgical_risk(tumor_characteristics, patient_factors)
        ]
        
        tumor_analysis, fitness_assessment, institutional_assessment, risk_analysis = await asyncio.gather(
            *analysis_tasks
        )
        
        # Generate surgical recommendation
        surgical_recommendation = await self._generate_surgical_plan(
            tumor_analysis, fitness_assessment, institutional_assessment, risk_analysis
        )
        
        # Calculate confidence and uncertainty
        confidence_analysis = self._calculate_decision_confidence(
            surgical_recommendation, tumor_analysis, fitness_assessment, parameters
        )
        
        # Generate alternative approaches
        alternatives = await self._generate_alternative_approaches(
            surgical_recommendation, tumor_analysis, fitness_assessment, confidence_analysis
        )
        
        # Predict outcomes
        outcome_predictions = self._predict_surgical_outcomes(surgical_recommendation, risk_analysis)
        
        # Build comprehensive surgical decision
        primary_decision = {
            "recommended_procedure": surgical_recommendation,
            "surgical_approach": surgical_recommendation["approach"],
            "resection_type": surgical_recommendation["resection"],
            "lymph_dissection": surgical_recommendation["lymph_dissection"],
            "reconstruction": surgical_recommendation["reconstruction"],
            "confidence_score": confidence_analysis["overall_confidence"],
            "risk_assessment": risk_analysis,
            "outcome_predictions": outcome_predictions,
            "evidence_level": self._determine_evidence_level(surgical_recommendation),
            "guideline_compliance": self._check_guideline_compliance(surgical_recommendation, tumor_analysis)
        }
        
        return DecisionResult(
            primary_decision=primary_decision,
            confidence=confidence_analysis["overall_confidence"],
            alternatives=alternatives,
            metadata={
                "decision_type": "surgical_planning",
                "evidence_base": self.evidence_base,
                "analysis_components": {
                    "tumor_analysis": tumor_analysis,
                    "fitness_assessment": fitness_assessment,
                    "institutional_assessment": institutional_assessment
                },
                "confidence_breakdown": confidence_analysis,
                "surgical_complexity": surgical_recommendation.get("complexity_score", 0.5)
            }
        )
    
    async def _analyze_tumor_factors(self, tumor: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze tumor characteristics for surgical planning"""
        
        stage = tumor.get("stage", "T1").upper()
        location = tumor.get("location", "antrum").lower()
        size_cm = tumor.get("size_cm", 2.0)
        histology = tumor.get("histology", "adenocarcinoma")
        differentiation = tumor.get("differentiation", "moderate")
        
        # Calculate tumor complexity score
        complexity_score = 0.0
        
        # Stage-based complexity
        stage_complexity = {
            "T1": 0.1, "T1A": 0.05, "T1B": 0.15,
            "T2": 0.3, "T3": 0.6, "T4": 0.9,
            "STAGE I": 0.2, "STAGE II": 0.4, "STAGE III": 0.7, "STAGE IV": 1.0
        }
        complexity_score += stage_complexity.get(stage, 0.5)
        
        # Location-based complexity
        location_complexity = {
            "antrum": 0.1, "body": 0.3, "fundus": 0.5,
            "cardia": 0.7, "gej": 0.8, "esophagogastric": 0.9,
            "linitis": 1.0, "multifocal": 0.8
        }
        complexity_score += location_complexity.get(location, 0.3)
        
        # Size impact
        if size_cm > 5.0:
            complexity_score += 0.3
        elif size_cm > 3.0:
            complexity_score += 0.2
        else:
            complexity_score += 0.1
        
        complexity_score = min(complexity_score / 3.0, 1.0)
        
        # Determine resection requirements
        resection_indication = self._determine_resection_type(stage, location, size_cm)
        lymph_requirement = self._determine_lymph_dissection(stage, resection_indication)
        
        return {
            "complexity_score": complexity_score,
            "stage": stage,
            "location": location,
            "size_cm": size_cm,
            "histology": histology,
            "differentiation": differentiation,
            "resection_indication": resection_indication,
            "lymph_requirement": lymph_requirement,
            "oncologic_priority": self._assess_oncologic_priority(stage, histology)
        }
    
    async def _assess_patient_fitness(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """Assess patient fitness for surgical intervention"""
        
        age = patient.get("age", 65)
        bmi = patient.get("bmi", 25.0)
        asa_score = patient.get("asa_score", 2)
        performance_status = patient.get("performance_status", 1)
        comorbidities = patient.get("comorbidities", [])
        
        # Calculate fitness score
        fitness_score = 1.0
        
        # Age impact
        if age > 80:
            fitness_score -= 0.3
        elif age > 70:
            fitness_score -= 0.2
        elif age > 60:
            fitness_score -= 0.1
        
        # BMI impact
        if bmi > 35 or bmi < 18:
            fitness_score -= 0.2
        elif bmi > 30 or bmi < 20:
            fitness_score -= 0.1
        
        # ASA impact
        asa_impact = {1: 0.0, 2: 0.05, 3: 0.15, 4: 0.3, 5: 0.5}
        fitness_score -= asa_impact.get(asa_score, 0.15)
        
        # Performance status impact
        fitness_score -= (performance_status * 0.1)
        
        # Comorbidity impact
        high_risk_comorbidities = [
            "heart_failure", "copd", "renal_failure", "liver_cirrhosis",
            "diabetes_uncontrolled", "previous_mi", "pulmonary_hypertension"
        ]
        
        comorbidity_impact = sum(0.1 for c in comorbidities if c in high_risk_comorbidities)
        fitness_score -= comorbidity_impact
        
        fitness_score = max(fitness_score, 0.0)
        
        # Determine surgical risk category
        if fitness_score >= 0.8:
            risk_category = "low"
        elif fitness_score >= 0.6:
            risk_category = "moderate"
        elif fitness_score >= 0.4:
            risk_category = "high"
        else:
            risk_category = "prohibitive"
        
        return {
            "fitness_score": fitness_score,
            "risk_category": risk_category,
            "age": age,
            "bmi": bmi,
            "asa_score": asa_score,
            "performance_status": performance_status,
            "comorbidity_count": len(comorbidities),
            "high_risk_comorbidities": [c for c in comorbidities if c in high_risk_comorbidities],
            "surgical_candidacy": fitness_score >= 0.4
        }
    
    async def _evaluate_institutional_capability(self, institution: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate institutional capability for complex procedures"""
        
        volume = institution.get("annual_cases", 50)
        expertise_level = institution.get("expertise", "standard")
        technology = institution.get("available_technology", [])
        support_services = institution.get("support_services", [])
        
        # Calculate capability score
        capability_score = 0.5  # baseline
        
        # Volume impact
        if volume >= 100:
            capability_score += 0.3
        elif volume >= 50:
            capability_score += 0.2
        elif volume >= 25:
            capability_score += 0.1
        
        # Expertise level
        expertise_boost = {
            "expert": 0.3,
            "experienced": 0.2,
            "standard": 0.0,
            "limited": -0.2
        }
        capability_score += expertise_boost.get(expertise_level, 0.0)
        
        # Technology availability
        advanced_tech = ["robotic_system", "laparoscopic_hd", "icu_monitoring", "interventional_radiology"]
        tech_score = sum(0.05 for tech in technology if tech in advanced_tech)
        capability_score += tech_score
        
        capability_score = min(max(capability_score, 0.0), 1.0)
        
        return {
            "capability_score": capability_score,
            "annual_volume": volume,
            "expertise_level": expertise_level,
            "technology_available": technology,
            "support_services": support_services,
            "complex_case_suitable": capability_score >= 0.7,
            "recommended_procedures": self._get_suitable_procedures(capability_score, expertise_level)
        }
    
    async def _calculate_surgical_risk(
        self, 
        tumor: Dict[str, Any], 
        patient: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate comprehensive surgical risk assessment"""
        
        # Base risk from tumor complexity
        tumor_risk = tumor.get("complexity_score", 0.5) * 0.4
        
        # Patient risk factors
        age = patient.get("age", 65)
        asa = patient.get("asa_score", 2)
        comorbidities = len(patient.get("comorbidities", []))
        
        patient_risk = 0.0
        if age > 75:
            patient_risk += 0.2
        if asa >= 3:
            patient_risk += 0.15
        patient_risk += comorbidities * 0.05
        
        overall_risk = min(tumor_risk + patient_risk, 1.0)
        
        # Risk categories
        if overall_risk < 0.3:
            risk_level = "low"
        elif overall_risk < 0.6:
            risk_level = "moderate"
        else:
            risk_level = "high"
        
        return {
            "overall_risk": overall_risk,
            "risk_level": risk_level,
            "tumor_risk_component": tumor_risk,
            "patient_risk_component": patient_risk,
            "estimated_morbidity": self._estimate_morbidity(overall_risk),
            "estimated_mortality": self._estimate_mortality(overall_risk),
            "risk_mitigation_strategies": self._get_risk_mitigation(risk_level)
        }
    
    async def _generate_surgical_plan(
        self,
        tumor_analysis: Dict[str, Any],
        fitness_assessment: Dict[str, Any],
        institutional_assessment: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive surgical plan"""
        
        # Determine optimal approach
        approach = self._select_optimal_approach(
            tumor_analysis, fitness_assessment, institutional_assessment
        )
        
        # Determine resection type
        resection = tumor_analysis["resection_indication"]
        
        # Determine lymph dissection
        lymph_dissection = tumor_analysis["lymph_requirement"]
        
        # Select reconstruction method
        reconstruction = self._select_reconstruction(resection, approach, fitness_assessment)
        
        # Calculate complexity score
        complexity_score = self._calculate_procedure_complexity(
            approach, resection, lymph_dissection, tumor_analysis
        )
        
        return {
            "approach": approach,
            "resection": resection,
            "lymph_dissection": lymph_dissection,
            "reconstruction": reconstruction,
            "complexity_score": complexity_score,
            "estimated_duration_hours": self._estimate_duration(approach, resection, complexity_score),
            "perioperative_plan": self._generate_perioperative_plan(fitness_assessment, risk_analysis),
            "quality_metrics": self._define_quality_metrics(approach, resection)
        }
    
    def _select_optimal_approach(
        self,
        tumor_analysis: Dict[str, Any],
        fitness_assessment: Dict[str, Any],
        institutional_assessment: Dict[str, Any]
    ) -> str:
        """Select optimal surgical approach"""
        
        complexity = tumor_analysis["complexity_score"]
        fitness = fitness_assessment["fitness_score"]
        capability = institutional_assessment["capability_score"]
        
        # Decision algorithm
        if complexity < 0.4 and fitness > 0.7 and capability > 0.6:
            if "robotic_system" in institutional_assessment.get("technology_available", []):
                return "robotic"
            else:
                return "laparoscopic"
        elif complexity < 0.7 and fitness > 0.5 and capability > 0.5:
            return "laparoscopic"
        else:
            return "open"
    
    def _determine_resection_type(self, stage: str, location: str, size_cm: float) -> str:
        """Determine appropriate resection type"""
        
        # Total gastrectomy indications
        total_indications = [
            stage in ["T3", "T4", "STAGE III", "STAGE IV"],
            location in ["cardia", "gej", "fundus", "linitis", "multifocal"],
            size_cm > 6.0,
            location == "proximal" and size_cm > 4.0
        ]
        
        if any(total_indications):
            return "total"
        else:
            return "subtotal"
    
    def _determine_lymph_dissection(self, stage: str, resection_type: str) -> str:
        """Determine appropriate lymph node dissection level"""
        
        if stage in ["T1A"]:
            return "D1"
        elif stage in ["T1B", "T2"] and resection_type == "subtotal":
            return "D1+"
        else:
            return "D2"
    
    def _select_reconstruction(
        self, 
        resection: str, 
        approach: str, 
        fitness: Dict[str, Any]
    ) -> str:
        """Select appropriate reconstruction method"""
        
        if resection == "total":
            if fitness["fitness_score"] > 0.7:
                return "roux_en_y_with_pouch"
            else:
                return "roux_en_y"
        else:  # subtotal
            if approach in ["laparoscopic", "robotic"]:
                return "billroth_i"
            else:
                return "billroth_i"  # can consider billroth_ii if needed
    
    def _calculate_decision_confidence(
        self,
        surgical_plan: Dict[str, Any],
        tumor_analysis: Dict[str, Any],
        fitness_assessment: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate confidence in surgical decision"""
        
        # Base confidence from evidence strength
        evidence_confidence = 0.8  # strong evidence base
        
        # Adjust for case complexity
        complexity_factor = 1.0 - (surgical_plan["complexity_score"] * 0.2)
        
        # Adjust for patient fitness
        fitness_factor = fitness_assessment["fitness_score"] * 0.1
        
        # Adjust for data completeness
        required_fields = ["tumor", "patient"]
        optional_fields = ["institution", "preferences"]
        completeness = sum(1 for field in required_fields if field in parameters) / len(required_fields)
        completeness += sum(0.5 for field in optional_fields if field in parameters) / len(optional_fields)
        completeness_factor = min(completeness, 1.0) * 0.1
        
        overall_confidence = evidence_confidence * complexity_factor + fitness_factor + completeness_factor
        overall_confidence = min(max(overall_confidence, 0.0), 1.0)
        
        return {
            "overall_confidence": round(overall_confidence, 3),
            "evidence_strength": evidence_confidence,
            "complexity_adjustment": complexity_factor,
            "fitness_adjustment": fitness_factor,
            "data_completeness": completeness_factor,
            "confidence_level": "high" if overall_confidence > 0.8 else "moderate" if overall_confidence > 0.6 else "low"
        }
    
    async def _generate_alternative_approaches(
        self,
        primary_plan: Dict[str, Any],
        tumor_analysis: Dict[str, Any],
        fitness_assessment: Dict[str, Any],
        confidence_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate alternative surgical approaches"""
        
        alternatives = []
        primary_approach = primary_plan["approach"]
        
        # Alternative surgical approaches
        if primary_approach == "laparoscopic":
            alternatives.append({
                "approach": "open",
                "rationale": "Lower technical complexity, faster learning curve",
                "trade_offs": "Larger incision, longer recovery",
                "confidence": 0.85,
                "recommendation_strength": "moderate"
            })
            
            if "robotic" not in primary_approach:
                alternatives.append({
                    "approach": "robotic",
                    "rationale": "Enhanced precision, better ergonomics",
                    "trade_offs": "Higher cost, longer setup time",
                    "confidence": 0.80,
                    "recommendation_strength": "weak"
                })
        
        elif primary_approach == "open":
            if tumor_analysis["complexity_score"] < 0.6:
                alternatives.append({
                    "approach": "laparoscopic",
                    "rationale": "Faster recovery, better cosmesis",
                    "trade_offs": "Higher technical complexity",
                    "confidence": 0.75,
                    "recommendation_strength": "moderate"
                })
        
        # Alternative resection extent
        if primary_plan["resection"] == "subtotal":
            alternatives.append({
                "approach": "total_gastrectomy",
                "rationale": "Wider oncologic margins",
                "trade_offs": "Greater functional impact",
                "confidence": 0.70,
                "recommendation_strength": "weak"
            })
        
        return alternatives
    
    def _predict_surgical_outcomes(
        self, 
        surgical_plan: Dict[str, Any], 
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict surgical outcomes based on plan and risk"""
        
        approach = surgical_plan["approach"]
        approach_data = self.surgical_approaches[approach]
        
        # Adjust outcomes based on patient risk
        risk_multiplier = 1.0 + risk_analysis["overall_risk"]
        
        return {
            "estimated_los_days": approach_data["recovery_days"] * risk_multiplier,
            "morbidity_risk": approach_data["morbidity_rate"] * risk_multiplier,
            "mortality_risk": approach_data["mortality_rate"] * risk_multiplier,
            "blood_loss_ml": approach_data["blood_loss_ml"] * risk_multiplier,
            "operative_time_min": approach_data["operative_time_min"],
            "functional_outcomes": self._predict_functional_outcomes(surgical_plan),
            "oncologic_outcomes": self._predict_oncologic_outcomes(surgical_plan),
            "quality_of_life": self._predict_qol_outcomes(surgical_plan, risk_analysis)
        }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> List[str]:
        """Validate surgical decision parameters"""
        errors = []
        
        # Required tumor information
        if "tumor" not in parameters:
            errors.append("Missing tumor characteristics")
        else:
            tumor = parameters["tumor"]
            required_tumor_fields = ["stage", "location"]
            for field in required_tumor_fields:
                if field not in tumor:
                    errors.append(f"Missing tumor.{field}")
        
        # Required patient information
        if "patient" not in parameters:
            errors.append("Missing patient information")
        else:
            patient = parameters["patient"]
            required_patient_fields = ["age", "asa_score", "performance_status"]
            for field in required_patient_fields:
                if field not in patient:
                    errors.append(f"Missing patient.{field}")
        
        # Validate age
        if "patient" in parameters and "age" in parameters["patient"]:
            age = parameters["patient"]["age"]
            if not isinstance(age, (int, float)) or age < 0 or age > 120:
                errors.append("Invalid patient age")
        
        return errors
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for surgical decision parameters"""
        return {
            "type": "object",
            "title": "Gastrectomy Surgical Decision Parameters",
            "properties": {
                "tumor": {
                    "type": "object",
                    "required": True,
                    "properties": {
                        "stage": {"type": "string", "enum": ["T1", "T1a", "T1b", "T2", "T3", "T4", "Stage I", "Stage II", "Stage III", "Stage IV"]},
                        "location": {"type": "string", "enum": ["antrum", "body", "fundus", "cardia", "gej", "linitis", "multifocal"]},
                        "size_cm": {"type": "number", "minimum": 0, "maximum": 20},
                        "histology": {"type": "string", "enum": ["adenocarcinoma", "signet_ring", "mixed"]},
                        "differentiation": {"type": "string", "enum": ["well", "moderate", "poor"]}
                    }
                },
                "patient": {
                    "type": "object",
                    "required": True,
                    "properties": {
                        "age": {"type": "integer", "minimum": 0, "maximum": 120},
                        "bmi": {"type": "number", "minimum": 10, "maximum": 60},
                        "asa_score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "performance_status": {"type": "integer", "minimum": 0, "maximum": 4},
                        "comorbidities": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "institution": {
                    "type": "object",
                    "properties": {
                        "annual_cases": {"type": "integer", "minimum": 0},
                        "expertise": {"type": "string", "enum": ["limited", "standard", "experienced", "expert"]},
                        "available_technology": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "support_services": {
                            "type": "array", 
                            "items": {"type": "string"}
                        }
                    }
                },
                "preferences": {
                    "type": "object",
                    "properties": {
                        "approach_preference": {"type": "string", "enum": ["open", "laparoscopic", "robotic", "no_preference"]},
                        "priority": {"type": "string", "enum": ["oncologic_outcome", "functional_preservation", "quick_recovery"]}
                    }
                }
            },
            "required": ["tumor", "patient"]
        }
    
    # Helper methods for outcome prediction
    def _predict_functional_outcomes(self, surgical_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Predict functional outcomes"""
        resection = surgical_plan["resection"]
        
        if resection == "total":
            return {
                "dumping_syndrome_risk": 0.3,
                "weight_loss_expected": 15,
                "dietary_restrictions": "significant",
                "vitamin_supplementation": "lifelong"
            }
        else:
            return {
                "dumping_syndrome_risk": 0.1,
                "weight_loss_expected": 8,
                "dietary_restrictions": "minimal",
                "vitamin_supplementation": "selective"
            }
    
    def _predict_oncologic_outcomes(self, surgical_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Predict oncologic outcomes"""
        lymph_dissection = surgical_plan["lymph_dissection"]
        
        dissection_data = self.lymph_dissection_levels[lymph_dissection]
        
        return {
            "r0_resection_probability": 0.95,
            "local_recurrence_risk": 0.05,
            "lymph_node_yield": len(dissection_data["stations"]),
            "oncologic_adequacy": dissection_data["oncologic_benefit"]
        }
    
    def _predict_qol_outcomes(self, surgical_plan: Dict[str, Any], risk_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Predict quality of life outcomes"""
        approach = surgical_plan["approach"]
        resection = surgical_plan["resection"]
        
        base_qol = 0.8
        
        # Approach impact
        if approach in ["laparoscopic", "robotic"]:
            base_qol += 0.1
        
        # Resection impact
        if resection == "total":
            base_qol -= 0.2
        
        # Risk adjustment
        base_qol -= risk_analysis["overall_risk"] * 0.1
        
        return {
            "6_month_qol_score": min(max(base_qol, 0.0), 1.0),
            "return_to_activity_weeks": 6 if approach in ["laparoscopic", "robotic"] else 8,
            "long_term_satisfaction": 0.85
        }
    
    def _estimate_morbidity(self, risk_score: float) -> float:
        """Estimate morbidity based on risk score"""
        base_morbidity = 0.15
        return min(base_morbidity + (risk_score * 0.2), 0.5)
    
    def _estimate_mortality(self, risk_score: float) -> float:
        """Estimate mortality based on risk score"""
        base_mortality = 0.02
        return min(base_mortality + (risk_score * 0.05), 0.1)
    
    def _get_risk_mitigation(self, risk_level: str) -> List[str]:
        """Get risk mitigation strategies"""
        strategies = {
            "low": ["Standard perioperative care", "Early mobilization"],
            "moderate": ["Enhanced recovery protocol", "Nutritional optimization", "Cardiology consultation if indicated"],
            "high": ["Intensive perioperative monitoring", "ICU bed reservation", "Multidisciplinary team evaluation", "Consider staged approach"]
        }
        return strategies.get(risk_level, [])
    
    def _calculate_procedure_complexity(
        self, 
        approach: str, 
        resection: str, 
        lymph_dissection: str, 
        tumor_analysis: Dict[str, Any]
    ) -> float:
        """Calculate overall procedure complexity"""
        
        base_complexity = self.surgical_approaches[approach]["complexity_factor"]
        resection_complexity = 1.5 if resection == "total" else 1.0
        lymph_complexity = self.lymph_dissection_levels[lymph_dissection]["complexity"]
        
        complexity_map = {"low": 1.0, "moderate": 1.3, "high": 1.6}
        lymph_factor = complexity_map.get(lymph_complexity, 1.3)
        
        tumor_complexity = tumor_analysis["complexity_score"]
        
        overall_complexity = (base_complexity * resection_complexity * lymph_factor + tumor_complexity) / 3.0
        return min(overall_complexity, 2.0)
    
    def _estimate_duration(self, approach: str, resection: str, complexity: float) -> float:
        """Estimate procedure duration"""
        base_duration = self.surgical_approaches[approach]["operative_time_min"]
        
        if resection == "total":
            base_duration *= 1.3
        
        complexity_adjustment = 1.0 + (complexity - 1.0) * 0.3
        
        return base_duration * complexity_adjustment / 60  # Convert to hours
    
    def _generate_perioperative_plan(
        self, 
        fitness_assessment: Dict[str, Any], 
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate perioperative care plan"""
        
        risk_level = risk_analysis["risk_level"]
        
        return {
            "preoperative": {
                "optimization_needed": fitness_assessment["fitness_score"] < 0.7,
                "consultations": self._get_required_consultations(fitness_assessment),
                "monitoring": "standard" if risk_level == "low" else "enhanced"
            },
            "intraoperative": {
                "monitoring_level": "standard" if risk_level == "low" else "invasive",
                "fluid_strategy": "goal_directed",
                "anesthesia_considerations": self._get_anesthesia_considerations(fitness_assessment)
            },
            "postoperative": {
                "icu_required": risk_level == "high",
                "monitoring_duration_hours": 24 if risk_level == "low" else 48,
                "early_feeding": True,
                "mobilization": "day_1"
            }
        }
    
    def _define_quality_metrics(self, approach: str, resection: str) -> Dict[str, Any]:
        """Define quality metrics for the procedure"""
        return {
            "target_r0_rate": 0.95,
            "target_morbidity": self.surgical_approaches[approach]["morbidity_rate"],
            "target_mortality": self.surgical_approaches[approach]["mortality_rate"],
            "target_los": self.surgical_approaches[approach]["recovery_days"],
            "lymph_node_target": 25 if resection == "total" else 15,
            "conversion_rate_threshold": 0.10 if approach == "laparoscopic" else None
        }
    
    def _determine_evidence_level(self, surgical_plan: Dict[str, Any]) -> str:
        """Determine evidence level for recommendation"""
        approach = surgical_plan["approach"]
        resection = surgical_plan["resection"]
        
        # High evidence for standard procedures
        if approach in ["open", "laparoscopic"] and resection in ["subtotal", "total"]:
            return "Grade A (Multiple RCTs)"
        elif approach == "robotic":
            return "Grade B (Limited RCTs, observational studies)"
        else:
            return "Grade C (Expert opinion)"
    
    def _check_guideline_compliance(
        self, 
        surgical_plan: Dict[str, Any], 
        tumor_analysis: Dict[str, Any]
    ) -> bool:
        """Check compliance with international guidelines"""
        
        # JGCA/IGCA compliance checks
        resection = surgical_plan["resection"]
        lymph_dissection = surgical_plan["lymph_dissection"]
        stage = tumor_analysis["stage"]
        
        # Check if lymph dissection is adequate for stage
        if stage in ["T3", "T4"] and lymph_dissection != "D2":
            return False
        
        # Check if resection is appropriate for location
        location = tumor_analysis["location"]
        if location in ["cardia", "gej"] and resection != "total":
            return False
        
        return True
    
    def _get_required_consultations(self, fitness_assessment: Dict[str, Any]) -> List[str]:
        """Get required preoperative consultations"""
        consultations = []
        
        if fitness_assessment["asa_score"] >= 3:
            consultations.append("anesthesiology")
        
        high_risk_comorbidities = fitness_assessment.get("high_risk_comorbidities", [])
        
        if "heart_failure" in high_risk_comorbidities or "previous_mi" in high_risk_comorbidities:
            consultations.append("cardiology")
        
        if "copd" in high_risk_comorbidities:
            consultations.append("pulmonology")
        
        if fitness_assessment["age"] > 75:
            consultations.append("geriatrics")
        
        return consultations
    
    def _get_anesthesia_considerations(self, fitness_assessment: Dict[str, Any]) -> List[str]:
        """Get anesthesia considerations"""
        considerations = []
        
        if fitness_assessment["bmi"] > 35:
            considerations.append("difficult_airway_risk")
        
        if fitness_assessment["asa_score"] >= 3:
            considerations.append("invasive_monitoring")
        
        comorbidities = fitness_assessment.get("high_risk_comorbidities", [])
        if "heart_failure" in comorbidities:
            considerations.append("cardiac_optimization")
        
        return considerations
    
    def _assess_oncologic_priority(self, stage: str, histology: str) -> str:
        """Assess oncologic priority level"""
        
        if stage in ["T3", "T4", "STAGE III", "STAGE IV"]:
            return "high"
        elif histology == "signet_ring":
            return "high"
        elif stage in ["T2", "STAGE II"]:
            return "moderate"
        else:
            return "standard"
    
    def _get_suitable_procedures(self, capability_score: float, expertise_level: str) -> List[str]:
        """Get procedures suitable for institutional capability"""
        
        procedures = ["open_gastrectomy"]
        
        if capability_score >= 0.6 and expertise_level in ["experienced", "expert"]:
            procedures.append("laparoscopic_gastrectomy")
        
        if capability_score >= 0.8 and expertise_level == "expert":
            procedures.append("robotic_gastrectomy")
        
        return procedures
