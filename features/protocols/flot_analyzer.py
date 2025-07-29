"""
FLOT Protocol Analysis Module for Decision Precision in Gastric Surgery

This module provides comprehensive analysis for FLOT (Fluorouracil, Leucovorin, Oxaliplatin, and Docetaxel)
perioperative chemotherapy for gastric cancer patients with impact assessment on surgical outcomes.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
import json

from core.services.logger import get_logger, audit_log
from core.utils.validation import validate_patient_data

logger = get_logger(__name__)

class FLOTAnalyzer:
    """
    Specialized analyzer for FLOT protocol in gastric cancer treatment
    with precision impact assessment capabilities
    """
    
    def __init__(self):
        """Initialize the enhanced FLOT analyzer"""
        self.protocol_version = "3.0-Precision"
        self.evidence_levels = {
            "A": "High-quality evidence from multiple RCTs",
            "B": "Moderate-quality evidence from single RCT or multiple cohort studies",
            "C": "Low-quality evidence from observational studies",
            "D": "Expert opinion or case studies"
        }
        logger.info(f"FLOT Analyzer initialized with precision protocol version {self.protocol_version}")
    
    async def analyze_gastric_surgery_case(self, patient_data: Dict[str, Any], 
                                     research_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Core FLOT protocol analysis for gastric surgery cases with collaborative research support
        
        Args:
            patient_data: Dictionary containing patient clinical data
            research_context: Optional context for research collaboration
            
        Returns:
            Dictionary with treatment plan, risk assessment, follow-up schedule,
            and collaborative research insights
        """
        """
        # Validate patient data for FLOT protocol
        if not self._validate_patient_data(patient_data):
            logger.error("Invalid patient data for FLOT analysis")
            return {"error": "Invalid patient data for FLOT analysis"}
        
        # Log analysis with audit trail
        patient_id = patient_data.get("patient_id", "unknown")
        audit_log(
            action="flot_analysis_start",
            resource_type="patient_data",
            resource_id=patient_id,
            details="Starting FLOT protocol analysis with collaborative research"
        )
        """
        # Validate patient data for FLOT protocol using centralized validation
        is_valid, missing_fields = validate_patient_data(patient_data, "flot")
        if not is_valid:
            error_msg = f"Invalid patient data for FLOT analysis: missing {', '.join(missing_fields)}"
            logger.error(error_msg)
            return {"error": error_msg}
        
        # Log analysis with audit trail
        patient_id = patient_data.get("patient_id", "unknown")
        audit_log(
            action="flot_analysis_start",
            resource_type="patient_data",
            resource_id=patient_id,
            details="Starting FLOT protocol analysis with collaborative research"
        )
        
        try:
            # Generate the complete FLOT analysis
            treatment_plan = self._generate_treatment_plan(patient_data)
            risk_assessment = self._calculate_risks(patient_data)
            follow_up = self._create_follow_up(patient_data)
            
            # Generate research insights if context provided
            if research_context:
                research_insights = self._generate_research_insights(
                    patient_data, 
                    treatment_plan,
                    research_context
                )
                evidence_quality = self._assess_evidence_quality(research_context)
            else:
                research_insights = None
                evidence_quality = None
            
            # Generate impact metrics for FLOT on surgical outcomes
            surgical_impact = self._analyze_surgical_impact(patient_data, treatment_plan)
            
            result = {
                "treatment_plan": treatment_plan,
                "risk_assessment": risk_assessment,
                "follow_up_schedule": follow_up,
                "surgical_impact": surgical_impact,
                "research_insights": research_insights,
                "evidence_quality": evidence_quality,
                "protocol_version": self.protocol_version,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            # Log successful analysis with audit trail
            audit_log(
                action="flot_analysis_complete",
                resource_type="patient_data",
                resource_id=patient_id,
                details=f"FLOT analysis completed with {treatment_plan.get('recommendation', 'unknown')} recommendation"
            )
            
            logger.info(f"FLOT analysis completed for patient {patient_id}")
            return result
            
        except Exception as e:
            # Log error with audit trail
            audit_log(
                action="flot_analysis_error",
                resource_type="patient_data",
                resource_id=patient_id,
                details=f"Error in FLOT analysis: {str(e)}"
            )
            
            logger.error(f"Error in FLOT analysis: {str(e)}")
            return {"error": str(e)}
    
    def _generate_treatment_plan(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a FLOT treatment plan based on patient data
        """
        age = patient_data.get("age", 0)
        performance_status = patient_data.get("performance_status", "")
        tumor_stage = patient_data.get("tumor_stage", "")
        
        # Determine if patient is eligible for standard FLOT protocol
        is_standard_eligible = (
            age < 75 and 
            performance_status in ["0", "1"] and
            tumor_stage in ["II", "III", "IVA"]
        )
        
        # Determine if dose reduction is needed
        needs_dose_reduction = (
            (age >= 70 and age < 75) or
            performance_status == "2" or
            patient_data.get("renal_impairment", False)
        )
        
        # Define cycles based on stage and eligibility
        if is_standard_eligible:
            preop_cycles = 4
            postop_cycles = 4
            cycle_length_days = 14
        else:
            preop_cycles = 3
            postop_cycles = 3
            cycle_length_days = 21
            
        # Generate drug dosing
        dosing = self._calculate_drug_dosing(patient_data, needs_dose_reduction)
        
        # Determine recommendation
        if is_standard_eligible:
            recommendation = "Standard FLOT Protocol Recommended"
            confidence = "high"
        elif needs_dose_reduction:
            recommendation = "Modified FLOT Protocol with Dose Reduction"
            confidence = "moderate"
        else:
            recommendation = "Consider Alternative Protocol"
            confidence = "low"
            
        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "preoperative_cycles": preop_cycles,
            "postoperative_cycles": postop_cycles,
            "cycle_length_days": cycle_length_days,
            "dosing": dosing,
            "standard_protocol_eligible": is_standard_eligible,
            "dose_reduction_required": needs_dose_reduction,
            "expected_completion_weeks": (preop_cycles + postop_cycles) * (cycle_length_days / 7)
        }
        
    def _calculate_drug_dosing(self, patient_data: Dict[str, Any], needs_reduction: bool) -> Dict[str, Any]:
        """Calculate drug dosing based on patient parameters"""
        # Standard FLOT dosing
        standard_dosing = {
            "docetaxel": {"dose": 50, "unit": "mg/m2", "day": 1},
            "oxaliplatin": {"dose": 85, "unit": "mg/m2", "day": 1},
            "leucovorin": {"dose": 200, "unit": "mg/m2", "day": 1},
            "fluorouracil": {"dose": 2600, "unit": "mg/m2", "day": "1-2 (24h infusion)"}
        }
        
        # Apply dose reduction if needed
        if needs_reduction:
            reduction_factor = 0.75  # 25% dose reduction
            for drug in standard_dosing:
                standard_dosing[drug]["dose"] *= reduction_factor
                standard_dosing[drug]["note"] = "Dose reduced due to patient factors"
                
        return standard_dosing
    
    def _calculate_risks(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate FLOT-related risks based on patient data
        """
        age = patient_data.get("age", 0)
        comorbidities = patient_data.get("comorbidities", [])
        
        # Calculate risks for different toxicities
        hematologic_risk = self._calculate_hematologic_risk(patient_data)
        gi_risk = self._calculate_gi_risk(patient_data)
        neuropathy_risk = self._calculate_neuropathy_risk(patient_data)
        
        # Calculate overall risk
        risk_factors = []
        
        if age > 70:
            risk_factors.append("Advanced age")
            
        if "diabetes" in comorbidities:
            risk_factors.append("Diabetes (increased neuropathy risk)")
            
        if "renal_impairment" in comorbidities:
            risk_factors.append("Renal impairment (increased toxicity risk)")
            
        # Overall risk category
        if hematologic_risk > 0.5 or gi_risk > 0.5 or neuropathy_risk > 0.5 or len(risk_factors) > 2:
            overall_risk = "high"
        elif hematologic_risk > 0.3 or gi_risk > 0.3 or neuropathy_risk > 0.3 or len(risk_factors) > 0:
            overall_risk = "moderate"
        else:
            overall_risk = "low"
            
        return {
            "overall_risk": overall_risk,
            "risk_factors": risk_factors,
            "toxicity_risks": {
                "hematologic": hematologic_risk,
                "gastrointestinal": gi_risk,
                "neuropathy": neuropathy_risk
            },
            "mitigation_strategies": self._generate_risk_mitigation(patient_data)
        }
        
    def _calculate_hematologic_risk(self, patient_data: Dict[str, Any]) -> float:
        """Calculate risk of hematologic toxicity"""
        # Simplified calculation for MVP
        base_risk = 0.2  # Base risk
        
        age = patient_data.get("age", 0)
        if age > 70:
            base_risk += 0.1
            
        lab_results = patient_data.get("lab_results", {})
        if lab_results.get("wbc", 10) < 4:
            base_risk += 0.2
            
        if lab_results.get("platelets", 300) < 150:
            base_risk += 0.2
            
        return min(base_risk, 1.0)  # Cap at 1.0
        
    def _calculate_gi_risk(self, patient_data: Dict[str, Any]) -> float:
        """Calculate risk of GI toxicity"""
        # Simplified calculation for MVP
        base_risk = 0.3  # Base risk for FLOT
        
        if "ibd" in patient_data.get("comorbidities", []):
            base_risk += 0.3
            
        if patient_data.get("prior_gi_surgery", False):
            base_risk += 0.2
            
        return min(base_risk, 1.0)  # Cap at 1.0
        
    def _calculate_neuropathy_risk(self, patient_data: Dict[str, Any]) -> float:
        """Calculate risk of neuropathy"""
        # Simplified calculation for MVP
        base_risk = 0.25  # Base risk for FLOT
        
        if "diabetes" in patient_data.get("comorbidities", []):
            base_risk += 0.2
            
        if "prior_platinum_therapy" in patient_data.get("prior_treatments", []):
            base_risk += 0.3
            
        return min(base_risk, 1.0)  # Cap at 1.0
        
    def _generate_risk_mitigation(self, patient_data: Dict[str, Any]) -> List[str]:
        """Generate risk mitigation strategies"""
        strategies = [
            "Regular CBC monitoring",
            "Proactive antiemetic therapy",
            "Clinical assessment before each cycle"
        ]
        
        # Add targeted strategies based on risk factors
        if patient_data.get("age", 0) > 70:
            strategies.append("Consider G-CSF support")
            
        if "diabetes" in patient_data.get("comorbidities", []):
            strategies.append("Enhanced neuropathy monitoring")
            
        return strategies
    
    def _create_follow_up(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a follow-up schedule based on patient data and FLOT plan
        """
        # Standard follow-up schedule
        schedule = [
            {"timepoint": "Before each cycle", "assessments": ["CBC", "Chemistry panel", "Clinical assessment"]},
            {"timepoint": "After 2 cycles", "assessments": ["CT scan", "Clinical assessment"]},
            {"timepoint": "Before surgery", "assessments": ["CT scan", "Endoscopy", "Surgical evaluation"]},
            {"timepoint": "After surgery", "assessments": ["Pathology review", "Multidisciplinary discussion"]},
            {"timepoint": "During postop cycles", "assessments": ["CBC", "Chemistry panel", "Clinical assessment"]},
            {"timepoint": "3 months post-completion", "assessments": ["CT scan", "Clinical assessment"]},
            {"timepoint": "6 months post-completion", "assessments": ["CT scan", "Endoscopy", "Clinical assessment"]},
            {"timepoint": "12 months post-completion", "assessments": ["CT scan", "Clinical assessment"]}
        ]
        
        # Add high-risk monitoring if needed
        risk_factors = []
        if patient_data.get("age", 0) > 75:
            risk_factors.append("Advanced age")
            
        if "cardiac_disease" in patient_data.get("comorbidities", []):
            risk_factors.append("Cardiac comorbidity")
            schedule.append({"timepoint": "Before each cycle", "assessments": ["ECG", "Cardiac assessment"]})
            
        return {
            "schedule": schedule,
            "additional_monitoring": len(risk_factors) > 0,
            "risk_factors": risk_factors
        }
        
    def _analyze_surgical_impact(self, patient_data: Dict[str, Any], 
                               treatment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the impact of FLOT on surgical outcomes
        
        Args:
            patient_data: Patient clinical data
            treatment_plan: Generated FLOT treatment plan
            
        Returns:
            Dictionary with surgical impact assessment
        """
        # Implementation would analyze how FLOT affects surgical outcomes
        # Simplified implementation for MVP
        
        # Expected downstaging based on literature
        downstaging_probability = 0.65  # ~65% chance of downstaging based on FLOT trials
        
        # Factors affecting surgical impact
        if treatment_plan.get("standard_protocol_eligible", False):
            completion_probability = 0.8  # 80% chance of completing all preop cycles
            response_quality = "good"
        else:
            completion_probability = 0.6  # 60% chance with modified protocol
            response_quality = "moderate"
            
        # R0 resection probability
        r0_probability = 0.75 if treatment_plan.get("standard_protocol_eligible", False) else 0.65
            
        return {
            "expected_downstaging": downstaging_probability,
            "completion_probability": completion_probability,
            "expected_response": response_quality,
            "r0_resection_probability": r0_probability,
            "surgical_complexity_impact": "Potentially reduced due to tumor response",
            "expected_surgical_benefits": [
                "Improved R0 resection rate",
                "Potential for organ preservation",
                "Reduced surgical morbidity with good response"
            ],
            "surgical_considerations": [
                "Plan surgery 4-6 weeks after last FLOT cycle",
                "Assess response before surgical approach finalization",
                "Consider post-FLOT re-staging to optimize surgical approach"
            ]
        }
        
    def _generate_research_insights(self, patient_data: Dict[str, Any],
                                 treatment_plan: Dict[str, Any],
                                 research_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate research insights based on the case and research context
        
        Args:
            patient_data: Patient clinical data
            treatment_plan: Generated FLOT treatment plan
            research_context: Research collaboration context
            
        Returns:
            Dictionary with research insights
        """
        # Implementation would generate research insights
        # Simplified implementation for MVP
        
        # Research relevance assessment
        research_relevance = []
        
        if patient_data.get("age", 0) > 75 and "elderly_outcomes" in research_context.get("focus_areas", []):
            research_relevance.append("Elderly patient outcomes")
            
        if not treatment_plan.get("standard_protocol_eligible", True) and "protocol_modifications" in research_context.get("focus_areas", []):
            research_relevance.append("Modified protocol outcomes")
        
        # Generate collaborative findings
        return {
            "research_relevance": research_relevance,
            "potential_study_cohorts": self._identify_study_cohorts(patient_data, research_context),
            "literature_gaps": research_context.get("identified_gaps", []),
            "recommended_data_collection": self._recommend_data_collection(patient_data, research_context),
            "collaborative_opportunities": research_context.get("collaboration_opportunities", [])
        }
        
    def _identify_study_cohorts(self, patient_data: Dict[str, Any], 
                              research_context: Dict[str, Any]) -> List[str]:
        """Identify potential study cohorts for the patient case"""
        # Implementation would identify relevant research cohorts
        # Simplified implementation for MVP
        cohorts = []
        
        if patient_data.get("age", 0) > 70:
            cohorts.append("Elderly FLOT recipients")
            
        if "diabetes" in patient_data.get("comorbidities", []):
            cohorts.append("FLOT with metabolic comorbidities")
            
        if patient_data.get("tumor_stage", "") == "III":
            cohorts.append("Locally advanced gastric cancer")
            
        return cohorts
        
    def _recommend_data_collection(self, patient_data: Dict[str, Any],
                                 research_context: Dict[str, Any]) -> List[str]:
        """Recommend specific data points to collect for research"""
        # Implementation would recommend specific data collection
        # Simplified implementation for MVP
        recommendations = [
            "Quality of life measurements during FLOT",
            "Detailed toxicity grading and timeline",
            "Molecular tumor analysis"
        ]
        
        if patient_data.get("age", 0) > 70:
            recommendations.append("Geriatric assessment scores")
            
        return recommendations
        
    def _assess_evidence_quality(self, research_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the quality of evidence for FLOT recommendations
        
        Args:
            research_context: Research collaboration context
            
        Returns:
            Dictionary with evidence quality assessment
        """
        # Implementation would assess evidence quality
        # Simplified implementation for MVP
        
        # Standard FLOT has high-quality evidence
        standard_evidence = {
            "level": "A",
            "description": self.evidence_levels["A"],
            "key_studies": ["FLOT4-AIO", "FLOT4 phase 2"]
        }
        
        # Modified protocols have lower quality evidence
        modified_evidence = {
            "level": "B",
            "description": self.evidence_levels["B"],
            "key_studies": ["Retrospective cohort studies", "Single-arm phase 2 trials"]
        }
        
        # Special populations often have lowest quality evidence
        special_populations = {
            "level": "C",
            "description": self.evidence_levels["C"],
            "key_studies": ["Case series", "Expert opinion", "Extrapolation from other populations"]
        }
        
        return {
            "standard_protocol": standard_evidence,
            "modified_protocol": modified_evidence,
            "special_populations": special_populations,
            "evidence_gaps": research_context.get("evidence_gaps", [
                "Optimal management in elderly",
                "Duration of therapy",
                "Management of specific toxicities"
            ])
        }
        
        # Determine if patient is eligible for standard FLOT protocol
        is_standard_eligible = (
            age < 75 and 
            performance_status in ["0", "1"] and
            tumor_stage in ["II", "III", "IVA"]
        )
        
        # Determine if dose reduction is needed
        needs_dose_reduction = (
            (age >= 70 and age < 75) or
            performance_status == "2" or
            patient_data.get("renal_impairment", False)
        )
        
        # Define cycles based on stage and eligibility
        if is_standard_eligible:
            preop_cycles = 4
            postop_cycles = 4
            cycle_length_days = 14
        else:
            preop_cycles = 3
            postop_cycles = 3
            cycle_length_days = 21
        
        # Define dosing
        if needs_dose_reduction:
            dosing = {
                "fluorouracil": "2000 mg/m²",
                "leucovorin": "200 mg/m²",
                "oxaliplatin": "75 mg/m²",
                "docetaxel": "45 mg/m²"
            }
        else:
            dosing = {
                "fluorouracil": "2600 mg/m²",
                "leucovorin": "200 mg/m²",
                "oxaliplatin": "85 mg/m²",
                "docetaxel": "50 mg/m²"
            }
        
        return {
            "eligible_for_standard_protocol": is_standard_eligible,
            "dose_reduction_recommended": needs_dose_reduction,
            "preoperative_cycles": preop_cycles,
            "postoperative_cycles": postop_cycles,
            "cycle_length_days": cycle_length_days,
            "dosing": dosing,
            "total_treatment_duration_weeks": (preop_cycles + postop_cycles) * cycle_length_days / 7,
            "special_considerations": self._get_special_considerations(patient_data)
        }
    
    def _calculate_risks(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risks associated with FLOT treatment
        """
        age = patient_data.get("age", 0)
        comorbidities = patient_data.get("comorbidities", [])
        
        # Calculate base risk scores
        neutropenia_risk = 0.25
        neuropathy_risk = 0.30
        gi_toxicity_risk = 0.35
        
        # Adjust for age
        if age > 70:
            neutropenia_risk += 0.15
            neuropathy_risk += 0.10
            gi_toxicity_risk += 0.10
        
        # Adjust for comorbidities
        if "diabetes" in comorbidities:
            neuropathy_risk += 0.15
        
        if "cardiac" in comorbidities:
            neutropenia_risk += 0.10
        
        if "gastrointestinal" in comorbidities:
            gi_toxicity_risk += 0.20
        
        # Calculate overall risk
        overall_risk = (neutropenia_risk + neuropathy_risk + gi_toxicity_risk) / 3
        risk_category = "high" if overall_risk > 0.5 else "moderate" if overall_risk > 0.3 else "low"
        
        return {
            "neutropenia_risk": round(neutropenia_risk, 2),
            "neuropathy_risk": round(neuropathy_risk, 2),
            "gi_toxicity_risk": round(gi_toxicity_risk, 2),
            "overall_risk": round(overall_risk, 2),
            "risk_category": risk_category,
            "recommended_monitoring": self._get_monitoring_recommendations(risk_category)
        }
    
    def _create_follow_up(self, patient_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a follow-up schedule based on patient data and FLOT protocol
        """
        tumor_stage = patient_data.get("tumor_stage", "")
        
        # Base follow-up schedule
        follow_up = [
            {"timepoint": "2 weeks", "assessments": ["CBC", "Chemistry panel", "Clinical assessment"]},
            {"timepoint": "4 weeks", "assessments": ["CBC", "Chemistry panel", "Clinical assessment"]},
            {"timepoint": "3 months", "assessments": ["CBC", "Chemistry panel", "CT scan", "Clinical assessment"]},
            {"timepoint": "6 months", "assessments": ["CBC", "Chemistry panel", "CT scan", "Clinical assessment"]},
            {"timepoint": "12 months", "assessments": ["CBC", "Chemistry panel", "CT scan", "Clinical assessment"]}
        ]
        
        # Adjust for higher stage disease
        if tumor_stage in ["III", "IVA"]:
            follow_up.append(
                {"timepoint": "9 months", "assessments": ["CBC", "Chemistry panel", "CT scan", "Clinical assessment"]}
            )
            # Add more frequent endoscopy for high risk patients
            for item in follow_up:
                if item["timepoint"] in ["6 months", "12 months"]:
                    item["assessments"].append("Endoscopy")
        
        return follow_up
    
    def _get_special_considerations(self, patient_data: Dict[str, Any]) -> List[str]:
        """
        Get special considerations for the patient based on their data
        """
        considerations = []
        
        age = patient_data.get("age", 0)
        comorbidities = patient_data.get("comorbidities", [])
        
        if age > 70:
            considerations.append("Consider G-CSF prophylaxis due to age-related neutropenia risk")
        
        if "diabetes" in comorbidities:
            considerations.append("Monitor neuropathy closely; consider dose reduction for oxaliplatin if symptoms develop")
        
        if "renal_impairment" in patient_data and patient_data["renal_impairment"]:
            considerations.append("Adjust fluorouracil dose based on creatinine clearance")
        
        if "prior_cardiotoxicity" in patient_data and patient_data["prior_cardiotoxicity"]:
            considerations.append("Obtain baseline cardiac function and monitor throughout treatment")
        
        return considerations
    
    def _get_monitoring_recommendations(self, risk_category: str) -> List[str]:
        """
        Get monitoring recommendations based on risk category
        """
        if risk_category == "high":
            return [
                "Weekly CBC for first 2 cycles",
                "Biweekly comprehensive metabolic panel",
                "Proactive antiemetic therapy",
                "Consider G-CSF prophylaxis",
                "Weekly clinical assessment during first cycle"
            ]
        elif risk_category == "moderate":
            return [
                "CBC prior to each cycle",
                "Comprehensive metabolic panel every cycle",
                "Standard antiemetic protocol",
                "Biweekly clinical assessment"
            ]
        else:  # low
            return [
                "CBC prior to each cycle",
                "Comprehensive metabolic panel every cycle",
                "Standard antiemetic protocol",
                "Clinical assessment before each cycle"
            ]
            
    def analyze_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Public method to analyze a patient for FLOT protocol eligibility
        
        Args:
            patient_data: Dictionary containing patient data
            
        Returns:
            Analysis result including treatment plan and recommendations
        """
        return self.analyze_gastric_surgery_case(patient_data)
        
    def validate_input(self, patient_data: Dict[str, Any]) -> bool:
        """
        Validate patient data for FLOT protocol analysis
        Public interface for main.py endpoint
        
        Args:
            patient_data: Dictionary containing patient data
            
        Returns:
            Boolean indicating whether the data is valid
        """
        return self._validate_patient_data(patient_data)
