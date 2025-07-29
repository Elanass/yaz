"""
Precision Decision Engine
Combines impact analysis with statistical prediction models
"""

from typing import Dict, List, Any

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
        """Compute MCDA score combining adjusted risk and confidence"""
        # Lower adjusted_risk is better; invert for scoring
        risk_score = 1 - option.get('adjusted_risk', 1)
        confidence = option.get('confidence', 0)
        w = self.criteria_weights
        score = risk_score * w['risk_score'] + confidence * w['confidence']
        return max(0.0, min(score, 1.0))
