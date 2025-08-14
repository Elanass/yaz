"""Chemo FLOT Module
Independent cell module for FLOT chemotherapy impact analysis and optimization.
"""

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from src.surge.core.models.medical import MetastasisStage, NodeStage, TumorStage


class FLOTPhase(str, Enum):
    """FLOT treatment phases."""

    PREOPERATIVE = "preoperative"
    POSTOPERATIVE = "postoperative"
    COMPLETE = "complete"
    INTERRUPTED = "interrupted"


class ResponseGrade(str, Enum):
    """Tumor response grades."""

    COMPLETE = "complete_response"  # pCR
    MAJOR = "major_response"  # >90% regression
    PARTIAL = "partial_response"  # 50-90% regression
    MINIMAL = "minimal_response"  # 10-50% regression
    STABLE = "stable_disease"  # <10% change
    PROGRESSIVE = "progressive_disease"


class ToxicityGrade(str, Enum):
    """CTCAE toxicity grades."""

    GRADE_0 = "0"  # No toxicity
    GRADE_1 = "1"  # Mild
    GRADE_2 = "2"  # Moderate
    GRADE_3 = "3"  # Severe
    GRADE_4 = "4"  # Life-threatening
    GRADE_5 = "5"  # Death


class FLOTCase(BaseModel):
    """FLOT chemotherapy case model."""

    # Patient identifiers
    patient_id: str = Field(..., description="Unique patient identifier")
    case_id: str = Field(..., description="Unique case identifier")

    # Pre-treatment staging
    initial_t_stage: TumorStage = Field(..., description="Initial T stage")
    initial_n_stage: NodeStage = Field(..., description="Initial N stage")
    initial_m_stage: MetastasisStage = Field(..., description="Initial M stage")

    # Post-treatment staging (if available)
    post_t_stage: TumorStage | None = Field(None, description="Post-FLOT T stage")
    post_n_stage: NodeStage | None = Field(None, description="Post-FLOT N stage")
    post_m_stage: MetastasisStage | None = Field(None, description="Post-FLOT M stage")

    # FLOT treatment details
    planned_cycles: int = Field(..., ge=1, le=8, description="Planned FLOT cycles")
    completed_cycles: int = Field(..., ge=0, le=8, description="Completed FLOT cycles")
    phase: FLOTPhase = Field(..., description="Treatment phase")

    # Timing
    flot_start_date: date | None = Field(None, description="FLOT start date")
    flot_end_date: date | None = Field(None, description="FLOT end date")
    surgery_date: date | None = Field(None, description="Surgery date")

    # Response assessment
    radiological_response: ResponseGrade | None = Field(
        None, description="Radiological response"
    )
    pathological_response: ResponseGrade | None = Field(
        None, description="Pathological response"
    )
    tumor_regression_grade: int | None = Field(
        None, ge=0, le=5, description="TRG score (0-5)"
    )

    # Toxicity
    max_toxicity_grade: ToxicityGrade | None = Field(
        None, description="Maximum toxicity grade"
    )
    dose_reductions: int = Field(
        default=0, ge=0, description="Number of dose reductions"
    )
    treatment_delays: int = Field(
        default=0, ge=0, description="Number of treatment delays"
    )

    # Laboratory values
    baseline_albumin: float | None = Field(
        None, ge=1.0, le=6.0, description="Baseline albumin (g/dL)"
    )
    post_flot_albumin: float | None = Field(
        None, ge=1.0, le=6.0, description="Post-FLOT albumin (g/dL)"
    )
    baseline_hemoglobin: float | None = Field(
        None, ge=5.0, le=18.0, description="Baseline Hgb (g/dL)"
    )
    post_flot_hemoglobin: float | None = Field(
        None, ge=5.0, le=18.0, description="Post-FLOT Hgb (g/dL)"
    )

    # Performance status
    baseline_ecog: int | None = Field(
        None, ge=0, le=4, description="Baseline ECOG score"
    )
    post_flot_ecog: int | None = Field(
        None, ge=0, le=4, description="Post-FLOT ECOG score"
    )

    # Weight and nutrition
    baseline_weight_kg: float | None = Field(
        None, ge=30.0, le=200.0, description="Baseline weight (kg)"
    )
    post_flot_weight_kg: float | None = Field(
        None, ge=30.0, le=200.0, description="Post-FLOT weight (kg)"
    )

    # Complications
    hospitalizations: int = Field(
        default=0, ge=0, description="Hospitalizations during FLOT"
    )
    infections: int = Field(default=0, ge=0, description="Infections during FLOT")

    class Config:
        use_enum_values = True


class FLOTAnalysis(BaseModel):
    """Analysis results for FLOT chemotherapy case."""

    case_id: str = Field(..., description="Case identifier")
    analysis_timestamp: datetime = Field(default_factory=datetime.now)

    # Treatment completion analysis
    completion_rate: float = Field(
        ..., ge=0, le=1, description="Treatment completion rate"
    )
    adherence_score: float = Field(
        ..., ge=0, le=100, description="Treatment adherence score"
    )

    # Efficacy assessment
    response_score: float | None = Field(
        None, ge=0, le=100, description="Overall response score"
    )
    staging_improvement: bool = Field(..., description="Staging improvement achieved")
    downstaging_success: bool = Field(..., description="Successful downstaging")

    # Toxicity assessment
    toxicity_burden_score: float = Field(
        ..., ge=0, le=100, description="Overall toxicity burden"
    )
    tolerability_rating: str = Field(..., description="Treatment tolerability rating")

    # Predictive factors
    surgical_fitness_score: float | None = Field(
        None, ge=0, le=100, description="Post-FLOT surgical fitness"
    )
    nutritional_status_score: float | None = Field(
        None, ge=0, le=100, description="Nutritional status score"
    )

    # Recommendations
    surgery_recommendation: str = Field(..., description="Surgery recommendation")
    timing_recommendation: str = Field(
        ..., description="Surgical timing recommendation"
    )
    additional_therapy_needed: bool = Field(
        ..., description="Additional therapy needed"
    )

    # Quality metrics
    treatment_quality_score: float = Field(
        ..., ge=0, le=100, description="Overall treatment quality"
    )
    outcome_prediction: str = Field(..., description="Predicted outcome")

    # Confidence
    confidence_score: float = Field(..., ge=0, le=1, description="Analysis confidence")
    evidence_level: str = Field(..., description="Evidence quality level")

    class Config:
        use_enum_values = True


class ChemoFLOTModule:
    """Independent module for FLOT chemotherapy analysis and optimization."""

    def __init__(self) -> None:
        self.version = "1.0.0"
        self.name = "Chemo FLOT Module"

    def analyze_flot_case(self, case: FLOTCase) -> FLOTAnalysis:
        """Analyze FLOT chemotherapy case and provide recommendations."""
        # Calculate treatment metrics
        completion_rate = self._calculate_completion_rate(case)
        adherence_score = self._calculate_adherence_score(case)

        # Assess efficacy
        response_score = self._calculate_response_score(case)
        staging_improvement = self._assess_staging_improvement(case)
        downstaging_success = self._assess_downstaging_success(case)

        # Assess toxicity
        toxicity_score = self._calculate_toxicity_burden(case)
        tolerability = self._assess_tolerability(case)

        # Assess fitness for surgery
        surgical_fitness = self._assess_surgical_fitness(case)
        nutritional_status = self._assess_nutritional_status(case)

        # Generate recommendations
        surgery_rec = self._recommend_surgery(case)
        timing_rec = self._recommend_surgical_timing(case)
        additional_therapy = self._assess_additional_therapy_need(case)

        # Quality metrics
        quality_score = self._calculate_treatment_quality(case)
        outcome_prediction = self._predict_outcome(case)

        # Confidence assessment
        confidence = self._calculate_confidence(case)
        evidence_level = self._assess_evidence_level(case)

        return FLOTAnalysis(
            case_id=case.case_id,
            completion_rate=completion_rate,
            adherence_score=adherence_score,
            response_score=response_score,
            staging_improvement=staging_improvement,
            downstaging_success=downstaging_success,
            toxicity_burden_score=toxicity_score,
            tolerability_rating=tolerability,
            surgical_fitness_score=surgical_fitness,
            nutritional_status_score=nutritional_status,
            surgery_recommendation=surgery_rec,
            timing_recommendation=timing_rec,
            additional_therapy_needed=additional_therapy,
            treatment_quality_score=quality_score,
            outcome_prediction=outcome_prediction,
            confidence_score=confidence,
            evidence_level=evidence_level,
        )

    def _calculate_completion_rate(self, case: FLOTCase) -> float:
        """Calculate treatment completion rate."""
        return case.completed_cycles / case.planned_cycles

    def _calculate_adherence_score(self, case: FLOTCase) -> float:
        """Calculate treatment adherence score."""
        base_score = (case.completed_cycles / case.planned_cycles) * 100

        # Penalize for dose reductions and delays
        penalty = (case.dose_reductions * 5) + (case.treatment_delays * 3)

        return max(0, base_score - penalty)

    def _calculate_response_score(self, case: FLOTCase) -> float | None:
        """Calculate overall response score."""
        if not case.radiological_response and not case.pathological_response:
            return None

        response_scores = {
            ResponseGrade.COMPLETE: 100,
            ResponseGrade.MAJOR: 80,
            ResponseGrade.PARTIAL: 60,
            ResponseGrade.MINIMAL: 30,
            ResponseGrade.STABLE: 10,
            ResponseGrade.PROGRESSIVE: 0,
        }

        # Use pathological response if available, otherwise radiological
        response = case.pathological_response or case.radiological_response
        return response_scores.get(response, 50)

    def _assess_staging_improvement(self, case: FLOTCase) -> bool:
        """Assess if staging improved with FLOT."""
        if not case.post_t_stage:
            return False

        # Simple comparison - more sophisticated staging comparison would be ideal
        initial_stage = f"{case.initial_t_stage.value}{case.initial_n_stage.value}{case.initial_m_stage.value}"
        post_stage = f"{case.post_t_stage.value}{case.post_n_stage.value}{case.post_m_stage.value}"

        # Basic downstaging detection
        return self._is_downstaged(initial_stage, post_stage)

    def _assess_downstaging_success(self, case: FLOTCase) -> bool:
        """Assess successful downstaging."""
        if not case.post_t_stage:
            return False

        # T stage downstaging
        t_downstaged = self._t_stage_numeric(case.post_t_stage) < self._t_stage_numeric(
            case.initial_t_stage
        )

        # N stage downstaging
        n_downstaged = (
            self._n_stage_numeric(case.post_n_stage)
            < self._n_stage_numeric(case.initial_n_stage)
            if case.post_n_stage
            else False
        )

        return t_downstaged or n_downstaged

    def _calculate_toxicity_burden(self, case: FLOTCase) -> float:
        """Calculate overall toxicity burden score."""
        base_score = 0

        if case.max_toxicity_grade:
            toxicity_scores = {
                ToxicityGrade.GRADE_0: 0,
                ToxicityGrade.GRADE_1: 10,
                ToxicityGrade.GRADE_2: 25,
                ToxicityGrade.GRADE_3: 50,
                ToxicityGrade.GRADE_4: 80,
                ToxicityGrade.GRADE_5: 100,
            }
            base_score = toxicity_scores.get(case.max_toxicity_grade, 25)

        # Add burden for hospitalizations and complications
        base_score += case.hospitalizations * 10
        base_score += case.infections * 15
        base_score += case.dose_reductions * 5

        return min(base_score, 100)

    def _assess_tolerability(self, case: FLOTCase) -> str:
        """Assess treatment tolerability."""
        toxicity_score = self._calculate_toxicity_burden(case)
        completion_rate = self._calculate_completion_rate(case)

        if toxicity_score <= 20 and completion_rate >= 0.8:
            return "Excellent"
        if toxicity_score <= 40 and completion_rate >= 0.6:
            return "Good"
        if toxicity_score <= 60 and completion_rate >= 0.4:
            return "Acceptable"
        return "Poor"

    def _assess_surgical_fitness(self, case: FLOTCase) -> float | None:
        """Assess fitness for surgery after FLOT."""
        if not case.post_flot_ecog:
            return None

        fitness_score = 80  # Base score

        # ECOG performance status
        if case.post_flot_ecog == 0:
            fitness_score += 20
        elif case.post_flot_ecog == 1:
            fitness_score += 10
        elif case.post_flot_ecog >= 2:
            fitness_score -= 30

        # Weight loss assessment
        if case.baseline_weight_kg and case.post_flot_weight_kg:
            weight_loss_pct = (
                (case.baseline_weight_kg - case.post_flot_weight_kg)
                / case.baseline_weight_kg
            ) * 100
            if weight_loss_pct > 15:
                fitness_score -= 25
            elif weight_loss_pct > 10:
                fitness_score -= 15
            elif weight_loss_pct > 5:
                fitness_score -= 5

        # Albumin level
        if case.post_flot_albumin:
            if case.post_flot_albumin >= 3.5:
                fitness_score += 10
            elif case.post_flot_albumin < 2.5:
                fitness_score -= 20

        return max(0, min(fitness_score, 100))

    def _assess_nutritional_status(self, case: FLOTCase) -> float | None:
        """Assess nutritional status after FLOT."""
        if not case.post_flot_albumin:
            return None

        nutrition_score = 50  # Base score

        # Albumin level
        if case.post_flot_albumin >= 4.0:
            nutrition_score += 30
        elif case.post_flot_albumin >= 3.5:
            nutrition_score += 20
        elif case.post_flot_albumin >= 3.0:
            nutrition_score += 10
        elif case.post_flot_albumin < 2.5:
            nutrition_score -= 30

        # Weight change
        if case.baseline_weight_kg and case.post_flot_weight_kg:
            weight_loss_pct = (
                (case.baseline_weight_kg - case.post_flot_weight_kg)
                / case.baseline_weight_kg
            ) * 100
            if weight_loss_pct <= 5:
                nutrition_score += 20
            elif weight_loss_pct <= 10:
                nutrition_score += 10
            elif weight_loss_pct > 15:
                nutrition_score -= 30

        return max(0, min(nutrition_score, 100))

    def _recommend_surgery(self, case: FLOTCase) -> str:
        """Recommend whether to proceed with surgery."""
        fitness_score = self._assess_surgical_fitness(case)
        response_score = self._calculate_response_score(case)

        # Factors supporting surgery
        good_response = response_score and response_score >= 50
        good_fitness = fitness_score and fitness_score >= 60
        completed_treatment = case.completed_cycles >= (case.planned_cycles * 0.75)

        if good_response and good_fitness and completed_treatment:
            return "Proceed with surgery"
        if fitness_score and fitness_score < 40:
            return "Delay surgery - optimize fitness"
        if response_score and response_score < 30:
            return "Consider alternative therapy"
        return "Surgery feasible with optimization"

    def _recommend_surgical_timing(self, case: FLOTCase) -> str:
        """Recommend optimal surgical timing."""
        fitness_score = self._assess_surgical_fitness(case)

        if fitness_score and fitness_score >= 80:
            return "Surgery within 4-6 weeks"
        if fitness_score and fitness_score >= 60:
            return "Surgery within 6-8 weeks with optimization"
        return "Delay surgery - nutritional optimization needed"

    def _assess_additional_therapy_need(self, case: FLOTCase) -> bool:
        """Assess if additional therapy is needed."""
        response_score = self._calculate_response_score(case)
        completion_rate = self._calculate_completion_rate(case)

        # Poor response or incomplete treatment may need additional therapy
        poor_response = response_score and response_score < 40
        incomplete_treatment = completion_rate < 0.6

        return poor_response or incomplete_treatment

    def _calculate_treatment_quality(self, case: FLOTCase) -> float:
        """Calculate overall treatment quality score."""
        completion_rate = self._calculate_completion_rate(case)
        adherence_score = self._calculate_adherence_score(case)
        response_score = self._calculate_response_score(case) or 50
        toxicity_score = self._calculate_toxicity_burden(case)

        # Weighted quality score
        quality = (
            completion_rate * 30
            + (adherence_score / 100) * 25
            + (response_score / 100) * 30
            + ((100 - toxicity_score) / 100) * 15
        )

        return min(quality, 100)

    def _predict_outcome(self, case: FLOTCase) -> str:
        """Predict treatment outcome."""
        quality_score = self._calculate_treatment_quality(case)

        if quality_score >= 80:
            return "Excellent prognosis"
        if quality_score >= 60:
            return "Good prognosis"
        if quality_score >= 40:
            return "Moderate prognosis"
        return "Guarded prognosis"

    def _calculate_confidence(self, case: FLOTCase) -> float:
        """Calculate confidence in analysis."""
        confidence = 0.7  # Base confidence

        # Increase confidence based on data completeness
        if case.radiological_response or case.pathological_response:
            confidence += 0.1
        if case.post_flot_albumin:
            confidence += 0.05
        if case.post_flot_ecog is not None:
            confidence += 0.05
        if case.baseline_weight_kg and case.post_flot_weight_kg:
            confidence += 0.05
        if case.max_toxicity_grade:
            confidence += 0.05

        return min(confidence, 1.0)

    def _assess_evidence_level(self, case: FLOTCase) -> str:
        """Assess quality of evidence for recommendations."""
        completion_rate = self._calculate_completion_rate(case)

        if completion_rate >= 0.8 and case.pathological_response:
            return "High"
        if completion_rate >= 0.6 and case.radiological_response:
            return "Moderate"
        return "Limited"

    # Helper methods for staging comparison
    def _is_downstaged(self, initial: str, post: str) -> bool:
        """Simple downstaging assessment."""
        # This would need more sophisticated logic for proper TNM comparison
        return len(post.replace("0", "")) < len(initial.replace("0", ""))

    def _t_stage_numeric(self, t_stage: TumorStage) -> int:
        """Convert T stage to numeric for comparison."""
        stage_map = {
            "T0": 0,
            "Tis": 0.5,
            "T1": 1,
            "T1a": 1.1,
            "T1b": 1.2,
            "T2": 2,
            "T3": 3,
            "T4": 4,
            "T4a": 4.1,
            "T4b": 4.2,
            "Tx": 0,
        }
        return stage_map.get(t_stage.value, 2)

    def _n_stage_numeric(self, n_stage: NodeStage) -> int:
        """Convert N stage to numeric for comparison."""
        stage_map = {
            "N0": 0,
            "N1": 1,
            "N2": 2,
            "N3": 3,
            "N3a": 3.1,
            "N3b": 3.2,
            "Nx": 0,
        }
        return stage_map.get(n_stage.value, 1)

    def analyze_flot_regimen(self: FLOTCase) -> dict[str, Any]:
        """Analyze FLOT regimen for a specific case, returning:
        - FLOT applicability score
        - Dose intensity analysis
        - Cycles completed assessment
        - Toxicity (CTCAE buckets)
        - Response (RECIST or pathologic)
        - Narrative summary.
        """
        from datetime import datetime

        analysis = {
            "case_id": self.case_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "flot_phase": self.flot_phase,
            "protocol_version": "FLOT4 Standard",
        }

        # FLOT Applicability Assessment
        def assess_flot_applicability(case: FLOTCase) -> dict[str, Any]:
            """Assess patient suitability for FLOT therapy."""
            criteria = {
                "performance_status": None,
                "organ_function": None,
                "tumor_stage": None,
                "histology": None,
                "age_fitness": None,
            }

            applicability_score = 0
            max_score = 0

            # Performance Status (ECOG 0-1 preferred)
            if case.baseline_ecog is not None:
                max_score += 20
                if case.baseline_ecog <= 1:
                    criteria["performance_status"] = "Excellent (ECOG 0-1)"
                    applicability_score += 20
                elif case.baseline_ecog == 2:
                    criteria["performance_status"] = "Marginal (ECOG 2)"
                    applicability_score += 10
                else:
                    criteria["performance_status"] = "Poor (ECOG >2)"
                    applicability_score += 0

            # Organ Function (kidney, liver, bone marrow)
            organ_score = 0
            organ_max = 25
            max_score += organ_max

            # Renal function
            if case.baseline_creatinine and case.baseline_creatinine <= 1.5:
                organ_score += 8
            elif case.baseline_creatinine and case.baseline_creatinine <= 2.0:
                organ_score += 4

            # Hepatic function
            if case.baseline_bilirubin and case.baseline_bilirubin <= 1.5:
                organ_score += 8
            elif case.baseline_bilirubin and case.baseline_bilirubin <= 2.0:
                organ_score += 4

            # Nutritional status
            if case.baseline_albumin and case.baseline_albumin >= 3.0:
                organ_score += 9
            elif case.baseline_albumin and case.baseline_albumin >= 2.5:
                organ_score += 4

            applicability_score += organ_score
            criteria["organ_function"] = f"Score: {organ_score}/{organ_max}"

            # Tumor Stage Appropriateness (T2+ or N+ typically)
            if case.initial_t_stage and case.initial_n_stage:
                max_score += 25
                t_numeric = (
                    int(case.initial_t_stage.value[1])
                    if case.initial_t_stage.value[1:].isdigit()
                    else 0
                )
                n_positive = case.initial_n_stage.value != "N0"

                if t_numeric >= 3 or n_positive:
                    criteria["tumor_stage"] = "Optimal indication (≥T3 or N+)"
                    applicability_score += 25
                elif t_numeric == 2:
                    criteria["tumor_stage"] = "Reasonable indication (T2)"
                    applicability_score += 15
                else:
                    criteria["tumor_stage"] = "Questionable indication (T1N0)"
                    applicability_score += 5

            # Histology (adenocarcinoma best)
            if hasattr(case, "histology_type"):
                max_score += 15
                if "adenocarcinoma" in case.histology_type.lower():
                    criteria["histology"] = "Optimal (Adenocarcinoma)"
                    applicability_score += 15
                else:
                    criteria["histology"] = f"Acceptable ({case.histology_type})"
                    applicability_score += 10

            # Age and Fitness
            if case.age:
                max_score += 15
                if case.age <= 70:
                    criteria["age_fitness"] = "Optimal (<70 years)"
                    applicability_score += 15
                elif case.age <= 75:
                    criteria["age_fitness"] = "Good (70-75 years)"
                    applicability_score += 12
                elif case.age <= 80:
                    criteria["age_fitness"] = "Caution (75-80 years)"
                    applicability_score += 8
                else:
                    criteria["age_fitness"] = "High risk (>80 years)"
                    applicability_score += 3

            percentage_score = (
                (applicability_score / max_score * 100) if max_score > 0 else 0
            )

            return {
                "applicability_score": round(percentage_score, 1),
                "criteria_assessment": criteria,
                "recommendation": (
                    "Excellent candidate"
                    if percentage_score >= 80
                    else "Good candidate"
                    if percentage_score >= 65
                    else "Marginal candidate"
                    if percentage_score >= 50
                    else "Poor candidate"
                ),
                "raw_score": f"{applicability_score}/{max_score}",
            }

        applicability = assess_flot_applicability(self)
        analysis["applicability"] = applicability

        # Dose Intensity Analysis
        def analyze_dose_intensity(case: FLOTCase) -> dict[str, Any]:
            """Analyze relative dose intensity of FLOT therapy."""
            planned_cycles = case.cycles_planned or 8  # Standard FLOT is 8 cycles
            completed_cycles = case.cycles_completed or 0

            # Standard FLOT doses (per cycle)

            # Calculate relative dose intensity (RDI)
            dose_reductions = case.dose_reductions or []
            delays = case.treatment_delays or []

            # Estimate RDI based on available data
            rdi_estimate = 100.0  # Start at 100%

            # Reduce for dose modifications
            if dose_reductions:
                avg_reduction = (
                    sum(
                        float(red.replace("%", ""))
                        for red in dose_reductions
                        if red.replace("%", "").replace(".", "").isdigit()
                    )
                    / len(dose_reductions)
                    if dose_reductions
                    else 0
                )
                rdi_estimate -= avg_reduction

            # Reduce for delays (approximate impact)
            if delays:
                delay_impact = min(len(delays) * 5, 20)  # Max 20% reduction for delays
                rdi_estimate -= delay_impact

            # Adjust for incomplete cycles
            cycle_completion_rate = (
                (completed_cycles / planned_cycles * 100) if planned_cycles > 0 else 0
            )
            rdi_estimate = min(rdi_estimate, cycle_completion_rate)

            return {
                "relative_dose_intensity": round(max(rdi_estimate, 0), 1),
                "cycles_planned": planned_cycles,
                "cycles_completed": completed_cycles,
                "completion_rate": round(cycle_completion_rate, 1),
                "dose_modifications": {
                    "reductions": dose_reductions,
                    "delays": delays,
                    "total_modifications": len(dose_reductions) + len(delays),
                },
                "rdi_category": (
                    "Optimal"
                    if rdi_estimate >= 85
                    else "Adequate"
                    if rdi_estimate >= 70
                    else "Suboptimal"
                    if rdi_estimate >= 50
                    else "Poor"
                ),
            }

        dose_intensity = analyze_dose_intensity(self)
        analysis["dose_intensity"] = dose_intensity

        # Toxicity Analysis (CTCAE)
        def analyze_toxicity_profile(case: FLOTCase) -> dict[str, Any]:
            """Analyze toxicity according to CTCAE criteria."""
            toxicity_buckets = {
                "hematologic": [],
                "gastrointestinal": [],
                "neurologic": [],
                "constitutional": [],
                "other": [],
            }

            # Categorize toxicities
            specific_toxicities = case.specific_toxicities or []
            for toxicity in specific_toxicities:
                tox_lower = toxicity.lower()
                if any(
                    term in tox_lower
                    for term in [
                        "neutropenia",
                        "anemia",
                        "thrombocytopenia",
                        "leukopenia",
                    ]
                ):
                    toxicity_buckets["hematologic"].append(toxicity)
                elif any(
                    term in tox_lower
                    for term in [
                        "nausea",
                        "vomiting",
                        "diarrhea",
                        "mucositis",
                        "stomatitis",
                    ]
                ):
                    toxicity_buckets["gastrointestinal"].append(toxicity)
                elif any(
                    term in tox_lower
                    for term in ["neuropathy", "peripheral", "sensory"]
                ):
                    toxicity_buckets["neurologic"].append(toxicity)
                elif any(
                    term in tox_lower
                    for term in ["fatigue", "asthenia", "weakness", "fever"]
                ):
                    toxicity_buckets["constitutional"].append(toxicity)
                else:
                    toxicity_buckets["other"].append(toxicity)

            # Grade analysis
            max_grade = (
                case.max_toxicity_grade.value if case.max_toxicity_grade else "0"
            )
            grade_distribution = {}

            # If specific grades available, analyze them
            if hasattr(case, "toxicity_grades") and case.toxicity_grades:
                for grade in case.toxicity_grades:
                    grade_distribution[grade] = grade_distribution.get(grade, 0) + 1

            return {
                "toxicity_buckets": toxicity_buckets,
                "max_grade": max_grade,
                "grade_distribution": grade_distribution,
                "severe_toxicity": max_grade in ["3", "4", "5"],
                "dose_limiting": case.dose_limiting_toxicity,
                "hospitalization_required": any(
                    grade in ["4", "5"] for grade in grade_distribution
                ),
                "tolerability_assessment": (
                    "Excellent"
                    if max_grade in ["0", "1"]
                    else "Good"
                    if max_grade == "2"
                    else "Poor"
                    if max_grade == "3"
                    else "Severe"
                    if max_grade in ["4", "5"]
                    else "Unknown"
                ),
            }

        toxicity = analyze_toxicity_profile(self)
        analysis["toxicity"] = toxicity

        # Response Analysis (RECIST/Pathologic)
        def analyze_response(case: FLOTCase) -> dict[str, Any]:
            """Analyze tumor response to FLOT therapy."""
            response_data = {
                "clinical_response": case.clinical_response,
                "radiologic_response": case.radiologic_response,
                "pathologic_response": case.pathologic_response,
                "response_evaluation_method": "RECIST 1.1",
            }

            # Determine best response
            responses = [
                case.clinical_response,
                case.radiologic_response,
                case.pathologic_response,
            ]
            valid_responses = [r for r in responses if r and r.value != "unknown"]

            # Response hierarchy (best to worst)
            response_hierarchy = {
                "complete_response": 4,
                "major_response": 3,
                "partial_response": 2,
                "stable_disease": 1,
                "progressive_disease": 0,
            }

            best_response = None
            best_score = -1

            for response in valid_responses:
                if response and response.value in response_hierarchy:
                    score = response_hierarchy[response.value]
                    if score > best_score:
                        best_score = score
                        best_response = response.value

            # Calculate response metrics
            response_metrics = {
                "best_response": best_response,
                "clinical_benefit": best_response
                in ["complete_response", "major_response", "partial_response"]
                if best_response
                else None,
                "disease_control": best_response
                in [
                    "complete_response",
                    "major_response",
                    "partial_response",
                    "stable_disease",
                ]
                if best_response
                else None,
                "pathologic_complete_response": case.pathologic_response
                and case.pathologic_response.value == "complete_response",
            }

            # Response quality assessment
            if best_response:
                if best_response in ["complete_response", "major_response"]:
                    quality = "Excellent"
                elif best_response == "partial_response":
                    quality = "Good"
                elif best_response == "stable_disease":
                    quality = "Stable"
                else:
                    quality = "Poor"
            else:
                quality = "Unknown"

            response_data.update(
                {
                    "response_metrics": response_metrics,
                    "response_quality": quality,
                    "tumor_regression_grade": case.pathologic_response.value
                    if case.pathologic_response
                    else None,
                }
            )

            return response_data

        response_analysis = analyze_response(self)
        analysis["response"] = response_analysis

        # Generate Narrative Summary
        def generate_narrative(case: FLOTCase, analysis_data: dict) -> str:
            """Generate clinical narrative summary."""
            narrative_parts = []

            # Patient demographics
            age_str = f"{case.age}-year-old" if case.age else "Adult"
            narrative_parts.append(f"{age_str} patient with gastric adenocarcinoma")

            # Staging
            if case.initial_t_stage and case.initial_n_stage:
                stage = f"{case.initial_t_stage.value}{case.initial_n_stage.value}"
                if case.initial_m_stage:
                    stage += case.initial_m_stage.value
                narrative_parts.append(f"staged as {stage}")

            # FLOT suitability
            app_score = analysis_data["applicability"]["applicability_score"]
            suitability = analysis_data["applicability"]["recommendation"]
            narrative_parts.append(
                f"assessed as {suitability.lower()} for FLOT therapy (score: {app_score}%)"
            )

            # Treatment course
            cycles_completed = case.cycles_completed or 0
            cycles_planned = case.cycles_planned or 8
            narrative_parts.append(
                f"completed {cycles_completed} of {cycles_planned} planned FLOT cycles"
            )

            # Dose intensity
            rdi = analysis_data["dose_intensity"]["relative_dose_intensity"]
            rdi_cat = analysis_data["dose_intensity"]["rdi_category"]
            narrative_parts.append(
                f"achieving {rdi_cat.lower()} dose intensity ({rdi}%)"
            )

            # Toxicity
            max_grade = analysis_data["toxicity"]["max_grade"]
            tox_assessment = analysis_data["toxicity"]["tolerability_assessment"]
            narrative_parts.append(
                f"with {tox_assessment.lower()} tolerability (max grade {max_grade} toxicity)"
            )

            # Response
            best_response = analysis_data["response"]["response_metrics"][
                "best_response"
            ]
            if best_response:
                response_quality = analysis_data["response"]["response_quality"]
                narrative_parts.append(
                    f"demonstrating {response_quality.lower()} response ({best_response.replace('_', ' ')})"
                )

            # Recommendations
            recommendations = []
            if app_score < 50:
                recommendations.append("consider alternative regimen")
            if rdi < 70:
                recommendations.append("optimize supportive care")
            if max_grade in ["3", "4", "5"]:
                recommendations.append("enhance toxicity monitoring")

            if recommendations:
                narrative_parts.append(f"Recommendations: {', '.join(recommendations)}")

            return ". ".join(part.capitalize() for part in narrative_parts) + "."

        narrative = generate_narrative(self, analysis)
        analysis["narrative_summary"] = narrative

        # Overall Assessment Score
        scores = [
            analysis["applicability"]["applicability_score"],
            analysis["dose_intensity"]["relative_dose_intensity"],
            (100 - int(analysis["toxicity"]["max_grade"]) * 20)
            if analysis["toxicity"]["max_grade"].isdigit()
            else 80,
            (
                80
                if analysis["response"]["response_quality"] == "Excellent"
                else 60
                if analysis["response"]["response_quality"] == "Good"
                else 40
                if analysis["response"]["response_quality"] == "Stable"
                else 20
                if analysis["response"]["response_quality"] == "Poor"
                else 50
            ),
        ]

        overall_score = sum(scores) / len(scores)
        analysis["overall_assessment"] = {
            "composite_score": round(overall_score, 1),
            "grade": (
                "A"
                if overall_score >= 85
                else "B"
                if overall_score >= 70
                else "C"
                if overall_score >= 55
                else "D"
            ),
            "component_scores": {
                "applicability": scores[0],
                "dose_intensity": scores[1],
                "toxicity_tolerance": scores[2],
                "response_quality": scores[3],
            },
        }

        return analysis


# Descriptive analytics functions
def analyze_flot_cohort(cases: list[FLOTCase]) -> dict[str, Any]:
    """Analyze a cohort of FLOT cases - descriptive analytics."""
    if not cases:
        return {"error": "No cases provided"}

    # Basic metrics
    total_cases = len(cases)
    completed_cases = [
        case
        for case in cases
        if case.phase in [FLOTPhase.COMPLETE, FLOTPhase.POSTOPERATIVE]
    ]

    # Treatment completion rates
    completion_rates = [case.completed_cycles / case.planned_cycles for case in cases]
    avg_completion_rate = sum(completion_rates) / len(completion_rates)

    # Response rates (for cases with response data)
    response_cases = [
        case
        for case in cases
        if case.radiological_response or case.pathological_response
    ]
    good_responses = [
        case
        for case in response_cases
        if case.radiological_response
        in [ResponseGrade.COMPLETE, ResponseGrade.MAJOR, ResponseGrade.PARTIAL]
    ]

    # Toxicity assessment
    high_toxicity_cases = [
        case
        for case in cases
        if case.max_toxicity_grade
        in [ToxicityGrade.GRADE_3, ToxicityGrade.GRADE_4, ToxicityGrade.GRADE_5]
    ]

    # Dose modifications
    dose_reduced_cases = [case for case in cases if case.dose_reductions > 0]
    delayed_cases = [case for case in cases if case.treatment_delays > 0]

    return {
        "cohort_summary": {
            "total_cases": total_cases,
            "completed_treatment": len(completed_cases),
            "average_completion_rate": round(avg_completion_rate, 3),
        },
        "efficacy_metrics": {
            "response_evaluable_cases": len(response_cases),
            "objective_response_rate": len(good_responses) / len(response_cases)
            if response_cases
            else 0,
            "complete_response_rate": len(
                [
                    c
                    for c in response_cases
                    if c.radiological_response == ResponseGrade.COMPLETE
                ]
            )
            / len(response_cases)
            if response_cases
            else 0,
        },
        "toxicity_profile": {
            "high_grade_toxicity_rate": len(high_toxicity_cases) / total_cases,
            "dose_reduction_rate": len(dose_reduced_cases) / total_cases,
            "treatment_delay_rate": len(delayed_cases) / total_cases,
            "hospitalization_rate": len([c for c in cases if c.hospitalizations > 0])
            / total_cases,
        },
        "treatment_modifications": {
            "average_dose_reductions": sum(case.dose_reductions for case in cases)
            / total_cases,
            "average_treatment_delays": sum(case.treatment_delays for case in cases)
            / total_cases,
        },
    }


# Analytic functions for optimization
def optimize_flot_protocol(cases: list[FLOTCase]) -> dict[str, Any]:
    """Optimize FLOT protocol based on case outcomes."""
    if not cases:
        return {"error": "No cases provided"}

    module = ChemoFLOTModule()
    analyses = [module.analyze_flot_case(case) for case in cases]

    # Identify optimal cycle number
    cycle_outcomes = {}
    for case, analysis in zip(cases, analyses, strict=False):
        cycles = case.completed_cycles
        if cycles not in cycle_outcomes:
            cycle_outcomes[cycles] = []
        cycle_outcomes[cycles].append(analysis.treatment_quality_score)

    optimal_cycles = max(
        cycle_outcomes.keys(),
        key=lambda x: sum(cycle_outcomes[x]) / len(cycle_outcomes[x]),
    )

    # Identify patients at risk for poor outcomes
    high_risk_patients = []
    for case, analysis in zip(cases, analyses, strict=False):
        if analysis.toxicity_burden_score > 60 or analysis.treatment_quality_score < 40:
            high_risk_patients.append(
                {
                    "patient_id": case.patient_id,
                    "risk_factors": _identify_flot_risk_factors(case),
                    "recommendations": _get_optimization_recommendations(
                        case, analysis
                    ),
                }
            )

    # Protocol recommendations
    recommendations = []

    # Cycle optimization
    recommendations.append(
        f"Optimal cycle number appears to be {optimal_cycles} based on quality outcomes"
    )

    # Risk mitigation
    if len(high_risk_patients) > len(cases) * 0.3:
        recommendations.append(
            "Consider dose reduction protocols for high-risk patients"
        )

    # Monitoring recommendations
    if sum(case.hospitalizations for case in cases) > len(cases) * 0.2:
        recommendations.append(
            "Enhance monitoring protocols to reduce hospitalizations"
        )

    return {
        "protocol_optimization": {
            "optimal_cycle_number": optimal_cycles,
            "high_risk_patient_rate": len(high_risk_patients) / len(cases),
            "average_quality_score": sum(a.treatment_quality_score for a in analyses)
            / len(analyses),
        },
        "high_risk_patients": high_risk_patients,
        "optimization_recommendations": recommendations,
        "toxicity_patterns": _analyze_toxicity_patterns(cases),
        "efficacy_predictors": _identify_efficacy_predictors(cases, analyses),
    }


def _identify_flot_risk_factors(case: FLOTCase) -> list[str]:
    """Identify risk factors for poor FLOT outcomes."""
    risk_factors = []

    if case.baseline_ecog and case.baseline_ecog >= 2:
        risk_factors.append("Poor baseline performance status")

    if case.baseline_albumin and case.baseline_albumin < 3.0:
        risk_factors.append("Low baseline albumin")

    if case.initial_t_stage.value in ["T4", "T4a", "T4b"]:
        risk_factors.append("Advanced T stage")

    if case.initial_m_stage.value.startswith("M1"):
        risk_factors.append("Metastatic disease")

    return risk_factors


def _get_optimization_recommendations(
    case: FLOTCase, analysis: FLOTAnalysis
) -> list[str]:
    """Get optimization recommendations for specific case."""
    recommendations = []

    if analysis.toxicity_burden_score > 60:
        recommendations.append("Consider dose reduction or alternative regimen")

    if analysis.surgical_fitness_score and analysis.surgical_fitness_score < 50:
        recommendations.append("Intensive nutritional support and fitness optimization")

    if analysis.completion_rate < 0.6:
        recommendations.append("Early intervention for treatment adherence")

    return recommendations


def _analyze_toxicity_patterns(cases: list[FLOTCase]) -> dict[str, Any]:
    """Analyze toxicity patterns across cohort."""
    toxicity_distribution = {}
    for case in cases:
        if case.max_toxicity_grade:
            grade = case.max_toxicity_grade.value
            toxicity_distribution[grade] = toxicity_distribution.get(grade, 0) + 1

    return {
        "toxicity_distribution": toxicity_distribution,
        "severe_toxicity_rate": len(
            [
                c
                for c in cases
                if c.max_toxicity_grade
                in [ToxicityGrade.GRADE_3, ToxicityGrade.GRADE_4]
            ]
        )
        / len(cases),
    }


def _identify_efficacy_predictors(
    cases: list[FLOTCase], analyses: list[FLOTAnalysis]
) -> dict[str, Any]:
    """Identify predictors of treatment efficacy."""
    # Correlate baseline factors with response
    good_responders = []
    poor_responders = []

    for case, analysis in zip(cases, analyses, strict=False):
        if analysis.response_score and analysis.response_score >= 60:
            good_responders.append(case)
        elif analysis.response_score and analysis.response_score < 40:
            poor_responders.append(case)

    return {
        "good_responder_characteristics": {
            "average_baseline_albumin": _safe_average(
                [c.baseline_albumin for c in good_responders if c.baseline_albumin]
            ),
            "t4_rate": len(
                [c for c in good_responders if c.initial_t_stage.value.startswith("T4")]
            )
            / len(good_responders)
            if good_responders
            else 0,
        },
        "poor_responder_characteristics": {
            "average_baseline_albumin": _safe_average(
                [c.baseline_albumin for c in poor_responders if c.baseline_albumin]
            ),
            "t4_rate": len(
                [c for c in poor_responders if c.initial_t_stage.value.startswith("T4")]
            )
            / len(poor_responders)
            if poor_responders
            else 0,
        },
    }


def _safe_average(values: list[float]) -> float | None:
    """Safely calculate average of a list."""
    return sum(values) / len(values) if values else None


# Import helpers for easier access
def analyze_flot_regimen(case: FLOTCase) -> dict[str, Any]:
    """Standalone function to analyze FLOT regimen."""
    module = FLOTModule()
    return module.analyze_flot_regimen(case)


def create_sample_flot_case(patient_id: str = "P001") -> FLOTCase:
    """Create a sample FLOT case for testing."""
    return FLOTCase(
        patient_id=patient_id,
        case_id=f"C{patient_id[1:]}",
        age=45,
        performance_status=0,
        initial_t_stage=TumorStage.T1,
        initial_n_stage=NodeStage.N0,
        initial_m_stage=MetastasisStage.M0,
        cycles_planned=4,
        cycles_completed=4,
        phase=FLOTPhase.COMPLETE,
    )
