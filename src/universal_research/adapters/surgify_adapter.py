"""
Surgify Adapter - Maps current case data to universal research engine
Preserves existing data structure while enabling research capabilities
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.models.database_models import Case, Patient, User


class SurgifyAdapter:
    """
    Adapter that bridges existing Surgify case data with universal research engine
    Maintains backward compatibility while enabling research analysis
    """

    def __init__(self, db_session: Session = None):
        self.db_session = db_session or next(get_db())

    def map_case_to_research_data(self, case: Case) -> Dict[str, Any]:
        """
        Maps existing Surgify case to universal research format
        Preserves all existing fields while adding research metadata
        """
        return {
            # Existing case data (unchanged)
            "case_id": case.case_number,
            "patient_id": case.patient.patient_id if case.patient else None,
            "procedure_type": case.procedure_type,
            "diagnosis": case.diagnosis,
            "status": case.status,
            "risk_score": case.risk_score,
            "scheduled_date": case.scheduled_date,
            "actual_start": case.actual_start,
            "actual_end": case.actual_end,
            "notes": case.notes,
            # Enhanced research fields (new)
            "research_metadata": {
                "domain": "surgery",
                "specialty": self._extract_specialty(case.procedure_type),
                "complexity_score": self._calculate_complexity(case),
                "outcome_category": self._categorize_outcome(case),
                "research_eligible": True,
            },
            # Patient data (existing, enhanced for research)
            "patient_demographics": {
                "age": case.patient.age if case.patient else None,
                "gender": case.patient.gender if case.patient else None,
                "bmi": case.patient.bmi if case.patient else None,
                "medical_history": case.patient.medical_history
                if case.patient
                else None,
            },
            # Surgeon data (existing)
            "provider_info": {
                "surgeon_id": case.surgeon.username if case.surgeon else None,
                "surgeon_role": case.surgeon.role if case.surgeon else None,
            },
        }

    def get_research_cohort(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts research cohort from existing Surgify cases
        Uses current database queries, enhanced for research analysis
        """
        query = self.db_session.query(Case).join(Patient).join(User)

        # Apply existing filtering logic (preserved)
        if criteria.get("procedure_type"):
            query = query.filter(Case.procedure_type == criteria["procedure_type"])

        if criteria.get("date_range"):
            start_date, end_date = criteria["date_range"]
            query = query.filter(Case.created_at.between(start_date, end_date))

        if criteria.get("status"):
            query = query.filter(Case.status == criteria["status"])

        # Convert to research format
        cases = query.all()
        return [self.map_case_to_research_data(case) for case in cases]

    def enhance_existing_case_data(self, case_id: str) -> Dict[str, Any]:
        """
        Enhances existing case with research insights
        Preserves original case structure, adds research analysis
        """
        case = self.db_session.query(Case).filter(Case.case_number == case_id).first()
        if not case:
            return None

        base_data = self.map_case_to_research_data(case)

        # Add research enhancements (new capabilities)
        base_data["research_insights"] = {
            "similar_cases_count": self._count_similar_cases(case),
            "outcome_probability": self._predict_outcome_probability(case),
            "risk_factors": self._analyze_risk_factors(case),
            "evidence_level": self._assess_evidence_level(case),
        }

        return base_data

    def _extract_specialty(self, procedure_type: str) -> str:
        """Extract surgical specialty from procedure type"""
        if not procedure_type:
            return "general"

        specialty_map = {
            "cardiac": "cardiothoracic",
            "neuro": "neurosurgery",
            "ortho": "orthopedic",
            "gastro": "gastroenterology",
            "uro": "urology",
        }

        for key, specialty in specialty_map.items():
            if key.lower() in procedure_type.lower():
                return specialty

        return "general"

    def _calculate_complexity(self, case: Case) -> float:
        """Calculate procedure complexity score"""
        score = 1.0  # Base complexity

        if case.risk_score:
            score += case.risk_score * 0.5

        if case.patient and case.patient.age:
            if case.patient.age > 70:
                score += 0.3
            elif case.patient.age < 18:
                score += 0.2

        if case.patient and case.patient.medical_history:
            # Count comorbidities in medical history
            comorbidity_indicators = ["diabetes", "hypertension", "cardiac", "renal"]
            history_lower = case.patient.medical_history.lower()
            comorbidity_count = sum(
                1 for indicator in comorbidity_indicators if indicator in history_lower
            )
            score += comorbidity_count * 0.1

        return min(score, 5.0)  # Cap at 5.0

    def _categorize_outcome(self, case: Case) -> str:
        """Categorize case outcome for research"""
        if case.status == "completed":
            if case.risk_score and case.risk_score < 0.3:
                return "excellent"
            elif case.risk_score and case.risk_score < 0.7:
                return "good"
            else:
                return "acceptable"
        elif case.status == "cancelled":
            return "cancelled"
        else:
            return "pending"

    def _count_similar_cases(self, case: Case) -> int:
        """Count similar cases for comparative analysis"""
        similar_query = self.db_session.query(Case).filter(
            Case.procedure_type == case.procedure_type, Case.id != case.id
        )
        return similar_query.count()

    def _predict_outcome_probability(self, case: Case) -> float:
        """Predict outcome probability based on similar cases"""
        if not case.risk_score:
            return 0.75  # Default probability

        return max(0.1, min(0.95, 1.0 - case.risk_score))

    def _analyze_risk_factors(self, case: Case) -> List[str]:
        """Analyze risk factors from case data"""
        risk_factors = []

        if case.patient:
            if case.patient.age and case.patient.age > 70:
                risk_factors.append("advanced_age")

            if case.patient.bmi and case.patient.bmi > 30:
                risk_factors.append("obesity")

            if case.patient.medical_history:
                history_lower = case.patient.medical_history.lower()
                if "diabetes" in history_lower:
                    risk_factors.append("diabetes")
                if "cardiac" in history_lower:
                    risk_factors.append("cardiac_history")
                if "hypertension" in history_lower:
                    risk_factors.append("hypertension")

        if case.risk_score and case.risk_score > 0.7:
            risk_factors.append("high_risk_procedure")

        return risk_factors

    def _assess_evidence_level(self, case: Case) -> str:
        """Assess evidence level for research purposes"""
        similar_count = self._count_similar_cases(case)

        if similar_count > 100:
            return "high"
        elif similar_count > 20:
            return "moderate"
        elif similar_count > 5:
            return "low"
        else:
            return "case_study"
