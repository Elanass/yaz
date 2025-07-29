"""
FLOT Protocol Analysis Module for Gastric Oncology - MVP Version

This module provides simplified analysis for FLOT (Fluorouracil, Leucovorin, Oxaliplatin, and Docetaxel)
perioperative chemotherapy for gastric cancer patients.
"""

from typing import Dict, Any, List, Optional
import logging

from core.services.logger import get_logger

logger = get_logger(__name__)

class FLOTAnalyzer:
    """
    Specialized analyzer for FLOT protocol in gastric cancer treatment
    """
    
    def __init__(self):
        """Initialize the FLOT analyzer"""
        self.protocol_version = "2.1-MVP"
        logger.info(f"FLOT Analyzer initialized with protocol version {self.protocol_version}")
    
    def analyze_gastric_surgery_case(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core FLOT protocol analysis for gastric surgery cases
        
        Args:
            patient_data: Dictionary containing patient clinical data
            
        Returns:
            Dictionary with treatment plan, risk assessment, and follow-up schedule
        """
        # Validate patient data for FLOT protocol
        if not self._validate_patient_data(patient_data):
            logger.error("Invalid patient data for FLOT analysis")
            return {"error": "Invalid patient data for FLOT analysis"}
        
        try:
            # Generate the complete FLOT analysis
            treatment_plan = self._generate_treatment_plan(patient_data)
            risk_assessment = self._calculate_risks(patient_data)
            follow_up = self._create_follow_up(patient_data)
            
            result = {
                "treatment_plan": treatment_plan,
                "risk_assessment": risk_assessment,
                "follow_up_schedule": follow_up,
                "protocol_version": self.protocol_version
            }
            
            logger.info(f"FLOT analysis completed for patient {patient_data.get('patient_id', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Error in FLOT analysis: {str(e)}")
            return {"error": str(e)}
    
    def _validate_patient_data(self, patient_data: Dict[str, Any]) -> bool:
        """
        Validate patient data for FLOT protocol analysis
        """
        required_fields = [
            "age", "performance_status", "tumor_stage", "histology", 
            "comorbidities", "prior_treatments"
        ]
        
        return all(field in patient_data for field in required_fields)
    
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
