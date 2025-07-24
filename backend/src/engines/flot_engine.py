"""
FLOT Protocol Decision Engine
Fluorouracil, Leucovorin, Oxaliplatin, and Docetaxel perioperative chemotherapy
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import structlog

logger = structlog.get_logger(__name__)

class FLOTEngine:
    """
    FLOT Protocol Engine for perioperative chemotherapy recommendations
    
    Provides evidence-based recommendations for:
    - FLOT eligibility assessment
    - Dosing and scheduling
    - Neoadjuvant vs adjuvant timing
    - Toxicity monitoring
    - Response assessment
    """
    
    def __init__(self):
        self.engine_name = "flot"
        self.engine_version = "1.8.0"
        self.evidence_base = "FLOT4-AIO Trial, ESMO Guidelines 2023"
        
        # Standard FLOT dosing (per cycle)
        self.standard_dosing = {
            "fluorouracil": "2600 mg/m2 IV continuous infusion 24h",
            "leucovorin": "200 mg/m2 IV over 2h",
            "oxaliplatin": "85 mg/m2 IV over 2h",
            "docetaxel": "50 mg/m2 IV over 1h"
        }
        
    async def process_decision(
        self,
        patient_id: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        include_alternatives: bool = True,
        confidence_threshold: float = 0.75
    ) -> Dict[str, Any]:
        """Process FLOT protocol decision for gastric cancer treatment"""
        
        start_time = datetime.now()
        
        try:
            # Validate input parameters
            self._validate_parameters(parameters)
            
            # Assess FLOT eligibility
            eligibility_score, eligibility_factors = await self._assess_flot_eligibility(parameters)
            
            # Generate primary FLOT recommendation
            primary_recommendation = await self._generate_flot_recommendation(
                eligibility_score, parameters, context
            )
            
            # Calculate confidence metrics
            confidence_metrics = await self._calculate_confidence(
                parameters, primary_recommendation, context
            )
            
            # Generate alternative protocols if requested
            alternatives = []
            if include_alternatives:
                alternatives = await self._generate_alternative_protocols(
                    eligibility_score, parameters, confidence_threshold
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
                "eligibility_score": float(eligibility_score),
                "eligibility_factors": eligibility_factors,
                "alternatives": alternatives,
                "evidence_summary": evidence_summary,
                "toxicity_assessment": await self._assess_toxicity_risk(parameters),
                "monitoring_plan": await self._generate_monitoring_plan(primary_recommendation),
                "warnings": await self._check_contraindications(parameters),
                "data_completeness": self._calculate_data_completeness(parameters),
                "processing_time_ms": processing_time,
                "confidence_metrics": confidence_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Error in FLOT decision processing", 
                        patient_id=patient_id, error=str(e))
            raise

    async def _assess_flot_eligibility(self, parameters: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Assess patient eligibility for FLOT protocol"""
        
        factors = {}
        
        # Disease stage eligibility
        tumor_stage = parameters.get("tumor_stage", "")
        factors["disease_stage"] = self._score_disease_stage(tumor_stage)
        
        # Performance status
        ecog_score = parameters.get("ecog_score", 3)
        factors["performance_status"] = self._score_performance_status(ecog_score)
        
        # Age factor
        age = parameters.get("age", 80)
        factors["age_factor"] = self._score_age_for_chemotherapy(age)
        
        # Organ function
        organ_function = self._assess_organ_function(parameters)
        factors.update(organ_function)
        
        # Comorbidities
        comorbidities = parameters.get("comorbidities", [])
        factors["comorbidity_burden"] = self._score_comorbidities_for_chemo(comorbidities)
        
        # Histology
        histology = parameters.get("histology", "unknown")
        factors["histology"] = self._score_histology_for_flot(histology)
        
        # HER2 status (if available)
        her2_status = parameters.get("biomarkers", {}).get("her2", "unknown")
        factors["her2_status"] = self._score_her2_status(her2_status)
        
        # Calculate weighted eligibility score
        weights = {
            "disease_stage": 0.25,
            "performance_status": 0.20,
            "age_factor": 0.15,
            "renal_function": 0.10,
            "hepatic_function": 0.10,
            "cardiac_function": 0.05,
            "comorbidity_burden": 0.10,
            "histology": 0.03,
            "her2_status": 0.02
        }
        
        eligibility_score = sum(factors[factor] * weights.get(factor, 0) for factor in factors)
        
        return eligibility_score, factors

    def _score_disease_stage(self, tumor_stage: str) -> float:
        """Score disease stage for FLOT eligibility"""
        stage_scores = {
            # Resectable disease - primary indication
            "T2N0M0": 0.85,  # Borderline indication
            "T2N+M0": 0.95,  # Clear indication
            "T3N0M0": 0.90,  # Clear indication
            "T3N+M0": 0.95,  # Strong indication
            "T4aN0M0": 0.85, # Clear indication
            "T4aN+M0": 0.90, # Strong indication
            "T4bN0M0": 0.70, # Borderline resectable
            "T4bN+M0": 0.75, # Borderline resectable
            
            # Stage groupings
            "IB": 0.60,      # T2N0M0 - borderline
            "II": 0.85,      # Various combinations
            "III": 0.95,     # Strong indication
            "IIIA": 0.95,
            "IIIB": 0.90,
            "IIIC": 0.85,
            
            # Not indicated
            "IA": 0.30,      # T1N0M0 - surgery first
            "IV": 0.20,      # Metastatic - palliative intent
            "M1": 0.15       # Metastatic
        }
        
        # Check for specific patterns
        stage_clean = tumor_stage.upper().replace(" ", "")
        
        # Direct match
        if stage_clean in stage_scores:
            return stage_scores[stage_clean]
        
        # Pattern matching
        if "M1" in stage_clean:
            return 0.15
        
        if "T4B" in stage_clean:
            return 0.70
        
        if "T3" in stage_clean or "T4A" in stage_clean:
            return 0.90
        
        if "T2" in stage_clean and ("N1" in stage_clean or "N2" in stage_clean or "N3" in stage_clean):
            return 0.90
        
        if "T1" in stage_clean:
            return 0.30
        
        return 0.50  # Default for unclear staging

    def _score_performance_status(self, ecog: int) -> float:
        """Score ECOG performance status for chemotherapy"""
        ecog_scores = {
            0: 1.0,   # Fully active - excellent candidate
            1: 0.9,   # Restricted strenuous activity - good candidate
            2: 0.5,   # Ambulatory >50% of time - borderline
            3: 0.2,   # Ambulatory <50% of time - poor candidate
            4: 0.1    # Bedridden - contraindicated
        }
        return ecog_scores.get(ecog, 0.3)

    def _score_age_for_chemotherapy(self, age: int) -> float:
        """Score age for chemotherapy tolerance"""
        if age < 65:
            return 1.0
        elif age < 70:
            return 0.9
        elif age < 75:
            return 0.8
        elif age < 80:
            return 0.6
        else:
            return 0.4

    def _assess_organ_function(self, parameters: Dict[str, Any]) -> Dict[str, float]:
        """Assess organ function for chemotherapy eligibility"""
        
        lab_values = parameters.get("lab_values", {})
        comorbidities = parameters.get("comorbidities", [])
        
        # Renal function (creatinine clearance)
        creatinine = lab_values.get("creatinine_mg_dl", 1.0)
        age = parameters.get("age", 70)
        
        # Cockcroft-Gault estimate (simplified)
        estimated_ccr = (140 - age) * 72 / creatinine  # Simplified formula
        
        if estimated_ccr >= 60:
            renal_score = 1.0
        elif estimated_ccr >= 45:
            renal_score = 0.8
        elif estimated_ccr >= 30:
            renal_score = 0.5
        else:
            renal_score = 0.2
        
        # Hepatic function
        bilirubin = lab_values.get("total_bilirubin_mg_dl", 1.0)
        alt = lab_values.get("alt_u_l", 30)
        
        if bilirubin <= 1.5 and alt <= 100:
            hepatic_score = 1.0
        elif bilirubin <= 3.0 and alt <= 200:
            hepatic_score = 0.7
        elif bilirubin <= 5.0 and alt <= 300:
            hepatic_score = 0.4
        else:
            hepatic_score = 0.2
        
        # Cardiac function
        if "heart_failure" in comorbidities or "ejection_fraction_reduced" in comorbidities:
            cardiac_score = 0.5
        elif "coronary_artery_disease" in comorbidities:
            cardiac_score = 0.7
        else:
            cardiac_score = 1.0
        
        return {
            "renal_function": renal_score,
            "hepatic_function": hepatic_score,
            "cardiac_function": cardiac_score
        }

    def _score_comorbidities_for_chemo(self, comorbidities: List[str]) -> float:
        """Score comorbidity burden for chemotherapy"""
        if not comorbidities:
            return 1.0
        
        # High-risk comorbidities for chemotherapy
        high_risk_conditions = {
            "severe_heart_failure", "severe_copd", "cirrhosis", 
            "active_infection", "immunodeficiency", "severe_neuropathy"
        }
        
        # Moderate-risk comorbidities
        moderate_risk_conditions = {
            "diabetes", "hypertension", "mild_copd", "chronic_kidney_disease",
            "previous_chemotherapy", "peripheral_neuropathy"
        }
        
        high_risk_count = sum(1 for c in comorbidities if c.lower() in high_risk_conditions)
        moderate_risk_count = sum(1 for c in comorbidities if c.lower() in moderate_risk_conditions)
        
        # Calculate score
        score = 1.0 - (high_risk_count * 0.3) - (moderate_risk_count * 0.1)
        return max(score, 0.2)

    def _score_histology_for_flot(self, histology: str) -> float:
        """Score histology for FLOT effectiveness"""
        histology_scores = {
            "adenocarcinoma": 1.0,        # Primary indication
            "signet_ring": 0.9,           # Good response
            "poorly_differentiated": 0.9,  # Good response
            "mucinous": 0.8,              # Moderate response
            "linitis_plastica": 0.7,      # Variable response
            "mixed": 0.8,                 # Variable
            "unknown": 0.7                # Default
        }
        return histology_scores.get(histology.lower(), 0.7)

    def _score_her2_status(self, her2_status: str) -> float:
        """Score HER2 status (affects treatment choice)"""
        her2_scores = {
            "positive": 0.8,    # Consider trastuzumab addition
            "negative": 1.0,    # Standard FLOT
            "unknown": 0.9      # Default to standard
        }
        return her2_scores.get(her2_status.lower(), 0.9)

    async def _generate_flot_recommendation(
        self, 
        eligibility_score: float, 
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate primary FLOT recommendation"""
        
        tumor_stage = parameters.get("tumor_stage", "")
        age = parameters.get("age", 70)
        ecog_score = parameters.get("ecog_score", 2)
        her2_status = parameters.get("biomarkers", {}).get("her2", "unknown")
        
        # Determine if FLOT is recommended
        if eligibility_score >= 0.8:
            recommendation_status = "strongly_recommended"
            recommendation_rationale = "Excellent candidate for FLOT protocol with high likelihood of benefit"
        elif eligibility_score >= 0.6:
            recommendation_status = "recommended"
            recommendation_rationale = "Good candidate for FLOT protocol with expected clinical benefit"
        elif eligibility_score >= 0.4:
            recommendation_status = "consider_with_caution"
            recommendation_rationale = "Borderline candidate - consider benefits vs risks, possible dose modifications"
        else:
            recommendation_status = "not_recommended"
            recommendation_rationale = "Poor candidate for FLOT - consider alternative approaches"
        
        # Determine treatment approach
        if "M1" in tumor_stage:
            treatment_intent = "palliative"
            cycles_preop = 0
            cycles_postop = 6
        elif eligibility_score >= 0.7:
            treatment_intent = "perioperative"
            cycles_preop = 4
            cycles_postop = 4
        else:
            treatment_intent = "adjuvant_only"
            cycles_preop = 0
            cycles_postop = 6
        
        # Determine dosing modifications
        dose_modifications = self._determine_dose_modifications(parameters, eligibility_score)
        
        # HER2-positive modifications
        additional_agents = []
        if her2_status.lower() == "positive":
            additional_agents.append({
                "agent": "trastuzumab",
                "dosing": "8 mg/kg loading dose, then 6 mg/kg every 3 weeks",
                "rationale": "HER2-positive disease benefits from trastuzumab addition"
            })
        
        return {
            "recommendation_status": recommendation_status,
            "recommendation_rationale": recommendation_rationale,
            "treatment_intent": treatment_intent,
            "protocol_name": "FLOT",
            "cycles_preoperative": cycles_preop,
            "cycles_postoperative": cycles_postop,
            "cycle_frequency": "every_2_weeks",
            "total_duration_weeks": (cycles_preop + cycles_postop) * 2,
            "dosing": self._get_dosing_recommendation(dose_modifications),
            "dose_modifications": dose_modifications,
            "additional_agents": additional_agents,
            "surgery_timing": self._determine_surgery_timing(cycles_preop),
            "response_assessment": self._get_response_assessment_plan(cycles_preop),
            "supportive_care": self._get_supportive_care_recommendations(parameters)
        }

    def _determine_dose_modifications(self, parameters: Dict[str, Any], eligibility_score: float) -> Dict[str, Any]:
        """Determine if dose modifications are needed"""
        
        modifications = {
            "fluorouracil": "100%",  # Standard dose
            "leucovorin": "100%",
            "oxaliplatin": "100%",
            "docetaxel": "100%"
        }
        
        age = parameters.get("age", 70)
        ecog_score = parameters.get("ecog_score", 0)
        comorbidities = parameters.get("comorbidities", [])
        lab_values = parameters.get("lab_values", {})
        
        # Age-based modifications
        if age >= 75:
            modifications["docetaxel"] = "80%"
            modifications["oxaliplatin"] = "85%"
        elif age >= 70:
            modifications["docetaxel"] = "90%"
        
        # Performance status modifications
        if ecog_score >= 2:
            modifications["fluorouracil"] = "75%"
            modifications["docetaxel"] = "75%"
        
        # Organ function modifications
        creatinine = lab_values.get("creatinine_mg_dl", 1.0)
        if creatinine > 1.5:
            modifications["oxaliplatin"] = "75%"
        
        bilirubin = lab_values.get("total_bilirubin_mg_dl", 1.0)
        if bilirubin > 1.5:
            modifications["docetaxel"] = "75%"
        
        # Comorbidity-based modifications
        if "neuropathy" in comorbidities:
            modifications["oxaliplatin"] = "75%"
        
        if "liver_disease" in comorbidities:
            modifications["docetaxel"] = "75%"
            modifications["fluorouracil"] = "85%"
        
        return modifications

    def _get_dosing_recommendation(self, modifications: Dict[str, Any]) -> Dict[str, str]:
        """Get final dosing recommendation with modifications"""
        
        base_doses = {
            "fluorouracil": 2600,    # mg/m2
            "leucovorin": 200,       # mg/m2
            "oxaliplatin": 85,       # mg/m2
            "docetaxel": 50          # mg/m2
        }
        
        final_dosing = {}
        
        for drug, base_dose in base_doses.items():
            modification_percent = float(modifications[drug].rstrip('%')) / 100
            final_dose = base_dose * modification_percent
            
            if drug == "fluorouracil":
                final_dosing[drug] = f"{final_dose:.0f} mg/m² IV continuous infusion over 24 hours"
            elif drug == "leucovorin":
                final_dosing[drug] = f"{final_dose:.0f} mg/m² IV over 2 hours (day 1)"
            elif drug == "oxaliplatin":
                final_dosing[drug] = f"{final_dose:.0f} mg/m² IV over 2 hours (day 1)"
            elif drug == "docetaxel":
                final_dosing[drug] = f"{final_dose:.0f} mg/m² IV over 1 hour (day 1)"
        
        return final_dosing

    def _determine_surgery_timing(self, preop_cycles: int) -> Dict[str, Any]:
        """Determine optimal surgery timing"""
        if preop_cycles == 0:
            return {
                "approach": "surgery_first",
                "timing": "immediate",
                "rationale": "Direct surgical approach followed by adjuvant therapy"
            }
        else:
            surgery_week = preop_cycles * 2 + 4  # 2 weeks per cycle + 4 week break
            return {
                "approach": "neoadjuvant_first",
                "timing": f"week_{surgery_week}",
                "rationale": f"Surgery scheduled 4 weeks after completion of {preop_cycles} neoadjuvant cycles",
                "preop_restaging": "Required at week " + str(preop_cycles * 2)
            }

    def _get_response_assessment_plan(self, preop_cycles: int) -> Dict[str, Any]:
        """Get response assessment plan"""
        if preop_cycles == 0:
            return {"assessment": "not_applicable"}
        
        return {
            "baseline_imaging": "CT chest/abdomen/pelvis, EUS if indicated",
            "interim_assessment": f"After cycle {preop_cycles//2 if preop_cycles >= 4 else 2}",
            "preoperative_assessment": f"2-4 weeks after cycle {preop_cycles}",
            "response_criteria": "RECIST 1.1",
            "pathologic_assessment": "Tumor regression grade (TRG) at surgery"
        }

    def _get_supportive_care_recommendations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get supportive care recommendations"""
        
        age = parameters.get("age", 70)
        comorbidities = parameters.get("comorbidities", [])
        
        supportive_care = {
            "antiemetics": {
                "ondansetron": "8 mg IV/PO q8h PRN",
                "dexamethasone": "12 mg IV day 1 of each cycle",
                "metoclopramide": "10 mg PO TID PRN delayed nausea"
            },
            "premedications": {
                "dexamethasone": "8 mg IV 30 min before docetaxel",
                "antihistamines": "For hypersensitivity prophylaxis"
            },
            "monitoring": {
                "cbc_with_diff": "Before each cycle",
                "comprehensive_metabolic": "Before each cycle",
                "performance_status": "Each visit"
            },
            "prophylaxis": []
        }
        
        # Age-specific recommendations
        if age >= 70:
            supportive_care["prophylaxis"].append("Consider G-CSF support for neutropenia prevention")
        
        # Comorbidity-specific recommendations
        if "diabetes" in comorbidities:
            supportive_care["monitoring"]["glucose"] = "Frequent monitoring due to steroid premedication"
        
        if "neuropathy" in comorbidities:
            supportive_care["monitoring"]["neuropathy_assessment"] = "Before each cycle with dose modifications PRN"
        
        return supportive_care

    async def _generate_alternative_protocols(
        self, 
        eligibility_score: float, 
        parameters: Dict[str, Any], 
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Generate alternative chemotherapy protocols"""
        
        alternatives = []
        
        # ECF/ECX protocol
        if eligibility_score >= 0.6:
            alternatives.append({
                "protocol": "ECF",
                "confidence": min(eligibility_score * 0.85, 0.9),
                "rationale": "Alternative triplet regimen with established efficacy",
                "advantages": ["Well-established", "Oral capecitabine option"],
                "disadvantages": ["More toxic than FLOT", "Inferior efficacy vs FLOT"]
            })
        
        # Modified FLOT for elderly/frail patients
        if parameters.get("age", 70) >= 70 or eligibility_score < 0.6:
            alternatives.append({
                "protocol": "Modified_FLOT",
                "confidence": min(eligibility_score * 0.9, 0.8),
                "rationale": "Dose-reduced FLOT for elderly or frail patients",
                "advantages": ["Reduced toxicity", "Maintains efficacy"],
                "disadvantages": ["Potentially reduced efficacy"]
            })
        
        # Single-agent or doublet for poor PS
        if parameters.get("ecog_score", 2) >= 2:
            alternatives.append({
                "protocol": "Capecitabine_Oxaliplatin",
                "confidence": min(eligibility_score * 0.7, 0.7),
                "rationale": "Doublet therapy for patients unfit for triplet",
                "advantages": ["Lower toxicity", "Oral component"],
                "disadvantages": ["Reduced efficacy vs triplet"]
            })
        
        # Immunotherapy combinations (future option)
        her2_status = parameters.get("biomarkers", {}).get("her2", "unknown")
        if her2_status.lower() == "positive":
            alternatives.append({
                "protocol": "FLOT_Trastuzumab_Pertuzumab",
                "confidence": min(eligibility_score * 0.8, 0.85),
                "rationale": "Dual HER2 blockade for HER2-positive disease",
                "advantages": ["Enhanced anti-HER2 effect", "Improved pCR rates"],
                "disadvantages": ["Increased cost", "Cardiac monitoring required"]
            })
        
        return [alt for alt in alternatives if alt["confidence"] >= threshold]

    async def _assess_toxicity_risk(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Assess toxicity risk for FLOT protocol"""
        
        age = parameters.get("age", 70)
        ecog_score = parameters.get("ecog_score", 2)
        comorbidities = parameters.get("comorbidities", [])
        lab_values = parameters.get("lab_values", {})
        
        # Grade 3-4 hematologic toxicity risk
        hematologic_risk = self._calculate_hematologic_risk(age, ecog_score, comorbidities)
        
        # Neuropathy risk (oxaliplatin)
        neuropathy_risk = self._calculate_neuropathy_risk(age, comorbidities)
        
        # Diarrhea risk (fluorouracil)
        diarrhea_risk = self._calculate_diarrhea_risk(age, comorbidities)
        
        # Febrile neutropenia risk
        febrile_neutropenia_risk = self._calculate_febrile_neutropenia_risk(age, ecog_score)
        
        return {
            "overall_toxicity_risk": self._calculate_overall_toxicity_risk(
                hematologic_risk, neuropathy_risk, diarrhea_risk, febrile_neutropenia_risk
            ),
            "hematologic_toxicity": hematologic_risk,
            "peripheral_neuropathy": neuropathy_risk,
            "severe_diarrhea": diarrhea_risk,
            "febrile_neutropenia": febrile_neutropenia_risk,
            "specific_monitoring": self._get_toxicity_monitoring_plan(parameters)
        }

    def _calculate_hematologic_risk(self, age: int, ecog: int, comorbidities: List[str]) -> str:
        """Calculate hematologic toxicity risk"""
        risk_score = 0
        
        if age >= 70:
            risk_score += 2
        elif age >= 65:
            risk_score += 1
        
        if ecog >= 2:
            risk_score += 2
        
        if "bone_marrow_disorder" in comorbidities:
            risk_score += 3
        
        if "previous_chemotherapy" in comorbidities:
            risk_score += 1
        
        if risk_score <= 1:
            return "low"
        elif risk_score <= 3:
            return "moderate"
        else:
            return "high"

    def _calculate_neuropathy_risk(self, age: int, comorbidities: List[str]) -> str:
        """Calculate peripheral neuropathy risk"""
        risk_score = 0
        
        if age >= 70:
            risk_score += 1
        
        if "diabetes" in comorbidities:
            risk_score += 2
        
        if "neuropathy" in comorbidities or "peripheral_neuropathy" in comorbidities:
            risk_score += 3
        
        if "alcohol_use" in comorbidities:
            risk_score += 1
        
        if risk_score == 0:
            return "low"
        elif risk_score <= 2:
            return "moderate"
        else:
            return "high"

    def _calculate_diarrhea_risk(self, age: int, comorbidities: List[str]) -> str:
        """Calculate severe diarrhea risk"""
        risk_score = 0
        
        if age >= 75:
            risk_score += 1
        
        if "inflammatory_bowel_disease" in comorbidities:
            risk_score += 3
        
        if "previous_abdominal_radiation" in comorbidities:
            risk_score += 2
        
        if "dihydropyrimidine_dehydrogenase_deficiency" in comorbidities:
            risk_score += 3
        
        if risk_score == 0:
            return "low"
        elif risk_score <= 2:
            return "moderate"
        else:
            return "high"

    def _calculate_febrile_neutropenia_risk(self, age: int, ecog: int) -> str:
        """Calculate febrile neutropenia risk"""
        risk_score = 0
        
        if age >= 65:
            risk_score += 2
        
        if ecog >= 2:
            risk_score += 2
        
        # FLOT has baseline 10-15% risk
        base_risk = 1
        total_risk = base_risk + risk_score
        
        if total_risk <= 1:
            return "low"
        elif total_risk <= 3:
            return "moderate"
        else:
            return "high"

    def _calculate_overall_toxicity_risk(self, *risk_levels) -> str:
        """Calculate overall toxicity risk"""
        high_count = sum(1 for risk in risk_levels if risk == "high")
        moderate_count = sum(1 for risk in risk_levels if risk == "moderate")
        
        if high_count >= 2:
            return "high"
        elif high_count == 1 or moderate_count >= 3:
            return "moderate"
        else:
            return "low"

    def _get_toxicity_monitoring_plan(self, parameters: Dict[str, Any]) -> Dict[str, str]:
        """Get toxicity-specific monitoring plan"""
        
        monitoring = {
            "cbc_frequency": "Before each cycle, day 10 of first 2 cycles",
            "neuropathy_assessment": "Before each cycle using CTCAE grading",
            "diarrhea_education": "Patient education on early intervention strategies",
            "temperature_monitoring": "Daily temperature logs during treatment"
        }
        
        comorbidities = parameters.get("comorbidities", [])
        
        if "diabetes" in comorbidities:
            monitoring["neuropathy_enhanced"] = "Enhanced neuropathy monitoring with neurologic exam"
        
        if "kidney_disease" in comorbidities:
            monitoring["renal_function"] = "Creatinine monitoring before each cycle"
        
        return monitoring

    async def _generate_monitoring_plan(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive monitoring plan"""
        
        treatment_intent = recommendation.get("treatment_intent", "perioperative")
        preop_cycles = recommendation.get("cycles_preoperative", 4)
        
        return {
            "pretreatment_assessment": {
                "imaging": "CT chest/abdomen/pelvis, consider EUS",
                "cardiac_function": "ECHO or MUGA if indicated",
                "pulmonary_function": "PFTs if respiratory comorbidities",
                "labs": "CBC, CMP, LFTs, PT/INR, baseline tumor markers"
            },
            "during_treatment": {
                "cycle_assessments": "Before each cycle: CBC, CMP, PS assessment",
                "toxicity_monitoring": "CTCAE grading of all toxicities",
                "dose_modifications": "Per protocol dose modification guidelines"
            },
            "response_assessment": {
                "imaging_schedule": f"After cycle {preop_cycles//2} and {preop_cycles}" if preop_cycles > 0 else "After cycles 3 and 6",
                "tumor_markers": "CEA, CA 19-9 if elevated at baseline",
                "clinical_assessment": "Performance status and symptom evaluation"
            },
            "post_treatment": {
                "surgical_timing": "4-6 weeks after completion of neoadjuvant cycles",
                "pathologic_response": "Tumor regression grade assessment",
                "adjuvant_planning": "Continuation based on pathologic response"
            }
        }

    async def _generate_evidence_summary(
        self, 
        recommendation: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate evidence summary supporting FLOT recommendation"""
        
        evidence = []
        
        # Primary FLOT4-AIO evidence
        evidence.append({
            "evidence_id": "FLOT4_AIO_2019",
            "level": "1",
            "description": "FLOT superior to ECF in perioperative setting for resectable gastric cancer",
            "citation": "Al-Batran et al. Lancet Oncol 2019",
            "strength": "strong",
            "applicability": "high",
            "key_findings": "Improved pathologic complete response rate (16% vs 6%)"
        })
        
        # Toxicity data
        evidence.append({
            "evidence_id": "FLOT_TOXICITY_2020",
            "level": "2",
            "description": "FLOT toxicity profile manageable with appropriate monitoring",
            "citation": "Homann et al. J Clin Oncol 2020",
            "strength": "moderate",
            "applicability": "high",
            "key_findings": "Grade 3-4 toxicity rate 77% but reversible"
        })
        
        # HER2-positive evidence if applicable
        her2_status = parameters.get("biomarkers", {}).get("her2", "unknown")
        if her2_status.lower() == "positive":
            evidence.append({
                "evidence_id": "HER2_FLOT_2023",
                "level": "2",
                "description": "Trastuzumab addition to FLOT improves outcomes in HER2+ disease",
                "citation": "Wagner et al. ESMO 2023",
                "strength": "moderate",
                "applicability": "high",
                "key_findings": "Improved pCR rate with dual HER2 blockade"
            })
        
        return evidence

    async def _check_contraindications(self, parameters: Dict[str, Any]) -> List[str]:
        """Check for contraindications and warnings"""
        warnings = []
        
        age = parameters.get("age", 70)
        ecog_score = parameters.get("ecog_score", 2)
        comorbidities = parameters.get("comorbidities", [])
        lab_values = parameters.get("lab_values", {})
        
        # Absolute contraindications
        if ecog_score >= 3:
            warnings.append("ECOG PS ≥3 is contraindication to FLOT - consider palliative care")
        
        if "severe_heart_failure" in comorbidities:
            warnings.append("Severe heart failure contraindication - cardio-oncology consultation required")
        
        # Relative contraindications/warnings
        if age >= 75:
            warnings.append("Age ≥75 years - consider dose modifications and enhanced monitoring")
        
        creatinine = lab_values.get("creatinine_mg_dl", 1.0)
        if creatinine > 2.0:
            warnings.append("Severe renal impairment - dose modifications required")
        
        bilirubin = lab_values.get("total_bilirubin_mg_dl", 1.0)
        if bilirubin > 3.0:
            warnings.append("Severe hepatic impairment - dose modifications or alternative regimen")
        
        if "neuropathy" in comorbidities:
            warnings.append("Pre-existing neuropathy - consider oxaliplatin dose reduction")
        
        if "dihydropyrimidine_dehydrogenase_deficiency" in comorbidities:
            warnings.append("DPD deficiency - fluorouracil contraindicated")
        
        tumor_stage = parameters.get("tumor_stage", "")
        if "M1" in tumor_stage:
            warnings.append("Metastatic disease - palliative intent only")
        
        return warnings

    def _validate_parameters(self, parameters: Dict[str, Any]):
        """Validate input parameters"""
        required_fields = ["tumor_stage", "age", "ecog_score"]
        
        for field in required_fields:
            if field not in parameters:
                raise ValueError(f"Missing required parameter: {field}")
        
        # Validate age
        age = parameters.get("age")
        if not isinstance(age, (int, float)) or age < 0 or age > 120:
            raise ValueError("Age must be between 0 and 120")
        
        # Validate ECOG score
        ecog_score = parameters.get("ecog_score")
        if ecog_score not in [0, 1, 2, 3, 4]:
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
            "tumor_stage", "age", "ecog_score", "histology", "biomarkers",
            "comorbidities", "lab_values"
        ]
        
        available_fields = sum(1 for field in important_fields if parameters.get(field) is not None)
        return available_fields / len(important_fields)

    async def _calculate_confidence(
        self,
        parameters: Dict[str, Any],
        recommendation: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """Calculate confidence metrics for FLOT recommendation"""
        
        # Data completeness factor
        data_completeness = self._calculate_data_completeness(parameters)
        
        # Evidence strength factor (strong for FLOT)
        evidence_strength = 0.90  # Strong evidence from FLOT4-AIO
        
        # Clinical appropriateness factor
        clinical_appropriateness = self._assess_clinical_appropriateness(parameters, recommendation)
        
        # Patient suitability factor
        patient_suitability = self._assess_patient_suitability_for_chemo(parameters)
        
        # Calculate overall confidence
        confidence_factors = {
            "data_completeness": data_completeness,
            "evidence_strength": evidence_strength,
            "clinical_appropriateness": clinical_appropriateness,
            "patient_suitability": patient_suitability
        }
        
        # Weighted combination
        weights = {
            "data_completeness": 0.20,
            "evidence_strength": 0.40,
            "clinical_appropriateness": 0.25,
            "patient_suitability": 0.15
        }
        
        overall_confidence = sum(
            confidence_factors[factor] * weights[factor] 
            for factor in confidence_factors
        )
        
        confidence_factors["overall_confidence"] = overall_confidence
        
        return confidence_factors

    def _assess_clinical_appropriateness(self, parameters: Dict[str, Any], recommendation: Dict[str, Any]) -> float:
        """Assess clinical appropriateness of FLOT recommendation"""
        appropriateness = 0.8  # Base appropriateness
        
        tumor_stage = parameters.get("tumor_stage", "")
        recommendation_status = recommendation.get("recommendation_status", "")
        
        # Stage-specific appropriateness
        if "III" in tumor_stage and recommendation_status == "strongly_recommended":
            appropriateness += 0.1
        elif "II" in tumor_stage and recommendation_status in ["recommended", "strongly_recommended"]:
            appropriateness += 0.05
        elif "IV" in tumor_stage and recommendation_status == "not_recommended":
            appropriateness += 0.1
        
        return min(appropriateness, 1.0)

    def _assess_patient_suitability_for_chemo(self, parameters: Dict[str, Any]) -> float:
        """Assess patient suitability for chemotherapy"""
        age = parameters.get("age", 70)
        ecog_score = parameters.get("ecog_score", 2)
        comorbidities = parameters.get("comorbidities", [])
        
        suitability = 1.0
        
        # Age factor
        if age > 80:
            suitability -= 0.3
        elif age > 75:
            suitability -= 0.15
        elif age > 70:
            suitability -= 0.05
        
        # Performance status factor
        if ecog_score >= 3:
            suitability -= 0.5
        elif ecog_score == 2:
            suitability -= 0.2
        elif ecog_score == 1:
            suitability -= 0.05
        
        # Comorbidity factor
        if len(comorbidities) > 4:
            suitability -= 0.3
        elif len(comorbidities) > 2:
            suitability -= 0.15
        elif len(comorbidities) > 0:
            suitability -= 0.05
        
        return max(suitability, 0.2)
