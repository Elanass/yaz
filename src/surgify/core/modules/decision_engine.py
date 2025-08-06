"""
Surgify Decision Engine
Core decision support system for surgical procedures and planning
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class SurgicalRisk(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionEngine:
    """Core surgical decision support engine"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize decision engine"""
        self.config = config or {}
        self.version = "2.0.0"

    def assess_surgical_risk(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess surgical risk based on patient data"""
        # Simple risk calculation based on key factors
        age = patient_data.get("age", 0)
        comorbidities = len(patient_data.get("comorbidities", []))
        bmi = patient_data.get("bmi", 25)

        risk_score = 0
        risk_score += min(age / 10, 8)  # Age factor
        risk_score += comorbidities * 2  # Comorbidity factor
        risk_score += max(0, (bmi - 30) / 5)  # BMI factor

        if risk_score <= 5:
            risk_level = SurgicalRisk.LOW
        elif risk_score <= 10:
            risk_level = SurgicalRisk.MEDIUM
        elif risk_score <= 15:
            risk_level = SurgicalRisk.HIGH
        else:
            risk_level = SurgicalRisk.CRITICAL

        return {
            "risk_level": risk_level.value,
            "risk_score": round(risk_score, 2),
            "factors": {
                "age_factor": age,
                "comorbidity_count": comorbidities,
                "bmi_factor": bmi,
            },
            "recommendations": self._get_risk_recommendations(risk_level),
        }

    def recommend_procedure(
        self, patient_data: Dict[str, Any], procedure_options: List[str]
    ) -> Dict[str, Any]:
        """Recommend optimal surgical procedure"""
        risk_assessment = self.assess_surgical_risk(patient_data)

        # Simple recommendation logic
        if risk_assessment["risk_level"] == "low":
            recommended = (
                procedure_options[0] if procedure_options else "standard_approach"
            )
            approach = "minimally_invasive"
        elif risk_assessment["risk_level"] == "medium":
            recommended = (
                procedure_options[0] if procedure_options else "standard_approach"
            )
            approach = "standard"
        else:
            recommended = "conservative_management"
            approach = "high_risk_protocol"

        return {
            "recommended_procedure": recommended,
            "surgical_approach": approach,
            "confidence": 0.85,
            "rationale": f"Based on {risk_assessment['risk_level']} risk assessment",
            "alternatives": procedure_options[1:] if len(procedure_options) > 1 else [],
        }

    def optimize_scheduling(self, procedure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize surgical scheduling"""
        return {
            "optimal_time": "09:00",
            "estimated_duration": "2.5 hours",
            "required_resources": [
                "OR_1",
                "anesthesiologist",
                "surgical_nurse_x2",
                "specialized_equipment",
            ],
            "preparation_time": "30 minutes",
            "recovery_time": "1 hour",
        }

    def _get_risk_recommendations(self, risk_level: SurgicalRisk) -> List[str]:
        """Get recommendations based on risk level"""
        recommendations = {
            SurgicalRisk.LOW: [
                "Standard preoperative preparation",
                "Consider outpatient procedure",
                "Normal monitoring protocols",
            ],
            SurgicalRisk.MEDIUM: [
                "Enhanced preoperative assessment",
                "Consider inpatient monitoring",
                "Prepare for potential complications",
            ],
            SurgicalRisk.HIGH: [
                "Comprehensive preoperative workup",
                "Multidisciplinary team consultation",
                "ICU bed availability required",
            ],
            SurgicalRisk.CRITICAL: [
                "Consider non-surgical alternatives",
                "Extensive preoperative optimization",
                "High-risk consent and family discussion",
            ],
        }
        return recommendations.get(risk_level, [])
