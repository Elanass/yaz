"""
Enhanced FLOT Protocol Analyzer

This module extends the base FLOTAnalyzer with enhanced surgical
integration features for comprehensive gastric cancer surgical management.

The enhanced analyzer adds surgical planning, perioperative management,
and complication prevention strategies to the base FLOT analysis.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from features.protocols.flot_analyzer import FLOTAnalyzer

logger = logging.getLogger(__name__)


class EnhancedFLOTAnalyzer(FLOTAnalyzer):
    """
    Enhanced FLOT Protocol Analyzer with integrated surgical management features.
    
    This class extends the base FLOTAnalyzer with comprehensive surgical
    planning and management capabilities for gastric cancer patients.
    """
    
    async def analyze_gastric_surgery_case(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced FLOT analysis with integrated surgical management.
        
        Args:
            patient_data: Dictionary containing patient and case data
            
        Returns:
            Dictionary with comprehensive FLOT and surgical analysis
        """
        # Get base FLOT analysis from parent class
        base_analysis = await super().analyze_gastric_surgery_case(patient_data)
        
        # Add surgical enhancements
        surgical_enhancements = {
            'preoperative_optimization': self._optimize_preop_care(patient_data),
            'surgical_planning': self._plan_surgical_approach(patient_data),
            'perioperative_management': self._manage_periop_care(patient_data),
            'postoperative_pathway': self._design_postop_pathway(patient_data),
            'complication_prevention': self._prevent_complications(patient_data)
        }
        
        # Calculate expected surgical outcomes
        expected_outcomes = self._calculate_expected_outcomes(patient_data, base_analysis)
        
        # Combine base analysis with surgical enhancements and outcomes
        result = {**base_analysis, **surgical_enhancements, 'expected_outcomes': expected_outcomes}
        
        # Add evidence-based recommendations
        result['evidence_based_recommendations'] = self._get_evidence_based_recommendations(
            patient_data, 
            base_analysis
        )
        
        return result
    
    def _optimize_preop_care(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize preoperative care for gastric surgery patients.
        
        Args:
            patient_data: Dictionary containing patient and case data
            
        Returns:
            Dictionary with preoperative optimization recommendations
        """
        recommendations = {
            "nutrition": {
                "assessment": "Required",
                "intervention": "Standard nutritional support"
            },
            "cardiopulmonary": {
                "assessment": "Required",
                "intervention": "Standard preoperative evaluation"
            },
            "anemia": {
                "assessment": "Required",
                "intervention": "No specific intervention"
            }
        }
        
        # Check for malnutrition risk
        albumin = patient_data.get('lab_values', {}).get('albumin', 4.0)
        weight_loss = patient_data.get('weight_loss_percentage', 0)
        
        if albumin < 3.5 or weight_loss > 10:
            recommendations["nutrition"]["intervention"] = "Enhanced nutritional support protocol"
            recommendations["nutrition"]["details"] = "Immunonutrition supplementation for 7 days preoperatively"
        
        # Check for anemia
        hemoglobin = patient_data.get('lab_values', {}).get('hemoglobin', 14.0)
        
        if hemoglobin < 12.0:
            recommendations["anemia"]["intervention"] = "Iron supplementation"
            if hemoglobin < 8.0:
                recommendations["anemia"]["intervention"] = "Consider transfusion and hematology consult"
        
        # Check for cardiopulmonary risk
        if (patient_data.get('age', 0) > 70 or 
            'copd' in patient_data.get('comorbidities', []) or
            'coronary_artery_disease' in patient_data.get('comorbidities', [])):
            
            recommendations["cardiopulmonary"]["intervention"] = "Enhanced cardiopulmonary assessment"
            recommendations["cardiopulmonary"]["details"] = "Consider cardiopulmonary exercise testing"
        
        return recommendations
    
    def _plan_surgical_approach(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan optimal surgical approach based on patient factors.
        
        Args:
            patient_data: Dictionary containing patient and case data
            
        Returns:
            Dictionary with surgical approach recommendations
        """
        # Default approach
        approach = "laparoscopic"
        procedure = "distal gastrectomy"
        reconstruction = "Billroth II"
        rationale = "Standard approach for distal gastric cancer"
        
        # Check tumor location
        tumor_location = patient_data.get('tumor_location', 'distal')
        
        if tumor_location in ['proximal', 'cardia', 'GEJ']:
            procedure = "total gastrectomy"
            reconstruction = "Roux-en-Y esophagojejunostomy"
            rationale = "Proximal tumor location requires total gastrectomy"
        
        # Check for factors that might suggest open approach
        if patient_data.get('bmi', 0) > 35:
            approach = "open"
            rationale = "High BMI may complicate laparoscopic approach"
        elif 'prior_major_abdominal_surgery' in patient_data.get('medical_history', []):
            approach = "open"
            rationale = "Prior abdominal surgery with potential adhesions"
        elif 'T4' in patient_data.get('tumor_stage', ''):
            approach = "open"
            rationale = "Advanced T-stage with potential adjacent organ involvement"
        
        # Lymphadenectomy extent
        lymphadenectomy = "D2"
        if 'early_gastric_cancer' in patient_data.get('diagnosis_details', []):
            lymphadenectomy = "D1+"
        
        return {
            "recommended_approach": approach,
            "recommended_procedure": procedure,
            "recommended_reconstruction": reconstruction,
            "lymphadenectomy_extent": lymphadenectomy,
            "rationale": rationale,
            "technical_considerations": [
                f"{lymphadenectomy} lymphadenectomy required",
                "Consider placement of feeding tube if nutritionally compromised",
                "Assess for peritoneal metastases with staging laparoscopy",
                "Frozen section of margins recommended"
            ]
        }
    
    def _manage_periop_care(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage perioperative care for gastric surgery.
        
        Args:
            patient_data: Dictionary containing patient and case data
            
        Returns:
            Dictionary with perioperative management recommendations
        """
        management = {
            "fluid_management": {
                "recommendation": "Balanced crystalloid solution",
                "approach": "Goal-directed therapy",
                "targets": "MAP > 65 mmHg, UO > 0.5 mL/kg/hr"
            },
            "pain_control": {
                "primary": "Multimodal analgesia",
                "regional": "None",
                "medications": ["Acetaminophen", "NSAIDs", "Limited opioids"]
            },
            "glucose_management": {
                "target_range": "140-180 mg/dL",
                "monitoring": "Q4H for 48 hours"
            },
            "monitoring_requirements": {
                "level": "Standard monitoring",
                "special": []
            }
        }
        
        # Enhanced monitoring for high-risk patients
        if patient_data.get('asa_score', 2) >= 3:
            management["monitoring_requirements"]["level"] = "Enhanced monitoring"
            management["monitoring_requirements"]["special"] = ["Arterial line", "Consider ICU postop"]
        
        # Modify pain management for specific conditions
        if 'chronic_pain' in patient_data.get('medical_history', []):
            management["pain_control"]["primary"] = "Enhanced multimodal analgesia"
            management["pain_control"]["special"] = "Pain management consultation"
        
        if approach := patient_data.get('surgical_approach'):
            if approach == 'open':
                management["pain_control"]["regional"] = "Epidural or TAP blocks"
            else:
                management["pain_control"]["regional"] = "Consider TAP blocks"
        
        # Adjust fluid management for cardiac patients
        if 'heart_failure' in patient_data.get('comorbidities', []):
            management["fluid_management"]["approach"] = "Restrictive fluid strategy"
            management["fluid_management"]["special"] = "Cardiac function monitoring"
        
        return management
    
    def _design_postop_pathway(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design postoperative pathway for gastric surgery.
        
        Args:
            patient_data: Dictionary containing patient and case data
            
        Returns:
            Dictionary with postoperative pathway recommendations
        """
        # Determine appropriate level of care
        if patient_data.get('asa_score', 2) >= 3 or patient_data.get('age', 65) > 75:
            level_of_care = "ICU"
            rationale = "High ASA score or advanced age"
            expected_los = "24-48 hours in ICU, then transfer to surgical ward"
        else:
            level_of_care = "Regular surgical ward with enhanced monitoring"
            rationale = "Standard risk profile"
            expected_los = "Not applicable"
            
        # Design ERAS-based postoperative pathway
        pathway = {
            "level_of_care": level_of_care,
            "rationale": rationale,
            "expected_los_in_icu": expected_los,
            "mobilization_plan": {
                "day0": "Bedside position",
                "day1": "Ambulation 3 times daily",
                "day2_onward": "Progressive ambulation"
            },
            "nutrition_plan": {
                "day0": "NPO",
                "day1": "Clear liquids if flatus present",
                "day2": "Liquid diet if tolerating",
                "day3_onward": "Progressive diet advancement"
            },
            "drain_management": {
                "recommendation": "Early removal when criteria met",
                "criteria": "Output < 50 mL/day and amylase normal",
                "expected_timing": "POD 3-5"
            },
            "discharge_planning": {
                "expected_los": self._estimate_hospital_los(patient_data),
                "criteria": [
                    "Tolerating at least soft diet",
                    "Pain controlled with oral medications",
                    "Ambulating independently",
                    "Normal vital signs",
                    "No untreated complications"
                ],
                "follow_up": "2 weeks postoperatively"
            }
        }
        
        # Adjust for high-risk patients
        if patient_data.get('asa_score', 2) >= 4 or 'frail' in patient_data.get('assessment_findings', []):
            pathway["mobilization_plan"]["day1"] = "Gentle assisted mobilization"
            pathway["nutrition_plan"]["day1"] = "NPO, nutrition via feeding tube if placed"
            pathway["discharge_planning"]["expected_los"] += 2
            pathway["discharge_planning"]["special"] = "Consider post-acute care needs early"
        
        return pathway
    
    def _prevent_complications(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Develop complication prevention strategies.
        
        Args:
            patient_data: Dictionary containing patient and case data
            
        Returns:
            Dictionary with complication prevention strategies
        """
        # Start with standard prevention strategies
        strategies = {
            "vte_prophylaxis": {
                "method": "Pharmacological + mechanical",
                "duration": "Until discharge",
                "special": None
            },
            "infection_prevention": {
                "antibiotics": "Standard surgical prophylaxis",
                "skin_prep": "Chlorhexidine-alcohol",
                "special": None
            },
            "anastomotic_leak_prevention": {
                "technique": "Standard two-layer hand-sewn or stapled",
                "testing": "Air leak test",
                "reinforcement": None
            },
            "pulmonary_complication_prevention": {
                "interventions": ["Incentive spirometry", "Early mobilization"],
                "special": None
            }
        }
        
        # Personalize based on patient factors
        
        # VTE prevention
        if (patient_data.get('bmi', 25) > 30 or 
            'cancer' in patient_data.get('diagnosis', '') or 
            'previous_vte' in patient_data.get('medical_history', [])):
            
            strategies["vte_prophylaxis"]["duration"] = "Extended for 28 days post-discharge"
            strategies["vte_prophylaxis"]["special"] = "High VTE risk identified"
        
        # Pulmonary complication prevention
        if ('copd' in patient_data.get('comorbidities', []) or 
            patient_data.get('smoking_status') == 'current'):
            
            strategies["pulmonary_complication_prevention"]["interventions"].extend([
                "Respiratory therapy consultation",
                "Consider postop CPAP if high risk"
            ])
            strategies["pulmonary_complication_prevention"]["special"] = "High pulmonary risk"
        
        # Anastomotic leak prevention
        if (patient_data.get('albumin', 4.0) < 3.0 or 
            patient_data.get('immunosuppressed', False) or 
            'diabetes' in patient_data.get('comorbidities', [])):
            
            strategies["anastomotic_leak_prevention"]["reinforcement"] = "Consider omental reinforcement"
            strategies["anastomotic_leak_prevention"]["special"] = "Higher leak risk identified"
        
        # High vigilance areas
        high_vigilance = ["Anastomotic integrity", "Respiratory status"]
        
        if 'diabetes' in patient_data.get('comorbidities', []):
            high_vigilance.append("Glycemic control")
            
        if patient_data.get('age', 65) > 75:
            high_vigilance.append("Delirium prevention")
        
        strategies["high_vigilance_areas"] = high_vigilance
        
        return strategies
    
    def _calculate_expected_outcomes(self, patient_data: Dict[str, Any], 
                                    base_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate expected surgical outcomes based on patient factors.
        
        Args:
            patient_data: Dictionary containing patient and case data
            base_analysis: Base FLOT analysis results
            
        Returns:
            Dictionary with expected outcomes
        """
        # Start with baseline expected outcomes
        outcomes = {
            "mortality_risk": {
                "30_day": 0.02,  # 2% baseline
                "90_day": 0.04   # 4% baseline
            },
            "major_morbidity_risk": 0.15,  # 15% baseline
            "expected_los": 7,    # 7 days baseline
            "readmission_risk": 0.10,  # 10% baseline
            "specific_complications": {
                "anastomotic_leak": 0.05,  # 5% baseline
                "pneumonia": 0.08,         # 8% baseline
                "surgical_site_infection": 0.10,  # 10% baseline
                "ileus": 0.12              # 12% baseline
            }
        }
        
        # Adjust based on patient factors
        risk_adjustment = self._calculate_risk_adjustment(patient_data)
        
        # Apply risk adjustments
        outcomes["mortality_risk"]["30_day"] = min(0.15, outcomes["mortality_risk"]["30_day"] * risk_adjustment)
        outcomes["mortality_risk"]["90_day"] = min(0.20, outcomes["mortality_risk"]["90_day"] * risk_adjustment)
        outcomes["major_morbidity_risk"] = min(0.40, outcomes["major_morbidity_risk"] * risk_adjustment)
        outcomes["expected_los"] = max(5, outcomes["expected_los"] + (risk_adjustment - 1) * 3)
        outcomes["readmission_risk"] = min(0.30, outcomes["readmission_risk"] * risk_adjustment)
        
        # Adjust specific complications
        for complication in outcomes["specific_complications"]:
            outcomes["specific_complications"][complication] = min(
                0.25, 
                outcomes["specific_complications"][complication] * risk_adjustment
            )
        
        # Add confidence intervals
        outcomes["confidence_intervals"] = {
            "mortality_30_day": [
                max(0.01, outcomes["mortality_risk"]["30_day"] - 0.01),
                min(0.20, outcomes["mortality_risk"]["30_day"] + 0.02)
            ],
            "major_morbidity": [
                max(0.05, outcomes["major_morbidity_risk"] - 0.05),
                min(0.50, outcomes["major_morbidity_risk"] + 0.10)
            ],
            "expected_los": [
                max(4, outcomes["expected_los"] - 2),
                outcomes["expected_los"] + 4
            ]
        }
        
        return outcomes
    
    def _calculate_risk_adjustment(self, patient_data: Dict[str, Any]) -> float:
        """
        Calculate risk adjustment factor based on patient characteristics.
        
        Args:
            patient_data: Dictionary containing patient and case data
            
        Returns:
            Float representing risk multiplier (1.0 = baseline risk)
        """
        risk_factor = 1.0
        
        # Age adjustment
        age = patient_data.get('age', 65)
        if age > 75:
            risk_factor += 0.3
        elif age > 65:
            risk_factor += 0.1
        
        # ASA score adjustment
        asa = patient_data.get('asa_score', 2)
        if asa >= 4:
            risk_factor += 0.5
        elif asa == 3:
            risk_factor += 0.2
        
        # Comorbidity adjustment
        comorbidities = patient_data.get('comorbidities', [])
        if 'diabetes' in comorbidities:
            risk_factor += 0.1
        if 'copd' in comorbidities:
            risk_factor += 0.2
        if 'heart_failure' in comorbidities:
            risk_factor += 0.3
        if 'chronic_kidney_disease' in comorbidities:
            risk_factor += 0.2
        
        # Nutritional status adjustment
        albumin = patient_data.get('lab_values', {}).get('albumin', 4.0)
        if albumin < 3.0:
            risk_factor += 0.3
        elif albumin < 3.5:
            risk_factor += 0.1
        
        # Procedure complexity adjustment
        if patient_data.get('surgical_approach') == 'open':
            risk_factor += 0.1
        
        if (procedure := patient_data.get('recommended_procedure', '')) == 'total gastrectomy':
            risk_factor += 0.2
        
        # Emergency surgery has substantially higher risk
        if patient_data.get('urgency') == 'emergency':
            risk_factor += 0.5
        
        return risk_factor
    
    def _get_evidence_based_recommendations(self, patient_data: Dict[str, Any], 
                                           base_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate evidence-based recommendations for surgical management.
        
        Args:
            patient_data: Dictionary containing patient and case data
            base_analysis: Base FLOT analysis results
            
        Returns:
            List of evidence-based recommendations with sources
        """
        recommendations = []
        
        # FLOT protocol recommendation
        recommendations.append({
            "recommendation": "Complete FLOT protocol (4 cycles) before surgery",
            "evidence_level": "Level 1",
            "source": "Al-Batran et al. NEJM 2019",
            "applicable": base_analysis.get('flot_recommendation', {}).get('applicable', True)
        })
        
        # Surgical approach recommendation
        recommendations.append({
            "recommendation": "Laparoscopic approach for distal gastrectomy in suitable patients",
            "evidence_level": "Level 1",
            "source": "Kim et al. Lancet Oncol 2016",
            "applicable": patient_data.get('surgical_approach') == 'laparoscopic'
        })
        
        # D2 lymphadenectomy recommendation
        recommendations.append({
            "recommendation": "D2 lymphadenectomy for advanced gastric cancer",
            "evidence_level": "Level 1",
            "source": "Songun et al. Lancet Oncol 2010",
            "applicable": True
        })
        
        # Enhanced recovery pathway
        recommendations.append({
            "recommendation": "Enhanced recovery protocol for gastric cancer surgery",
            "evidence_level": "Level 2",
            "source": "Mortensen et al. Br J Surg 2014",
            "applicable": True
        })
        
        # Nutritional support recommendation
        if patient_data.get('lab_values', {}).get('albumin', 4.0) < 3.5:
            recommendations.append({
                "recommendation": "Preoperative immunonutrition for 7 days",
                "evidence_level": "Level 2",
                "source": "Zheng et al. Surgery 2007",
                "applicable": True
            })
        
        # VTE prophylaxis recommendation
        recommendations.append({
            "recommendation": "Extended VTE prophylaxis for 28 days after major cancer surgery",
            "evidence_level": "Level 2",
            "source": "Bergqvist et al. NEJM 2002",
            "applicable": True
        })
        
        return recommendations
    
    def _estimate_hospital_los(self, patient_data: Dict[str, Any]) -> int:
        """
        Estimate hospital length of stay based on patient factors.
        
        Args:
            patient_data: Dictionary containing patient and case data
            
        Returns:
            Integer representing expected length of stay in days
        """
        # Baseline LOS for gastric surgery
        base_los = 7
        
        # Adjust for age
        if patient_data.get('age', 65) > 75:
            base_los += 2
        elif patient_data.get('age', 65) > 65:
            base_los += 1
        
        # Adjust for comorbidities
        comorbidities = patient_data.get('comorbidities', [])
        if 'diabetes' in comorbidities:
            base_los += 1
        if 'copd' in comorbidities or 'heart_failure' in comorbidities:
            base_los += 2
        
        # Adjust for procedure complexity
        if patient_data.get('surgical_approach') == 'open':
            base_los += 1
        
        if patient_data.get('recommended_procedure', '') == 'total gastrectomy':
            base_los += 2
        
        # Adjust for ASA score
        if patient_data.get('asa_score', 2) >= 3:
            base_los += 2
        
        # Emergency surgery
        if patient_data.get('urgency') == 'emergency':
            base_los += 3
        
        # Laparoscopic approach shortens stay
        if patient_data.get('surgical_approach') == 'laparoscopic':
            base_los = max(5, base_los - 2)
        
        # Enhanced recovery protocol shortens stay
        base_los = max(5, base_los - 1)
        
        return base_los
