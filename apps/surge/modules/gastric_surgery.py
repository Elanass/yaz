"""Gastric Surgery Module
Independent cell module for gastric cancer surgery analysis and gastrectomy procedures.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from apps.surge.core.models.medical import (
    HistologyType,
    MetastasisStage,
    NodeStage,
    TumorStage,
)


class GastrectomyType(str, Enum):
    """Types of gastrectomy procedures."""

    TOTAL = "total_gastrectomy"
    SUBTOTAL = "subtotal_gastrectomy"
    PROXIMAL = "proximal_gastrectomy"
    PYLORUS_PRESERVING = "pylorus_preserving_gastrectomy"
    ENDOSCOPIC = "endoscopic_resection"
    PALLIATIVE = "palliative_bypass"


class SurgicalApproach(str, Enum):
    """Surgical approach methods."""

    OPEN = "open"
    LAPAROSCOPIC = "laparoscopic"
    ROBOTIC = "robotic"
    ENDOSCOPIC = "endoscopic"


class ResectionStatus(str, Enum):
    """Surgical resection completeness."""

    R0 = "R0"  # Complete resection
    R1 = "R1"  # Microscopic residual
    R2 = "R2"  # Macroscopic residual


class GastricSurgeryCase(BaseModel):
    """Gastric surgery case model."""

    # Patient identifiers
    patient_id: str = Field(..., description="Unique patient identifier")
    case_id: str = Field(..., description="Unique case identifier")
    age: int | None = Field(None, ge=0, le=120, description="Patient age")
    asa_score: int | None = Field(
        None, ge=1, le=5, description="ASA physical status classification"
    )

    # Tumor characteristics
    tumor_stage: TumorStage = Field(..., description="T stage")
    node_stage: NodeStage = Field(..., description="N stage")
    metastasis_stage: MetastasisStage = Field(..., description="M stage")
    histology: HistologyType = Field(..., description="Histological type")
    tumor_size_mm: float | None = Field(None, ge=0, description="Tumor size in mm")
    tumor_location: str | None = Field(None, description="Primary tumor location")

    # Surgery details
    gastrectomy_type: GastrectomyType = Field(..., description="Type of gastrectomy")
    surgical_approach: SurgicalApproach = Field(..., description="Surgical approach")
    surgery_date: datetime | None = Field(None, description="Date of surgery")
    surgeon: str | None = Field(None, description="Primary surgeon")

    # Outcomes
    resection_status: ResectionStatus | None = Field(
        None, description="Resection status"
    )
    lymph_nodes_harvested: int | None = Field(
        None, ge=0, description="Number of lymph nodes harvested"
    )
    lymph_nodes_positive: int | None = Field(
        None, ge=0, description="Number of positive lymph nodes"
    )
    operative_time_minutes: int | None = Field(
        None, ge=0, description="Operative time in minutes"
    )
    blood_loss_ml: float | None = Field(
        None, ge=0, description="Estimated blood loss in mL"
    )

    # Complications
    complications: list[str] = Field(
        default=[], description="Post-operative complications"
    )
    clavien_dindo_grade: int | None = Field(
        None, ge=0, le=5, description="Clavien-Dindo classification"
    )
    hospital_stay_days: int | None = Field(
        None, ge=0, description="Length of hospital stay"
    )

    # Pathology
    pathology_report: str | None = Field(None, description="Pathology report summary")

    # Margins
    proximal_margin_cm: float | None = Field(
        None, ge=0, description="Proximal margin in cm"
    )
    distal_margin_cm: float | None = Field(
        None, ge=0, description="Distal margin in cm"
    )

    # Lymph node examination
    lymph_nodes_examined: int | None = Field(
        None, ge=0, description="Total lymph nodes examined"
    )
    lymphadenectomy_type: str | None = Field(
        None, description="Type of lymphadenectomy (e.g., D2)"
    )

    class Config:
        use_enum_values = True


class GastricSurgeryAnalysis(BaseModel):
    """Analysis results for gastric surgery case."""

    case_id: str = Field(..., description="Case identifier")
    analysis_timestamp: datetime = Field(default_factory=datetime.now)

    # Risk assessment
    surgical_risk_score: float = Field(
        ..., ge=0, le=100, description="Surgical risk score"
    )
    risk_category: str = Field(..., description="Risk category")
    risk_factors: list[str] = Field(default=[], description="Identified risk factors")

    # Recommendations
    recommended_approach: SurgicalApproach = Field(
        ..., description="Recommended surgical approach"
    )
    recommended_gastrectomy: GastrectomyType = Field(
        ..., description="Recommended gastrectomy type"
    )
    alternative_approaches: list[str] = Field(
        default=[], description="Alternative surgical options"
    )

    # Predictions
    predicted_operative_time: int | None = Field(
        None, description="Predicted operative time (minutes)"
    )
    predicted_blood_loss: float | None = Field(
        None, description="Predicted blood loss (mL)"
    )
    predicted_hospital_stay: int | None = Field(
        None, description="Predicted hospital stay (days)"
    )

    # Quality metrics
    lymph_node_target: int = Field(default=15, description="Target lymph node harvest")
    resection_quality_score: float | None = Field(
        None, ge=0, le=100, description="Resection quality score"
    )

    # Confidence
    confidence_score: float = Field(..., ge=0, le=1, description="Analysis confidence")
    evidence_level: str = Field(..., description="Evidence quality level")

    class Config:
        use_enum_values = True


class GastricSurgeryModule:
    """Independent module for gastric surgery analysis and decision support."""

    def __init__(self) -> None:
        self.version = "1.0.0"
        self.name = "Gastric Surgery Module"

    def analyze_case(self, case: GastricSurgeryCase) -> GastricSurgeryAnalysis:
        """Analyze gastric surgery case and provide recommendations."""
        # Calculate surgical risk score
        risk_score = self._calculate_surgical_risk(case)
        risk_category = self._classify_risk(risk_score)
        risk_factors = self._identify_risk_factors(case)

        # Determine optimal surgical approach
        recommended_approach = self._recommend_surgical_approach(case)
        recommended_gastrectomy = self._recommend_gastrectomy_type(case)
        alternatives = self._get_alternative_approaches(case)

        # Make predictions
        predicted_time = self._predict_operative_time(case)
        predicted_blood_loss = self._predict_blood_loss(case)
        predicted_stay = self._predict_hospital_stay(case)

        # Calculate quality metrics
        ln_target = self._get_lymph_node_target(case)
        quality_score = self._calculate_resection_quality(case)

        # Determine confidence
        confidence = self._calculate_confidence(case)
        evidence_level = self._assess_evidence_level(case)

        return GastricSurgeryAnalysis(
            case_id=case.case_id,
            surgical_risk_score=risk_score,
            risk_category=risk_category,
            risk_factors=risk_factors,
            recommended_approach=recommended_approach,
            recommended_gastrectomy=recommended_gastrectomy,
            alternative_approaches=alternatives,
            predicted_operative_time=predicted_time,
            predicted_blood_loss=predicted_blood_loss,
            predicted_hospital_stay=predicted_stay,
            lymph_node_target=ln_target,
            resection_quality_score=quality_score,
            confidence_score=confidence,
            evidence_level=evidence_level,
        )

    def _calculate_surgical_risk(self, case: GastricSurgeryCase) -> float:
        """Calculate surgical risk score based on case characteristics."""
        risk_score = 0.0

        # T stage risk contribution
        t_stage_risk = {
            "T1": 5,
            "T1a": 5,
            "T1b": 10,
            "T2": 20,
            "T3": 40,
            "T4": 60,
            "T4a": 60,
            "T4b": 80,
        }
        risk_score += t_stage_risk.get(case.tumor_stage.value, 30)

        # N stage risk contribution
        n_stage_risk = {"N0": 5, "N1": 15, "N2": 30, "N3": 50, "N3a": 50, "N3b": 70}
        risk_score += n_stage_risk.get(case.node_stage.value, 25)

        # M stage risk contribution
        if case.metastasis_stage.value.startswith("M1"):
            risk_score += 40

        # Histology risk contribution
        if case.histology == HistologyType.SIGNET_RING:
            risk_score += 15

        # Tumor size risk contribution
        if case.tumor_size_mm:
            if case.tumor_size_mm > 50:
                risk_score += 10
            elif case.tumor_size_mm > 30:
                risk_score += 5

        return min(risk_score, 100.0)

    def _classify_risk(self, risk_score: float) -> str:
        """Classify risk based on score."""
        if risk_score <= 25:
            return "Low"
        if risk_score <= 50:
            return "Moderate"
        if risk_score <= 75:
            return "High"
        return "Very High"

    def _identify_risk_factors(self, case: GastricSurgeryCase) -> list[str]:
        """Identify specific risk factors."""
        factors = []

        if case.tumor_stage.value in ["T3", "T4", "T4a", "T4b"]:
            factors.append("Advanced T stage")

        if case.node_stage.value in ["N2", "N3", "N3a", "N3b"]:
            factors.append("Extensive nodal involvement")

        if case.metastasis_stage.value.startswith("M1"):
            factors.append("Distant metastases")

        if case.histology == HistologyType.SIGNET_RING:
            factors.append("Signet ring cell histology")

        if case.tumor_size_mm and case.tumor_size_mm > 50:
            factors.append("Large tumor size (>5cm)")

        return factors

    def _recommend_surgical_approach(
        self, case: GastricSurgeryCase
    ) -> SurgicalApproach:
        """Recommend optimal surgical approach."""
        # Early stage tumors - consider minimally invasive
        if case.tumor_stage.value in ["T1", "T1a", "T1b", "T2"]:
            if case.node_stage.value in ["N0", "N1"]:
                return SurgicalApproach.LAPAROSCOPIC

        # Advanced tumors - open approach may be preferred
        if case.tumor_stage.value in ["T4", "T4a", "T4b"]:
            return SurgicalApproach.OPEN

        # Moderate cases - laparoscopic if experienced team
        return SurgicalApproach.LAPAROSCOPIC

    def _recommend_gastrectomy_type(self, case: GastricSurgeryCase) -> GastrectomyType:
        """Recommend type of gastrectomy."""
        # Very early tumors - consider endoscopic resection
        if case.tumor_stage.value in ["T1a"] and case.node_stage.value == "N0":
            if case.tumor_size_mm and case.tumor_size_mm <= 20:
                return GastrectomyType.ENDOSCOPIC

        # Location-based recommendations would need tumor location
        # For now, use staging-based approach
        if case.tumor_stage.value in [
            "T1",
            "T1a",
            "T1b",
            "T2",
        ] and case.node_stage.value in ["N0", "N1"]:
            return GastrectomyType.SUBTOTAL

        # Advanced cases typically need total gastrectomy
        return GastrectomyType.TOTAL

    def _get_alternative_approaches(self, case: GastricSurgeryCase) -> list[str]:
        """Get alternative surgical approaches."""
        alternatives = []

        if case.tumor_stage.value in ["T1", "T2"]:
            alternatives.extend(["Robotic-assisted", "Single-port laparoscopy"])

        if case.tumor_stage.value in ["T3", "T4"]:
            alternatives.extend(["Neoadjuvant therapy + surgery", "Open conversion"])

        return alternatives

    def _predict_operative_time(self, case: GastricSurgeryCase) -> int | None:
        """Predict operative time in minutes."""
        base_time = 180  # Base 3 hours

        # Adjust for approach
        if case.surgical_approach == SurgicalApproach.LAPAROSCOPIC:
            base_time += 30
        elif case.surgical_approach == SurgicalApproach.ROBOTIC:
            base_time += 60

        # Adjust for complexity
        if case.tumor_stage.value in ["T3", "T4", "T4a", "T4b"]:
            base_time += 60

        if case.node_stage.value in ["N2", "N3", "N3a", "N3b"]:
            base_time += 30

        return base_time

    def _predict_blood_loss(self, case: GastricSurgeryCase) -> float | None:
        """Predict blood loss in mL."""
        base_loss = 200.0

        # Adjust for approach
        if case.surgical_approach == SurgicalApproach.OPEN:
            base_loss += 150
        elif case.surgical_approach == SurgicalApproach.LAPAROSCOPIC:
            base_loss += 50

        # Adjust for complexity
        if case.tumor_stage.value in ["T3", "T4", "T4a", "T4b"]:
            base_loss += 200

        return base_loss

    def _predict_hospital_stay(self, case: GastricSurgeryCase) -> int | None:
        """Predict hospital stay in days."""
        base_stay = 7

        # Adjust for approach
        if case.surgical_approach == SurgicalApproach.LAPAROSCOPIC:
            base_stay -= 2
        elif case.surgical_approach == SurgicalApproach.OPEN:
            base_stay += 2

        # Adjust for complexity
        if case.tumor_stage.value in ["T3", "T4", "T4a", "T4b"]:
            base_stay += 3

        return max(base_stay, 3)

    def _get_lymph_node_target(self, case: GastricSurgeryCase) -> int:
        """Get target lymph node harvest count."""
        # Standard recommendation is 15+ lymph nodes
        if case.tumor_stage.value in ["T3", "T4", "T4a", "T4b"]:
            return 20  # Higher target for advanced tumors
        return 15

    def _calculate_resection_quality(self, case: GastricSurgeryCase) -> float | None:
        """Calculate resection quality score if surgery completed."""
        if not case.resection_status or not case.lymph_nodes_harvested:
            return None

        quality_score = 0.0

        # R0 resection gets full points
        if case.resection_status == ResectionStatus.R0:
            quality_score += 50
        elif case.resection_status == ResectionStatus.R1:
            quality_score += 30
        else:  # R2
            quality_score += 10

        # Lymph node harvest adequacy
        target_ln = self._get_lymph_node_target(case)
        if case.lymph_nodes_harvested >= target_ln:
            quality_score += 50
        else:
            quality_score += (case.lymph_nodes_harvested / target_ln) * 50

        return min(quality_score, 100.0)

    def _calculate_confidence(self, case: GastricSurgeryCase) -> float:
        """Calculate confidence in analysis."""
        confidence = 0.8  # Base confidence

        # Increase confidence if more data available
        if case.tumor_size_mm:
            confidence += 0.05
        if case.tumor_location:
            confidence += 0.05
        if case.pathology_report:
            confidence += 0.1

        return min(confidence, 1.0)

    def _assess_evidence_level(self, case: GastricSurgeryCase) -> str:
        """Assess quality of evidence for recommendations."""
        # Based on data completeness and staging
        if case.tumor_stage.value in ["T1", "T2"] and case.node_stage.value in [
            "N0",
            "N1",
        ]:
            return "High"  # Well-established guidelines for early disease
        if case.tumor_stage.value in ["T3"] and case.node_stage.value in ["N1", "N2"]:
            return "Moderate"  # Good evidence for intermediate disease
        return "Limited"  # Less evidence for advanced/complex cases

    @staticmethod
    def analyze_gastrectomy_case(case: GastricSurgeryCase) -> dict[str, Any]:
        """Analyze gastrectomy case returning structured KPIs:
        R0 rate, nodes retrieved, LOS, complications (Clavien-Dindo),
        30/90-day mortality, and readmission flags.
        """
        analysis = {
            "case_id": case.case_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "procedure_type": case.gastrectomy_type,
            "surgical_approach": case.surgical_approach,
        }

        # R0 Resection Rate Analysis
        r0_analysis = {
            "resection_status": case.resection_status,
            "r0_achieved": case.resection_status == "R0",
            "margin_assessment": {
                "proximal_margin_cm": case.proximal_margin_cm,
                "distal_margin_cm": case.distal_margin_cm,
                "adequate_margins": (
                    case.proximal_margin_cm
                    and case.proximal_margin_cm >= 5.0
                    and case.distal_margin_cm
                    and case.distal_margin_cm >= 2.0
                )
                if case.proximal_margin_cm and case.distal_margin_cm
                else None,
            },
        }
        analysis["r0_analysis"] = r0_analysis

        # Lymph Node Retrieval Analysis
        ln_analysis = {
            "total_nodes_examined": case.lymph_nodes_examined,
            "positive_nodes": case.lymph_nodes_positive,
            "adequate_harvest": case.lymph_nodes_examined >= 15
            if case.lymph_nodes_examined
            else None,
            "d2_dissection_performed": case.lymphadenectomy_type == "D2",
            "nodal_ratio": (
                case.lymph_nodes_positive / case.lymph_nodes_examined
                if case.lymph_nodes_examined and case.lymph_nodes_positive
                else None
            ),
        }
        analysis["lymph_node_analysis"] = ln_analysis

        # Length of Stay (LOS) Prediction
        base_los = {
            "total_gastrectomy": 8,
            "subtotal_gastrectomy": 6,
            "proximal_gastrectomy": 5,
            "pylorus_preserving_gastrectomy": 5,
            "endoscopic_resection": 2,
            "palliative_bypass": 7,
        }.get(case.gastrectomy_type, 7)

        # Adjust for approach
        approach_modifier = {
            "laparoscopic": -1,
            "robotic": -1,
            "open": 0,
            "endoscopic": -3,
        }.get(case.surgical_approach, 0)

        # Adjust for complications
        complication_modifier = 0
        if case.complications:
            complication_modifier += len(case.complications)
        if case.clavien_dindo_grade and case.clavien_dindo_grade >= 3:
            complication_modifier += 2

        predicted_los = max(base_los + approach_modifier + complication_modifier, 1)

        los_analysis = {
            "predicted_los_days": predicted_los,
            "factors": {
                "base_procedure": base_los,
                "approach_modifier": approach_modifier,
                "complication_modifier": complication_modifier,
            },
            "eras_eligible": case.surgical_approach in ["laparoscopic", "robotic"],
        }
        analysis["length_of_stay"] = los_analysis

        # Clavien-Dindo Complication Analysis
        def classify_complications(complications: list[str]) -> dict[str, int]:
            """Classify complications by Clavien-Dindo grade."""
            classification = {"I": 0, "II": 0, "III": 0, "IV": 0, "V": 0}

            # Simple classification based on complication type
            high_grade_complications = [
                "anastomotic_leak",
                "bleeding_requiring_surgery",
                "organ_failure",
                "sepsis",
                "pulmonary_embolism",
                "stroke",
                "cardiac_arrest",
            ]

            moderate_complications = [
                "pneumonia",
                "wound_infection",
                "urinary_retention",
                "ileus",
                "bleeding_requiring_transfusion",
            ]

            for comp in complications:
                comp_lower = comp.lower()
                if any(hgc in comp_lower for hgc in high_grade_complications):
                    if "death" in comp_lower or "mortality" in comp_lower:
                        classification["V"] += 1
                    elif "icu" in comp_lower or "ventilator" in comp_lower:
                        classification["IV"] += 1
                    else:
                        classification["III"] += 1
                elif any(mc in comp_lower for mc in moderate_complications):
                    classification["II"] += 1
                else:
                    classification["I"] += 1

            return classification

        complications = case.complications or []
        clavien_dindo = classify_complications(complications)

        # Calculate overall grade (highest grade present)
        overall_grade = "0"
        for grade in ["V", "IV", "III", "II", "I"]:
            if clavien_dindo[grade] > 0:
                overall_grade = grade
                break

        complication_analysis = {
            "clavien_dindo_classification": clavien_dindo,
            "overall_grade": overall_grade,
            "major_complications": clavien_dindo["III"]
            + clavien_dindo["IV"]
            + clavien_dindo["V"],
            "any_complication": sum(clavien_dindo.values()) > 0,
            "complication_details": complications,
        }
        analysis["complications"] = complication_analysis

        # Mortality Risk Assessment (30/90-day)
        def calculate_mortality_risk(case: GastricSurgeryCase) -> dict[str, float]:
            """Calculate 30 and 90-day mortality risk."""
            # Base risk by procedure type
            base_risk_30 = {
                "total_gastrectomy": 0.05,
                "subtotal_gastrectomy": 0.02,
                "proximal_gastrectomy": 0.03,
                "pylorus_preserving_gastrectomy": 0.02,
                "endoscopic_resection": 0.001,
                "palliative_bypass": 0.08,
            }.get(case.gastrectomy_type, 0.03)

            # Risk modifiers
            risk_multiplier = 1.0

            # Age factor
            if case.age and case.age > 75:
                risk_multiplier *= 2.0
            elif case.age and case.age > 65:
                risk_multiplier *= 1.5

            # ASA score factor
            if case.asa_score and case.asa_score >= 4:
                risk_multiplier *= 3.0
            elif case.asa_score and case.asa_score >= 3:
                risk_multiplier *= 1.8

            # Approach factor
            if case.surgical_approach == "open":
                risk_multiplier *= 1.3
            elif case.surgical_approach in ["laparoscopic", "robotic"]:
                risk_multiplier *= 0.8

            # Comorbidity factor
            if case.major_comorbidities and len(case.major_comorbidities) >= 3:
                risk_multiplier *= 2.0
            elif case.major_comorbidities and len(case.major_comorbidities) >= 1:
                risk_multiplier *= 1.4

            risk_30_day = min(base_risk_30 * risk_multiplier, 0.3)  # Cap at 30%
            risk_90_day = min(risk_30_day * 1.8, 0.5)  # 90-day typically 1.5-2x 30-day

            return {
                "risk_30_day": round(risk_30_day, 4),
                "risk_90_day": round(risk_90_day, 4),
                "risk_category": (
                    "low"
                    if risk_30_day < 0.02
                    else "moderate"
                    if risk_30_day < 0.08
                    else "high"
                ),
            }

        mortality_analysis = calculate_mortality_risk(case)
        analysis["mortality_risk"] = mortality_analysis

        # Readmission Risk Assessment
        def calculate_readmission_risk(case: GastricSurgeryCase) -> dict[str, Any]:
            """Calculate 30-day readmission risk."""
            base_risk = 0.15  # 15% baseline for gastrectomy

            risk_factors = []
            risk_multiplier = 1.0

            # Age
            if case.age and case.age > 70:
                risk_factors.append("advanced_age")
                risk_multiplier *= 1.3

            # Complications
            if case.complications:
                risk_factors.append("postoperative_complications")
                risk_multiplier *= 1.5

            # Comorbidities
            if case.major_comorbidities and len(case.major_comorbidities) >= 2:
                risk_factors.append("multiple_comorbidities")
                risk_multiplier *= 1.4

            # Procedure complexity
            if case.gastrectomy_type == "total_gastrectomy":
                risk_factors.append("total_gastrectomy")
                risk_multiplier *= 1.2

            # Social factors (if available)
            if hasattr(case, "social_support") and not case.social_support:
                risk_factors.append("limited_social_support")
                risk_multiplier *= 1.3

            final_risk = min(base_risk * risk_multiplier, 0.6)  # Cap at 60%

            return {
                "readmission_risk_30_day": round(final_risk, 3),
                "risk_factors": risk_factors,
                "risk_category": (
                    "low"
                    if final_risk < 0.1
                    else "moderate"
                    if final_risk < 0.25
                    else "high"
                ),
                "mitigation_strategies": [
                    "Enhanced discharge planning",
                    "Early post-op follow-up",
                    "Patient education reinforcement",
                    "Home health services consideration",
                ]
                if final_risk > 0.2
                else ["Standard discharge planning"],
            }

        readmission_analysis = calculate_readmission_risk(case)
        analysis["readmission_risk"] = readmission_analysis

        # Overall Quality Metrics Summary
        quality_metrics = {
            "r0_resection_achieved": r0_analysis["r0_achieved"],
            "adequate_lymphadenectomy": ln_analysis["adequate_harvest"],
            "minimally_invasive_approach": case.surgical_approach
            in ["laparoscopic", "robotic"],
            "no_major_complications": complication_analysis["major_complications"] == 0,
            "low_mortality_risk": mortality_analysis["risk_category"] == "low",
            "low_readmission_risk": readmission_analysis["risk_category"] == "low",
        }

        # Calculate composite quality score
        quality_score = sum(1 for metric in quality_metrics.values() if metric is True)
        total_metrics = len([v for v in quality_metrics.values() if v is not None])
        quality_percentage = (
            (quality_score / total_metrics * 100) if total_metrics > 0 else 0
        )

        analysis["quality_metrics"] = {
            "individual_metrics": quality_metrics,
            "composite_score": quality_score,
            "total_possible": total_metrics,
            "quality_percentage": round(quality_percentage, 1),
            "quality_grade": (
                "Excellent"
                if quality_percentage >= 85
                else "Good"
                if quality_percentage >= 70
                else "Acceptable"
                if quality_percentage >= 55
                else "Needs Improvement"
            ),
        }

        # Recommendations based on analysis
        recommendations = []

        if not r0_analysis["r0_achieved"]:
            recommendations.append("Consider adjuvant therapy consultation")

        if not ln_analysis["adequate_harvest"]:
            recommendations.append("Review lymphadenectomy technique for future cases")

        if complication_analysis["major_complications"] > 0:
            recommendations.append("Multidisciplinary review of complications")

        if mortality_analysis["risk_category"] == "high":
            recommendations.append("Enhanced perioperative monitoring")

        if readmission_analysis["risk_category"] == "high":
            recommendations.append(
                "Consider extended observation or enhanced discharge planning"
            )

        analysis["recommendations"] = recommendations

        return analysis


# Descriptive analytics functions
def analyze_gastric_surgery_cohort(cases: list[GastricSurgeryCase]) -> dict[str, Any]:
    """Analyze a cohort of gastric surgery cases - descriptive analytics."""
    if not cases:
        return {"error": "No cases provided"}

    # Basic demographics
    total_cases = len(cases)

    # Staging distribution
    t_stages = [case.tumor_stage.value for case in cases]
    n_stages = [case.node_stage.value for case in cases]
    m_stages = [case.metastasis_stage.value for case in cases]

    # Histology distribution
    histologies = [case.histology.value for case in cases]

    # Surgical approaches
    approaches = [
        case.surgical_approach.value for case in cases if case.surgical_approach
    ]
    gastrectomy_types = [case.gastrectomy_type.value for case in cases]

    # Outcomes (for completed cases)
    completed_cases = [case for case in cases if case.resection_status]
    r0_resections = sum(
        1 for case in completed_cases if case.resection_status == ResectionStatus.R0
    )

    # Complications
    complications = []
    for case in cases:
        complications.extend(case.complications)

    return {
        "cohort_summary": {
            "total_cases": total_cases,
            "completed_surgeries": len(completed_cases),
        },
        "staging_distribution": {
            "t_stages": {stage: t_stages.count(stage) for stage in set(t_stages)},
            "n_stages": {stage: n_stages.count(stage) for stage in set(n_stages)},
            "m_stages": {stage: m_stages.count(stage) for stage in set(m_stages)},
        },
        "histology_distribution": {
            hist: histologies.count(hist) for hist in set(histologies)
        },
        "surgical_approaches": {app: approaches.count(app) for app in set(approaches)},
        "gastrectomy_types": {
            gt: gastrectomy_types.count(gt) for gt in set(gastrectomy_types)
        },
        "outcomes": {
            "r0_resection_rate": r0_resections / len(completed_cases)
            if completed_cases
            else 0,
            "complication_rate": len([c for c in cases if c.complications])
            / total_cases,
        },
        "complications": {
            comp: complications.count(comp) for comp in set(complications)
        },
    }


# Analytic functions for optimization
def optimize_surgical_scheduling(cases: list[GastricSurgeryCase]) -> dict[str, Any]:
    """Optimize surgical scheduling based on case complexity."""
    if not cases:
        return {"error": "No cases provided"}

    # Categorize cases by complexity
    low_complexity = []
    moderate_complexity = []
    high_complexity = []

    module = GastricSurgeryModule()

    for case in cases:
        analysis = module.analyze_case(case)
        if analysis.surgical_risk_score <= 30:
            low_complexity.append((case, analysis))
        elif analysis.surgical_risk_score <= 60:
            moderate_complexity.append((case, analysis))
        else:
            high_complexity.append((case, analysis))

    # Optimize scheduling
    schedule = []

    # Schedule high complexity cases early in the week
    for case, analysis in high_complexity:
        schedule.append(
            {
                "case_id": case.case_id,
                "recommended_day": "Monday/Tuesday",
                "estimated_duration": analysis.predicted_operative_time,
                "priority": "High",
                "team_requirement": "Senior surgeon + full team",
            }
        )

    # Schedule moderate complexity cases mid-week
    for case, analysis in moderate_complexity:
        schedule.append(
            {
                "case_id": case.case_id,
                "recommended_day": "Wednesday/Thursday",
                "estimated_duration": analysis.predicted_operative_time,
                "priority": "Moderate",
                "team_requirement": "Experienced surgeon",
            }
        )

    # Schedule low complexity cases when convenient
    for case, analysis in low_complexity:
        schedule.append(
            {
                "case_id": case.case_id,
                "recommended_day": "Any day",
                "estimated_duration": analysis.predicted_operative_time,
                "priority": "Low",
                "team_requirement": "Standard team",
            }
        )

    return {
        "schedule_optimization": schedule,
        "complexity_distribution": {
            "low_complexity": len(low_complexity),
            "moderate_complexity": len(moderate_complexity),
            "high_complexity": len(high_complexity),
        },
        "resource_recommendations": {
            "peak_or_utilization": "Monday-Tuesday",
            "optimal_case_mix": "Mix high/low complexity daily",
            "team_planning": "Ensure senior coverage early week",
        },
    }


# Standalone functions for easier import and testing
def analyze_gastrectomy_case(case: GastricSurgeryCase) -> dict[str, Any]:
    """Standalone function to analyze gastrectomy case."""
    module = GastricSurgeryModule()
    return module.analyze_gastrectomy_case(case)


def create_sample_case(patient_id: str = "P001") -> GastricSurgeryCase:
    """Create a sample gastric surgery case for testing."""
    return GastricSurgeryCase(
        patient_id=patient_id,
        case_id=f"C{patient_id[1:]}",
        age=45,
        tumor_stage=TumorStage.T1,
        node_stage=NodeStage.N0,
        metastasis_stage=MetastasisStage.M0,
        histology=HistologyType.ADENOCARCINOMA,
        gastrectomy_type=GastrectomyType.SUBTOTAL,
        surgical_approach=SurgicalApproach.LAPAROSCOPIC,
        resection_status=ResectionStatus.R0,
        lymph_nodes_harvested=15,
        lymph_nodes_positive=0,
        proximal_margin_cm=3.5,
        distal_margin_cm=4.2,
    )
