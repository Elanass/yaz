"""Precision Decision Engine
Advanced decision support system integrating gastric surgery and FLOT modules.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .chemo_flot import ChemoFLOTModule, FLOTAnalysis, FLOTCase
from .gastric_surgery import (
    GastricSurgeryAnalysis,
    GastricSurgeryCase,
    GastricSurgeryModule,
)


class DecisionClass(str, Enum):
    """Classification of clinical decisions."""

    SURGICAL_ONLY = "surgical_only"
    NEOADJUVANT_SURGERY = "neoadjuvant_surgery"
    PERIOPERATIVE = "perioperative"
    PALLIATIVE = "palliative"
    SURVEILLANCE = "surveillance"


class TreatmentSequence(str, Enum):
    """Treatment sequence options."""

    SURGERY_FIRST = "surgery_first"
    FLOT_THEN_SURGERY = "flot_then_surgery"
    FLOT_SURGERY_FLOT = "flot_surgery_flot"
    FLOT_ONLY = "flot_only"
    BEST_SUPPORTIVE_CARE = "best_supportive_care"


class EvidenceLevel(str, Enum):
    """Evidence quality levels."""

    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    EXPERT_OPINION = "expert_opinion"


class IntegratedCase(BaseModel):
    """Integrated case combining gastric surgery and FLOT data."""

    # Patient identifiers
    patient_id: str = Field(..., description="Unique patient identifier")
    case_id: str = Field(..., description="Unique case identifier")

    # Core components
    gastric_surgery_case: GastricSurgeryCase | None = Field(
        None, description="Gastric surgery case data"
    )
    flot_case: FLOTCase | None = Field(None, description="FLOT case data")

    # Patient factors
    age: int | None = Field(None, ge=0, le=120, description="Patient age")
    performance_status: int | None = Field(
        None, ge=0, le=4, description="ECOG performance status"
    )
    comorbidities: list[str] = Field(default=[], description="Major comorbidities")

    # Tumor biology
    histology_subtype: str | None = Field(
        None, description="Specific histology subtype"
    )
    her2_status: str | None = Field(None, description="HER2 status")
    msi_status: str | None = Field(None, description="MSI status")
    pdl1_expression: float | None = Field(
        None, ge=0, le=100, description="PD-L1 expression %"
    )

    # Multidisciplinary considerations
    surgeon_preference: str | None = Field(
        None, description="Surgeon preference/approach"
    )
    oncologist_recommendation: str | None = Field(
        None, description="Medical oncologist recommendation"
    )
    patient_preference: str | None = Field(None, description="Patient preference")
    institutional_protocol: str | None = Field(
        None, description="Institutional standard protocol"
    )

    class Config:
        use_enum_values = True


class PrecisionDecision(BaseModel):
    """Precision decision engine output."""

    case_id: str = Field(..., description="Case identifier")
    analysis_timestamp: datetime = Field(default_factory=datetime.now)

    # Primary recommendation
    decision_class: DecisionClass = Field(..., description="Primary decision class")
    recommended_sequence: TreatmentSequence = Field(
        ..., description="Recommended treatment sequence"
    )
    treatment_rationale: str = Field(..., description="Rationale for recommendation")

    # Detailed recommendations
    surgery_recommendation: str | None = Field(
        None, description="Specific surgery recommendation"
    )
    chemotherapy_recommendation: str | None = Field(
        None, description="Specific chemotherapy recommendation"
    )
    timing_recommendations: dict[str, str] = Field(
        default={}, description="Timing recommendations"
    )

    # Risk stratification
    overall_risk_score: float = Field(
        ..., ge=0, le=100, description="Overall risk score"
    )
    surgical_risk: float = Field(
        ..., ge=0, le=100, description="Surgical risk component"
    )
    chemotherapy_risk: float = Field(
        ..., ge=0, le=100, description="Chemotherapy risk component"
    )

    # Outcome predictions
    predicted_survival_months: float | None = Field(
        None, description="Predicted overall survival"
    )
    predicted_pfs_months: float | None = Field(
        None, description="Predicted progression-free survival"
    )
    predicted_quality_of_life: float | None = Field(
        None, ge=0, le=100, description="Predicted QoL score"
    )

    # Alternative options
    alternative_approaches: list[str] = Field(
        default=[], description="Alternative treatment approaches"
    )
    contraindications: list[str] = Field(
        default=[], description="Treatment contraindications"
    )

    # Quality metrics
    confidence_score: float = Field(
        ..., ge=0, le=1, description="Overall confidence in decision"
    )
    evidence_level: EvidenceLevel = Field(
        ..., description="Quality of supporting evidence"
    )
    consensus_score: float = Field(
        ..., ge=0, le=1, description="Multidisciplinary consensus score"
    )

    # Monitoring and follow-up
    monitoring_recommendations: list[str] = Field(
        default=[], description="Monitoring recommendations"
    )
    decision_review_triggers: list[str] = Field(
        default=[], description="Triggers for decision review"
    )

    class Config:
        use_enum_values = True


class PrecisionDecisionEngine:
    """Advanced precision decision engine for integrated gastric cancer care."""

    def __init__(self) -> None:
        self.version = "1.0.0"
        self.name = "Precision Decision Engine"
        self.gastric_module = GastricSurgeryModule()
        self.flot_module = ChemoFLOTModule()

    def analyze_integrated_case(self, case: IntegratedCase) -> PrecisionDecision:
        """Perform comprehensive analysis and generate precision decision."""
        # Analyze individual components
        surgery_analysis = self._analyze_surgery_component(case)
        flot_analysis = self._analyze_flot_component(case)

        # Integrate analyses
        decision_class = self._determine_decision_class(
            case, surgery_analysis, flot_analysis
        )
        treatment_sequence = self._determine_treatment_sequence(
            case, surgery_analysis, flot_analysis
        )
        rationale = self._generate_rationale(case, decision_class, treatment_sequence)

        # Generate specific recommendations
        surgery_rec = self._generate_surgery_recommendation(case, surgery_analysis)
        chemo_rec = self._generate_chemotherapy_recommendation(case, flot_analysis)
        timing_recs = self._generate_timing_recommendations(case, treatment_sequence)

        # Calculate integrated risk scores
        overall_risk = self._calculate_overall_risk(
            case, surgery_analysis, flot_analysis
        )
        surgical_risk = surgery_analysis.surgical_risk_score if surgery_analysis else 50
        chemo_risk = flot_analysis.toxicity_burden_score if flot_analysis else 50

        # Predict outcomes
        survival_prediction = self._predict_survival(
            case, surgery_analysis, flot_analysis
        )
        pfs_prediction = self._predict_progression_free_survival(
            case, surgery_analysis, flot_analysis
        )
        qol_prediction = self._predict_quality_of_life(
            case, surgery_analysis, flot_analysis
        )

        # Generate alternatives and contraindications
        alternatives = self._generate_alternatives(case, decision_class)
        contraindications = self._identify_contraindications(case)

        # Calculate quality metrics
        confidence = self._calculate_integrated_confidence(
            case, surgery_analysis, flot_analysis
        )
        evidence_level = self._assess_integrated_evidence(
            case, surgery_analysis, flot_analysis
        )
        consensus = self._calculate_consensus_score(case)

        # Generate monitoring recommendations
        monitoring_recs = self._generate_monitoring_recommendations(
            case, treatment_sequence
        )
        review_triggers = self._generate_review_triggers(case, treatment_sequence)

        return PrecisionDecision(
            case_id=case.case_id,
            decision_class=decision_class,
            recommended_sequence=treatment_sequence,
            treatment_rationale=rationale,
            surgery_recommendation=surgery_rec,
            chemotherapy_recommendation=chemo_rec,
            timing_recommendations=timing_recs,
            overall_risk_score=overall_risk,
            surgical_risk=surgical_risk,
            chemotherapy_risk=chemo_risk,
            predicted_survival_months=survival_prediction,
            predicted_pfs_months=pfs_prediction,
            predicted_quality_of_life=qol_prediction,
            alternative_approaches=alternatives,
            contraindications=contraindications,
            confidence_score=confidence,
            evidence_level=evidence_level,
            consensus_score=consensus,
            monitoring_recommendations=monitoring_recs,
            decision_review_triggers=review_triggers,
        )

    def _analyze_surgery_component(
        self, case: IntegratedCase
    ) -> GastricSurgeryAnalysis | None:
        """Analyze surgery component if available."""
        if not case.gastric_surgery_case:
            return None
        return self.gastric_module.analyze_case(case.gastric_surgery_case)

    def _analyze_flot_component(self, case: IntegratedCase) -> FLOTAnalysis | None:
        """Analyze FLOT component if available."""
        if not case.flot_case:
            return None
        return self.flot_module.analyze_flot_case(case.flot_case)

    def _determine_decision_class(
        self,
        case: IntegratedCase,
        surgery_analysis: GastricSurgeryAnalysis | None,
        flot_analysis: FLOTAnalysis | None,
    ) -> DecisionClass:
        """Determine primary decision class."""
        # Get staging information
        if case.gastric_surgery_case:
            t_stage = case.gastric_surgery_case.tumor_stage.value
            n_stage = case.gastric_surgery_case.node_stage.value
            m_stage = case.gastric_surgery_case.metastasis_stage.value
        elif case.flot_case:
            t_stage = case.flot_case.initial_t_stage.value
            n_stage = case.flot_case.initial_n_stage.value
            m_stage = case.flot_case.initial_m_stage.value
        else:
            return DecisionClass.SURVEILLANCE  # Default if no staging available

        # Decision logic based on staging and patient factors

        # Metastatic disease
        if m_stage.startswith("M1"):
            return DecisionClass.PALLIATIVE

        # Very early disease
        if t_stage in ["T1", "T1a"] and n_stage == "N0":
            return DecisionClass.SURGICAL_ONLY

        # Early disease with some nodal involvement
        if t_stage in ["T1b", "T2"] and n_stage in ["N0", "N1"]:
            # Consider patient factors
            if (
                case.age
                and case.age > 75
                and case.performance_status
                and case.performance_status >= 2
            ):
                return DecisionClass.SURGICAL_ONLY
            return DecisionClass.NEOADJUVANT_SURGERY

        # Locally advanced disease
        if t_stage in ["T3", "T4", "T4a", "T4b"] or n_stage in [
            "N2",
            "N3",
            "N3a",
            "N3b",
        ]:
            return DecisionClass.PERIOPERATIVE

        # Default to neoadjuvant approach
        return DecisionClass.NEOADJUVANT_SURGERY

    def _determine_treatment_sequence(
        self,
        case: IntegratedCase,
        surgery_analysis: GastricSurgeryAnalysis | None,
        flot_analysis: FLOTAnalysis | None,
    ) -> TreatmentSequence:
        """Determine optimal treatment sequence."""
        decision_class = self._determine_decision_class(
            case, surgery_analysis, flot_analysis
        )

        if decision_class == DecisionClass.SURGICAL_ONLY:
            return TreatmentSequence.SURGERY_FIRST
        if decision_class == DecisionClass.NEOADJUVANT_SURGERY:
            return TreatmentSequence.FLOT_THEN_SURGERY
        if decision_class == DecisionClass.PERIOPERATIVE:
            return TreatmentSequence.FLOT_SURGERY_FLOT
        if decision_class == DecisionClass.PALLIATIVE:
            # Check resectability for palliative surgery
            if surgery_analysis and surgery_analysis.surgical_risk_score < 60:
                return TreatmentSequence.FLOT_THEN_SURGERY
            return TreatmentSequence.FLOT_ONLY
        return TreatmentSequence.BEST_SUPPORTIVE_CARE

    def _generate_rationale(
        self,
        case: IntegratedCase,
        decision_class: DecisionClass,
        sequence: TreatmentSequence,
    ) -> str:
        """Generate rationale for treatment recommendation."""
        staging_info = ""
        if case.gastric_surgery_case:
            staging_info = f"T{case.gastric_surgery_case.tumor_stage.value}N{case.gastric_surgery_case.node_stage.value}M{case.gastric_surgery_case.metastasis_stage.value}"
        elif case.flot_case:
            staging_info = f"T{case.flot_case.initial_t_stage.value}N{case.flot_case.initial_n_stage.value}M{case.flot_case.initial_m_stage.value}"

        base_rationale = f"Based on staging ({staging_info})"

        if decision_class == DecisionClass.SURGICAL_ONLY:
            return f"{base_rationale}, early-stage disease is best treated with upfront surgery"
        if decision_class == DecisionClass.NEOADJUVANT_SURGERY:
            return (
                f"{base_rationale}, neoadjuvant therapy may improve surgical outcomes"
            )
        if decision_class == DecisionClass.PERIOPERATIVE:
            return f"{base_rationale}, perioperative therapy is standard for locally advanced disease"
        if decision_class == DecisionClass.PALLIATIVE:
            return f"{base_rationale}, metastatic disease requires systemic therapy approach"
        return (
            f"{base_rationale}, surveillance is appropriate for current disease status"
        )

    def _generate_surgery_recommendation(
        self, case: IntegratedCase, surgery_analysis: GastricSurgeryAnalysis | None
    ) -> str | None:
        """Generate specific surgery recommendation."""
        if not surgery_analysis:
            return None

        approach = surgery_analysis.recommended_approach.value
        gastrectomy = surgery_analysis.recommended_gastrectomy.value

        return f"Recommended: {gastrectomy} via {approach} approach"

    def _generate_chemotherapy_recommendation(
        self, case: IntegratedCase, flot_analysis: FLOTAnalysis | None
    ) -> str | None:
        """Generate specific chemotherapy recommendation."""
        if not case.flot_case:
            return "FLOT protocol (4 cycles preoperative, 4 cycles postoperative)"

        if flot_analysis:
            if flot_analysis.additional_therapy_needed:
                return "Modified FLOT protocol with dose adjustments based on toxicity profile"
            return "Standard FLOT protocol as per analysis"

        return "FLOT protocol with monitoring"

    def _generate_timing_recommendations(
        self, case: IntegratedCase, sequence: TreatmentSequence
    ) -> dict[str, str]:
        """Generate timing recommendations."""
        timing = {}

        if sequence == TreatmentSequence.SURGERY_FIRST:
            timing["surgery"] = "Within 4-6 weeks"
            timing["adjuvant"] = "Within 8-12 weeks post-surgery if indicated"
        elif sequence == TreatmentSequence.FLOT_THEN_SURGERY:
            timing["neoadjuvant"] = "4 cycles FLOT (12 weeks)"
            timing["surgery"] = "4-6 weeks after completion of neoadjuvant therapy"
        elif sequence == TreatmentSequence.FLOT_SURGERY_FLOT:
            timing["preoperative"] = "4 cycles FLOT (12 weeks)"
            timing["surgery"] = "4-6 weeks after preoperative therapy"
            timing["postoperative"] = "6-8 weeks after surgery (4 cycles FLOT)"
        elif sequence == TreatmentSequence.FLOT_ONLY:
            timing["chemotherapy"] = "Initiate within 2-4 weeks"
            timing["restaging"] = "Every 2-3 cycles"

        return timing

    def _calculate_overall_risk(
        self,
        case: IntegratedCase,
        surgery_analysis: GastricSurgeryAnalysis | None,
        flot_analysis: FLOTAnalysis | None,
    ) -> float:
        """Calculate integrated overall risk score."""
        risk_components = []

        # Surgery risk component
        if surgery_analysis:
            risk_components.append(surgery_analysis.surgical_risk_score)

        # Chemotherapy risk component
        if flot_analysis:
            risk_components.append(flot_analysis.toxicity_burden_score)

        # Patient factor risk
        patient_risk = 0
        if case.age and case.age > 70:
            patient_risk += 20
        if case.performance_status and case.performance_status >= 2:
            patient_risk += 30
        if len(case.comorbidities) > 2:
            patient_risk += 15

        risk_components.append(min(patient_risk, 100))

        # Weighted average
        if len(risk_components) > 1:
            return sum(risk_components) / len(risk_components)
        if risk_components:
            return risk_components[0]
        return 50  # Default moderate risk

    def _predict_survival(
        self,
        case: IntegratedCase,
        surgery_analysis: GastricSurgeryAnalysis | None,
        flot_analysis: FLOTAnalysis | None,
    ) -> float | None:
        """Predict overall survival in months."""
        # Base survival estimates by stage
        if case.gastric_surgery_case:
            t_stage = case.gastric_surgery_case.tumor_stage.value
            m_stage = case.gastric_surgery_case.metastasis_stage.value
        elif case.flot_case:
            t_stage = case.flot_case.initial_t_stage.value
            m_stage = case.flot_case.initial_m_stage.value
        else:
            return None

        # Base survival by stage
        if m_stage.startswith("M1"):
            base_survival = 15  # Metastatic disease
        elif t_stage in ["T4", "T4a", "T4b"]:
            base_survival = 36  # Locally advanced
        elif t_stage in ["T2", "T3"]:
            base_survival = 60  # Intermediate stage
        else:
            base_survival = 84  # Early stage

        # Adjust for treatment response
        if flot_analysis and flot_analysis.response_score:
            if flot_analysis.response_score >= 80:
                base_survival *= 1.3
            elif flot_analysis.response_score >= 60:
                base_survival *= 1.2
            elif flot_analysis.response_score < 40:
                base_survival *= 0.8

        # Adjust for surgical quality
        if surgery_analysis and surgery_analysis.resection_quality_score:
            if surgery_analysis.resection_quality_score >= 80:
                base_survival *= 1.2
            elif surgery_analysis.resection_quality_score < 60:
                base_survival *= 0.9

        # Adjust for patient factors
        if case.age and case.age > 75:
            base_survival *= 0.85
        if case.performance_status and case.performance_status >= 2:
            base_survival *= 0.8

        return round(base_survival, 1)

    def _predict_progression_free_survival(
        self,
        case: IntegratedCase,
        surgery_analysis: GastricSurgeryAnalysis | None,
        flot_analysis: FLOTAnalysis | None,
    ) -> float | None:
        """Predict progression-free survival in months."""
        overall_survival = self._predict_survival(case, surgery_analysis, flot_analysis)
        if overall_survival:
            # PFS is typically 60-80% of OS for gastric cancer
            return round(overall_survival * 0.7, 1)
        return None

    def _predict_quality_of_life(
        self,
        case: IntegratedCase,
        surgery_analysis: GastricSurgeryAnalysis | None,
        flot_analysis: FLOTAnalysis | None,
    ) -> float | None:
        """Predict quality of life score."""
        base_qol = 70  # Base QoL score

        # Adjust for treatment toxicity
        if flot_analysis:
            if flot_analysis.toxicity_burden_score > 60:
                base_qol -= 20
            elif flot_analysis.toxicity_burden_score < 30:
                base_qol += 10

        # Adjust for surgical approach
        if surgery_analysis:
            if surgery_analysis.recommended_approach.value == "laparoscopic":
                base_qol += 10
            elif surgery_analysis.recommended_approach.value == "open":
                base_qol -= 5

        # Adjust for performance status
        if case.performance_status:
            if case.performance_status == 0:
                base_qol += 15
            elif case.performance_status >= 2:
                base_qol -= 25

        return max(20, min(base_qol, 100))

    def _generate_alternatives(
        self, case: IntegratedCase, decision_class: DecisionClass
    ) -> list[str]:
        """Generate alternative treatment approaches."""
        alternatives = []

        if decision_class == DecisionClass.SURGICAL_ONLY:
            alternatives.extend(
                [
                    "Surveillance with delayed surgery",
                    "Adjuvant chemotherapy post-surgery",
                ]
            )
        elif decision_class == DecisionClass.NEOADJUVANT_SURGERY:
            alternatives.extend(["Upfront surgery", "Perioperative chemotherapy"])
        elif decision_class == DecisionClass.PERIOPERATIVE:
            alternatives.extend(
                ["Neoadjuvant therapy only", "Modified chemotherapy regimen"]
            )
        elif decision_class == DecisionClass.PALLIATIVE:
            alternatives.extend(
                ["Best supportive care", "Palliative surgery", "Immunotherapy if MSI-H"]
            )

        return alternatives

    def _identify_contraindications(self, case: IntegratedCase) -> list[str]:
        """Identify treatment contraindications."""
        contraindications = []

        if case.performance_status and case.performance_status >= 3:
            contraindications.append(
                "Poor performance status limits aggressive therapy"
            )

        if case.age and case.age > 80 and len(case.comorbidities) > 2:
            contraindications.append("Advanced age with multiple comorbidities")

        # Add specific contraindications based on case details
        if "heart_failure" in case.comorbidities:
            contraindications.append(
                "Heart failure may contraindicate anthracycline-based therapy"
            )

        if "renal_failure" in case.comorbidities:
            contraindications.append(
                "Renal dysfunction may limit platinum-based therapy"
            )

        return contraindications

    def _calculate_integrated_confidence(
        self,
        case: IntegratedCase,
        surgery_analysis: GastricSurgeryAnalysis | None,
        flot_analysis: FLOTAnalysis | None,
    ) -> float:
        """Calculate integrated confidence score."""
        confidence_components = []

        if surgery_analysis:
            confidence_components.append(surgery_analysis.confidence_score)

        if flot_analysis:
            confidence_components.append(flot_analysis.confidence_score)

        # Data completeness factor
        completeness = 0.5  # Base
        if case.gastric_surgery_case:
            completeness += 0.2
        if case.flot_case:
            completeness += 0.2
        if case.age and case.performance_status:
            completeness += 0.1

        confidence_components.append(completeness)

        return sum(confidence_components) / len(confidence_components)

    def _assess_integrated_evidence(
        self,
        case: IntegratedCase,
        surgery_analysis: GastricSurgeryAnalysis | None,
        flot_analysis: FLOTAnalysis | None,
    ) -> EvidenceLevel:
        """Assess integrated evidence level."""
        # High-quality evidence scenarios
        if (
            surgery_analysis
            and flot_analysis
            and (
                surgery_analysis.evidence_level == "High"
                and flot_analysis.evidence_level == "High"
            )
        ):
            return EvidenceLevel.HIGH

        # Moderate evidence
        if surgery_analysis and surgery_analysis.evidence_level in ["High", "Moderate"]:
            return EvidenceLevel.MODERATE

        if flot_analysis and flot_analysis.evidence_level in ["High", "Moderate"]:
            return EvidenceLevel.MODERATE

        # Limited evidence
        return EvidenceLevel.LOW

    def _calculate_consensus_score(self, case: IntegratedCase) -> float:
        """Calculate multidisciplinary consensus score."""
        consensus = 0.7  # Base consensus

        # Increase consensus if multiple specialists agree
        if (
            case.surgeon_preference
            and case.oncologist_recommendation
            and (
                "surgery" in case.surgeon_preference.lower()
                and "surgery" in case.oncologist_recommendation.lower()
            )
        ):
            consensus += 0.2

        # Patient preference alignment
        if case.patient_preference:
            consensus += 0.1

        return min(consensus, 1.0)

    def _generate_monitoring_recommendations(
        self, case: IntegratedCase, sequence: TreatmentSequence
    ) -> list[str]:
        """Generate monitoring recommendations."""
        monitoring = []

        if sequence in [
            TreatmentSequence.FLOT_THEN_SURGERY,
            TreatmentSequence.FLOT_SURGERY_FLOT,
        ]:
            monitoring.extend(
                [
                    "Complete blood count before each cycle",
                    "Comprehensive metabolic panel every 2 cycles",
                    "Performance status assessment before each cycle",
                    "Restaging imaging after neoadjuvant therapy",
                ]
            )

        if sequence in [
            TreatmentSequence.SURGERY_FIRST,
            TreatmentSequence.FLOT_THEN_SURGERY,
            TreatmentSequence.FLOT_SURGERY_FLOT,
        ]:
            monitoring.extend(
                [
                    "Post-operative complications monitoring",
                    "Nutritional status assessment",
                    "Regular imaging for recurrence surveillance",
                ]
            )

        monitoring.append("Quality of life assessments")

        return monitoring

    def _generate_review_triggers(
        self, case: IntegratedCase, sequence: TreatmentSequence
    ) -> list[str]:
        """Generate decision review triggers."""
        triggers = [
            "Disease progression on imaging",
            "Unacceptable toxicity (Grade 3+ persistent)",
            "Significant performance status decline",
            "Patient preference change",
        ]

        if sequence in [
            TreatmentSequence.FLOT_THEN_SURGERY,
            TreatmentSequence.FLOT_SURGERY_FLOT,
        ]:
            triggers.extend(
                [
                    "Poor response to neoadjuvant therapy",
                    "Surgical complications affecting adjuvant therapy timing",
                ]
            )

        return triggers

    def create_gastric_oncology_strategy(self) -> dict[str, Any]:
        """Create gastric-oncology specific decision strategy for the precision engine.
        Inputs: case + new entities + lab/biomarker panel
        Outputs: scores + explanations + confidence.
        """
        from apps.surge.core.models.medical import (
            GastricSystem,
            IndependentCellEntity,
            TumorUnit,
        )

        from .chemo_flot import analyze_flot_regimen
        from .gastric_surgery import analyze_gastrectomy_case

        strategy = {
            "strategy_id": "gastric-oncology",
            "version": "1.0.0",
            "description": "Precision decision strategy for gastric cancer management",
            "domains": ["surgery", "oncology", "pathology"],
            "biomarker_panel": [
                "HER2",
                "MSI",
                "PD-L1",
                "Ki-67",
                "p53",
                "E-cadherin",
                "MLH1",
                "MSH2",
                "MSH6",
                "PMS2",
            ],
        }

        def analyze_integrated_gastric_case(
            case: IntegratedCase,
            gastric_system: GastricSystem | None = None,
            tumor_unit: TumorUnit | None = None,
            cell_entity: IndependentCellEntity | None = None,
        ) -> dict[str, Any]:
            """Analyze integrated gastric case with new entity models."""
            analysis = {
                "case_id": case.case_id,
                "strategy": "gastric-oncology",
                "analysis_timestamp": datetime.now().isoformat(),
            }

            # Multi-modal entity analysis
            entity_analysis = {}

            if gastric_system:
                entity_analysis["gastric_system"] = {
                    "functional_status": gastric_system.functional_status,
                    "anatomical_fitness": _assess_anatomical_fitness(gastric_system),
                    "surgical_candidacy": _assess_surgical_candidacy(gastric_system),
                    "risk_factors": _identify_system_risk_factors(gastric_system),
                }

            if tumor_unit:
                entity_analysis["tumor_unit"] = {
                    "staging_completeness": _assess_staging_completeness(tumor_unit),
                    "molecular_profile": _analyze_molecular_profile(tumor_unit),
                    "resectability": _assess_resectability(tumor_unit),
                    "biomarker_scores": _calculate_biomarker_scores(tumor_unit),
                }

            if cell_entity:
                entity_analysis["cellular_analysis"] = {
                    "proliferation_index": _analyze_proliferation(cell_entity),
                    "immune_profile": _analyze_immune_markers(cell_entity),
                    "targeted_therapy_targets": _identify_therapy_targets(cell_entity),
                    "mismatch_repair_status": _assess_mmr_status(cell_entity),
                }

            analysis["entity_analysis"] = entity_analysis

            # Integrated treatment pathway analysis
            if case.gastric_surgery_case:
                surgery_analysis = analyze_gastrectomy_case(case.gastric_surgery_case)
                analysis["surgery_metrics"] = surgery_analysis

            if case.flot_case:
                flot_analysis = analyze_flot_regimen(case.flot_case)
                analysis["chemotherapy_metrics"] = flot_analysis

            # Precision scoring
            precision_scores = _calculate_precision_scores(
                case,
                entity_analysis,
                analysis.get("surgery_metrics"),
                analysis.get("chemotherapy_metrics"),
            )
            analysis["precision_scores"] = precision_scores

            # Risk stratification
            risk_assessment = _perform_risk_stratification(
                case, entity_analysis, precision_scores
            )
            analysis["risk_assessment"] = risk_assessment

            # Treatment recommendations
            recommendations = _generate_precision_recommendations(
                case, entity_analysis, precision_scores, risk_assessment
            )
            analysis["recommendations"] = recommendations

            # Expected outcomes
            outcome_projections = _project_outcomes(
                case, entity_analysis, precision_scores, risk_assessment
            )
            analysis["outcome_projections"] = outcome_projections

            # Confidence assessment
            confidence_metrics = _assess_decision_confidence(
                case, entity_analysis, analysis
            )
            analysis["confidence_metrics"] = confidence_metrics

            return analysis

        # Helper functions for entity analysis
        def _assess_anatomical_fitness(gastric_system: GastricSystem) -> dict[str, Any]:
            """Assess anatomical fitness for surgery."""
            fitness_score = 100

            if gastric_system.functional_status == "severely_compromised":
                fitness_score -= 40
            elif gastric_system.functional_status == "impaired":
                fitness_score -= 20

            if (
                gastric_system.wall_thickness_mm
                and gastric_system.wall_thickness_mm > 15
            ):
                fitness_score -= 10

            involved_regions = len(gastric_system.involved_regions)
            if involved_regions >= 4:
                fitness_score -= 20
            elif involved_regions >= 2:
                fitness_score -= 10

            return {
                "fitness_score": max(fitness_score, 0),
                "category": (
                    "excellent"
                    if fitness_score >= 85
                    else "good"
                    if fitness_score >= 70
                    else "fair"
                    if fitness_score >= 50
                    else "poor"
                ),
                "limiting_factors": _identify_limiting_factors(gastric_system),
            }

        def _assess_surgical_candidacy(gastric_system: GastricSystem) -> dict[str, Any]:
            """Assess surgical candidacy."""
            candidacy_factors = {
                "functional_reserve": gastric_system.functional_status
                != "severely_compromised",
                "anatomical_variants": len(gastric_system.anatomical_variants) == 0,
                "prior_interventions": len(gastric_system.prior_interventions) <= 1,
                "vascular_supply": gastric_system.vascular_supply != "compromised",
            }

            candidacy_score = (
                sum(candidacy_factors.values()) / len(candidacy_factors) * 100
            )

            return {
                "candidacy_score": candidacy_score,
                "factors": candidacy_factors,
                "recommendation": (
                    "excellent_candidate"
                    if candidacy_score >= 90
                    else "good_candidate"
                    if candidacy_score >= 75
                    else "marginal_candidate"
                    if candidacy_score >= 60
                    else "poor_candidate"
                ),
            }

        def _identify_system_risk_factors(gastric_system: GastricSystem) -> list[str]:
            """Identify system-level risk factors."""
            risk_factors = []

            if gastric_system.functional_status == "severely_compromised":
                risk_factors.append("severe_functional_impairment")

            if len(gastric_system.involved_regions) >= 3:
                risk_factors.append("extensive_anatomical_involvement")

            if gastric_system.prior_interventions:
                risk_factors.append("prior_surgical_history")

            if gastric_system.anatomical_variants:
                risk_factors.append("anatomical_complexity")

            return risk_factors

        def _assess_staging_completeness(tumor_unit: TumorUnit) -> dict[str, Any]:
            """Assess completeness of tumor staging."""
            staging_elements = {
                "t_stage": tumor_unit.t_stage is not None,
                "n_stage": tumor_unit.n_stage is not None,
                "m_stage": tumor_unit.m_stage is not None,
                "histology": tumor_unit.histology_type is not None,
                "grade": tumor_unit.tumor_grade is not None,
                "size": tumor_unit.tumor_size_cm is not None,
                "margins": tumor_unit.resection_margin is not None,
            }

            completeness = sum(staging_elements.values()) / len(staging_elements) * 100

            return {
                "completeness_percentage": completeness,
                "missing_elements": [k for k, v in staging_elements.items() if not v],
                "staging_quality": (
                    "complete"
                    if completeness >= 95
                    else "adequate"
                    if completeness >= 80
                    else "incomplete"
                ),
            }

        def _analyze_molecular_profile(tumor_unit: TumorUnit) -> dict[str, Any]:
            """Analyze molecular characteristics."""
            molecular_features = {
                "her2_status": tumor_unit.her2_status,
                "msi_status": tumor_unit.msi_status,
                "pdl1_expression": tumor_unit.pdl1_expression,
                "ebv_status": tumor_unit.ebv_status,
                "molecular_subtype": tumor_unit.molecular_subtype,
            }

            # Calculate molecular completeness
            available_markers = sum(
                1 for v in molecular_features.values() if v is not None
            )
            total_markers = len(molecular_features)

            # Identify actionable alterations
            actionable_targets = []
            if tumor_unit.her2_status == "positive":
                actionable_targets.append("HER2_targeted_therapy")
            if tumor_unit.msi_status == "MSI-H":
                actionable_targets.append("immunotherapy")
            if tumor_unit.pdl1_expression and tumor_unit.pdl1_expression >= 50:
                actionable_targets.append("PD1_PDL1_blockade")

            return {
                "molecular_features": molecular_features,
                "completeness": available_markers / total_markers * 100,
                "actionable_targets": actionable_targets,
                "therapeutic_implications": len(actionable_targets),
            }

        def _assess_resectability(tumor_unit: TumorUnit) -> dict[str, Any]:
            """Assess tumor resectability."""
            resectability_score = 100

            # T stage impact
            if tumor_unit.t_stage.value in ["T4a", "T4b"]:
                resectability_score -= 30
            elif tumor_unit.t_stage.value == "T3":
                resectability_score -= 10

            # N stage impact
            if tumor_unit.n_stage.value in ["N3a", "N3b"]:
                resectability_score -= 20
            elif tumor_unit.n_stage.value in ["N2", "N3"]:
                resectability_score -= 10

            # M stage impact
            if tumor_unit.m_stage.value in ["M1", "M1a", "M1b"]:
                resectability_score -= 50

            # Size impact
            if tumor_unit.tumor_size_cm and tumor_unit.tumor_size_cm > 10:
                resectability_score -= 15
            elif tumor_unit.tumor_size_cm and tumor_unit.tumor_size_cm > 5:
                resectability_score -= 5

            return {
                "resectability_score": max(resectability_score, 0),
                "category": (
                    "easily_resectable"
                    if resectability_score >= 85
                    else "resectable"
                    if resectability_score >= 70
                    else "borderline_resectable"
                    if resectability_score >= 50
                    else "unresectable"
                ),
                "considerations": _generate_resection_considerations(tumor_unit),
            }

        def _calculate_biomarker_scores(tumor_unit: TumorUnit) -> dict[str, Any]:
            """Calculate biomarker-based scores."""
            scores = {}

            # HER2 score
            if tumor_unit.her2_status:
                scores["her2_actionability"] = (
                    100
                    if tumor_unit.her2_status == "positive"
                    else 30
                    if tumor_unit.her2_status == "equivocal"
                    else 0
                )

            # MSI score
            if tumor_unit.msi_status:
                scores["msi_actionability"] = (
                    100
                    if tumor_unit.msi_status == "MSI-H"
                    else 20
                    if tumor_unit.msi_status == "MSI-L"
                    else 0
                )

            # PD-L1 score
            if tumor_unit.pdl1_expression is not None:
                scores["pdl1_actionability"] = min(tumor_unit.pdl1_expression * 2, 100)

            return scores

        def _analyze_proliferation(
            cell_entity: IndependentCellEntity,
        ) -> dict[str, Any]:
            """Analyze cellular proliferation markers."""
            proliferation_data = {
                "ki67_percentage": cell_entity.ki67_percentage,
                "mitotic_rate": cell_entity.mitotic_rate,
            }

            # Calculate proliferation index
            proliferation_score = 0
            if cell_entity.ki67_percentage:
                proliferation_score = cell_entity.ki67_percentage

            return {
                "proliferation_data": proliferation_data,
                "proliferation_score": proliferation_score,
                "proliferation_category": (
                    "high"
                    if proliferation_score >= 20
                    else "moderate"
                    if proliferation_score >= 10
                    else "low"
                ),
                "therapeutic_implications": (
                    "chemotherapy_sensitive"
                    if proliferation_score >= 15
                    else "chemotherapy_moderate"
                    if proliferation_score >= 8
                    else "chemotherapy_resistant"
                ),
            }

        def _analyze_immune_markers(
            cell_entity: IndependentCellEntity,
        ) -> dict[str, Any]:
            """Analyze immune-related markers."""
            immune_profile = {
                "pdl1_expression": cell_entity.pdl1_expression,
                "pdl1_cps_score": cell_entity.pdl1_cps_score,
                "cd8_til_density": cell_entity.cd8_til_density,
            }

            # Calculate immune score
            immune_score = 0
            if cell_entity.pdl1_expression:
                immune_score += min(cell_entity.pdl1_expression, 50)
            if (
                cell_entity.cd8_til_density
                and "high" in cell_entity.cd8_til_density.lower()
            ):
                immune_score += 30

            return {
                "immune_profile": immune_profile,
                "immune_score": immune_score,
                "immunotherapy_potential": (
                    "high"
                    if immune_score >= 60
                    else "moderate"
                    if immune_score >= 30
                    else "low"
                ),
            }

        def _identify_therapy_targets(cell_entity: IndependentCellEntity) -> list[str]:
            """Identify targeted therapy targets."""
            targets = []

            if cell_entity.her2_expression and cell_entity.her2_expression in [
                "moderate",
                "high",
            ]:
                targets.append("HER2")

            if cell_entity.pdl1_expression and cell_entity.pdl1_expression >= 50:
                targets.append("PD-L1")

            if cell_entity.p53_mutation_status == "mutated":
                targets.append("p53_pathway")

            return targets

        def _assess_mmr_status(cell_entity: IndependentCellEntity) -> dict[str, Any]:
            """Assess mismatch repair status."""
            mmr_proteins = {
                "MLH1": cell_entity.mlh1_expression,
                "MSH2": cell_entity.msh2_expression,
                "MSH6": cell_entity.msh6_expression,
                "PMS2": cell_entity.pms2_expression,
            }

            # Check for deficiency
            deficient_proteins = [
                protein
                for protein, expression in mmr_proteins.items()
                if expression and expression.value == "negative"
            ]

            mmr_status = "deficient" if deficient_proteins else "proficient"

            return {
                "mmr_proteins": mmr_proteins,
                "deficient_proteins": deficient_proteins,
                "mmr_status": mmr_status,
                "msi_prediction": cell_entity.msi_status
                or ("MSI-H" if mmr_status == "deficient" else "MSS"),
                "immunotherapy_indication": mmr_status == "deficient",
            }

        def _calculate_precision_scores(
            case: IntegratedCase,
            entity_analysis: dict,
            surgery_metrics: dict | None,
            chemo_metrics: dict | None,
        ) -> dict[str, Any]:
            """Calculate precision medicine scores."""
            scores = {
                "overall_precision_score": 0,
                "personalization_index": 0,
                "evidence_strength": 0,
                "actionability_score": 0,
            }

            # Calculate based on available data
            component_scores = []

            if entity_analysis.get("tumor_unit"):
                tumor_score = entity_analysis["tumor_unit"].get("biomarker_scores", {})
                if tumor_score:
                    avg_tumor_score = sum(tumor_score.values()) / len(tumor_score)
                    component_scores.append(avg_tumor_score)

            if entity_analysis.get("cellular_analysis"):
                cellular = entity_analysis["cellular_analysis"]
                immune_score = cellular.get("immune_profile", {}).get("immune_score", 0)
                proliferation_score = cellular.get("proliferation_data", {}).get(
                    "proliferation_score", 0
                )
                component_scores.extend([immune_score, proliferation_score])

            if surgery_metrics:
                quality_score = surgery_metrics.get("quality_metrics", {}).get(
                    "quality_percentage", 0
                )
                component_scores.append(quality_score)

            if chemo_metrics:
                overall_score = chemo_metrics.get("overall_assessment", {}).get(
                    "composite_score", 0
                )
                component_scores.append(overall_score)

            if component_scores:
                scores["overall_precision_score"] = sum(component_scores) / len(
                    component_scores
                )
                scores["personalization_index"] = min(
                    scores["overall_precision_score"] * 1.2, 100
                )
                scores["evidence_strength"] = (
                    len(component_scores) / 5 * 100
                )  # Max 5 components
                scores["actionability_score"] = scores["overall_precision_score"] * 0.9

            return scores

        def _perform_risk_stratification(
            case: IntegratedCase,
            entity_analysis: dict,
            precision_scores: dict,
        ) -> dict[str, Any]:
            """Perform comprehensive risk stratification."""
            risk_factors = []
            risk_score = 0

            # Age factor
            if case.age and case.age > 75:
                risk_factors.append("advanced_age")
                risk_score += 15
            elif case.age and case.age > 65:
                risk_score += 8

            # Performance status
            if case.performance_status and case.performance_status >= 2:
                risk_factors.append("poor_performance_status")
                risk_score += 20

            # Comorbidities
            if len(case.comorbidities) >= 3:
                risk_factors.append("multiple_comorbidities")
                risk_score += 15
            elif len(case.comorbidities) >= 1:
                risk_score += 8

            # Tumor factors
            if entity_analysis.get("tumor_unit"):
                resectability = entity_analysis["tumor_unit"].get("resectability", {})
                if resectability.get("category") == "unresectable":
                    risk_factors.append("unresectable_disease")
                    risk_score += 30
                elif resectability.get("category") == "borderline_resectable":
                    risk_factors.append("borderline_resectable")
                    risk_score += 15

            # System factors
            if entity_analysis.get("gastric_system"):
                fitness = entity_analysis["gastric_system"].get(
                    "anatomical_fitness", {}
                )
                if fitness.get("category") == "poor":
                    risk_factors.append("poor_anatomical_fitness")
                    risk_score += 25

            # Determine risk tier
            if risk_score >= 60:
                risk_tier = "high"
            elif risk_score >= 30:
                risk_tier = "moderate"
            else:
                risk_tier = "low"

            return {
                "risk_score": risk_score,
                "risk_tier": risk_tier,
                "risk_factors": risk_factors,
                "mitigation_strategies": _generate_risk_mitigation(risk_factors),
            }

        def _generate_precision_recommendations(
            case: IntegratedCase,
            entity_analysis: dict,
            precision_scores: dict,
            risk_assessment: dict,
        ) -> dict[str, Any]:
            """Generate precision medicine recommendations."""
            recommendations = {
                "primary_treatment": None,
                "adjuvant_therapy": None,
                "targeted_therapy": [],
                "monitoring": [],
                "next_steps": [],
                "rationale": [],
            }

            # Primary treatment recommendation
            if (
                entity_analysis.get("gastric_system", {})
                .get("surgical_candidacy", {})
                .get("recommendation")
                == "excellent_candidate"
            ):
                if entity_analysis.get("tumor_unit", {}).get("resectability", {}).get(
                    "category"
                ) in [
                    "easily_resectable",
                    "resectable",
                ]:
                    recommendations["primary_treatment"] = "upfront_surgery"
                    recommendations["rationale"].append(
                        "Excellent surgical candidate with resectable disease"
                    )
                else:
                    recommendations["primary_treatment"] = "neoadjuvant_therapy"
                    recommendations["rationale"].append(
                        "Surgical candidate requiring disease downstaging"
                    )
            else:
                recommendations["primary_treatment"] = "systemic_therapy"
                recommendations["rationale"].append("Systemic therapy indicated")

            # Targeted therapy recommendations
            molecular_targets = (
                entity_analysis.get("tumor_unit", {})
                .get("molecular_profile", {})
                .get("actionable_targets", [])
            )
            cellular_targets = entity_analysis.get("cellular_analysis", {}).get(
                "targeted_therapy_targets", []
            )

            all_targets = list(set(molecular_targets + cellular_targets))

            for target in all_targets:
                if target == "HER2_targeted_therapy":
                    recommendations["targeted_therapy"].append(
                        "Trastuzumab-based therapy"
                    )
                elif target == "immunotherapy":
                    recommendations["targeted_therapy"].append(
                        "Pembrolizumab or nivolumab"
                    )
                elif target == "PD1_PDL1_blockade":
                    recommendations["targeted_therapy"].append(
                        "Anti-PD-1/PD-L1 therapy"
                    )

            # Monitoring recommendations
            if risk_assessment["risk_tier"] == "high":
                recommendations["monitoring"].extend(
                    [
                        "Intensive perioperative monitoring",
                        "Enhanced nutritional support",
                        "Early intervention protocols",
                    ]
                )

            # Next steps
            if precision_scores["overall_precision_score"] < 60:
                recommendations["next_steps"].append(
                    "Consider additional molecular testing"
                )

            if (
                entity_analysis.get("tumor_unit", {})
                .get("staging_completeness", {})
                .get("staging_quality")
                == "incomplete"
            ):
                recommendations["next_steps"].append("Complete staging workup")

            return recommendations

        def _project_outcomes(
            case: IntegratedCase,
            entity_analysis: dict,
            precision_scores: dict,
            risk_assessment: dict,
        ) -> dict[str, Any]:
            """Project expected outcomes with confidence ranges."""
            base_outcomes = {
                "overall_survival_months": {"median": 24, "range": [18, 30]},
                "disease_free_survival_months": {"median": 18, "range": [12, 24]},
                "response_rate": {"percentage": 60, "range": [45, 75]},
                "r0_resection_probability": {"percentage": 85, "range": [70, 95]},
            }

            # Modify based on risk assessment
            risk_modifier = {
                "high": 0.7,
                "moderate": 0.85,
                "low": 1.1,
            }[risk_assessment["risk_tier"]]

            # Modify based on precision score
            precision_modifier = (
                1.0 + (precision_scores["overall_precision_score"] - 50) / 100
            )

            # Apply modifiers
            projected_outcomes = {}
            for outcome, values in base_outcomes.items():
                if "months" in outcome:
                    projected_outcomes[outcome] = {
                        "median": round(
                            values["median"] * risk_modifier * precision_modifier, 1
                        ),
                        "range": [
                            round(
                                values["range"][0] * risk_modifier * precision_modifier,
                                1,
                            ),
                            round(
                                values["range"][1] * risk_modifier * precision_modifier,
                                1,
                            ),
                        ],
                    }
                else:
                    projected_outcomes[outcome] = {
                        "percentage": round(
                            values["percentage"] * risk_modifier * precision_modifier, 1
                        ),
                        "range": [
                            round(
                                values["range"][0] * risk_modifier * precision_modifier,
                                1,
                            ),
                            round(
                                values["range"][1] * risk_modifier * precision_modifier,
                                1,
                            ),
                        ],
                    }

            return {
                "projected_outcomes": projected_outcomes,
                "modifiers_applied": {
                    "risk_modifier": risk_modifier,
                    "precision_modifier": precision_modifier,
                },
                "confidence_level": _calculate_outcome_confidence(
                    precision_scores, risk_assessment
                ),
            }

        def _assess_decision_confidence(
            case: IntegratedCase,
            entity_analysis: dict,
            full_analysis: dict,
        ) -> dict[str, Any]:
            """Assess confidence in decision recommendations."""
            confidence_factors = {
                "data_completeness": 0,
                "molecular_characterization": 0,
                "staging_accuracy": 0,
                "risk_assessment_clarity": 0,
                "evidence_base": 0,
            }

            # Data completeness
            total_components = 5
            available_components = sum(
                [
                    1 if case.gastric_surgery_case else 0,
                    1 if case.flot_case else 0,
                    1 if entity_analysis.get("gastric_system") else 0,
                    1 if entity_analysis.get("tumor_unit") else 0,
                    1 if entity_analysis.get("cellular_analysis") else 0,
                ]
            )
            confidence_factors["data_completeness"] = (
                available_components / total_components * 100
            )

            # Molecular characterization
            if entity_analysis.get("tumor_unit"):
                molecular_completeness = (
                    entity_analysis["tumor_unit"]
                    .get("molecular_profile", {})
                    .get("completeness", 0)
                )
                confidence_factors[
                    "molecular_characterization"
                ] = molecular_completeness

            # Staging accuracy
            if entity_analysis.get("tumor_unit"):
                staging_completeness = (
                    entity_analysis["tumor_unit"]
                    .get("staging_completeness", {})
                    .get("completeness_percentage", 0)
                )
                confidence_factors["staging_accuracy"] = staging_completeness

            # Risk assessment clarity
            confidence_factors["risk_assessment_clarity"] = (
                100
                - len(full_analysis.get("risk_assessment", {}).get("risk_factors", []))
                * 10
            )

            # Evidence base (simplified)
            confidence_factors[
                "evidence_base"
            ] = 85  # Assume good evidence base for gastric cancer

            # Calculate overall confidence
            overall_confidence = sum(confidence_factors.values()) / len(
                confidence_factors
            )

            return {
                "individual_factors": confidence_factors,
                "overall_confidence": round(overall_confidence, 1),
                "confidence_category": (
                    "high"
                    if overall_confidence >= 80
                    else "moderate"
                    if overall_confidence >= 65
                    else "low"
                ),
                "limiting_factors": [
                    factor for factor, score in confidence_factors.items() if score < 70
                ],
            }

        # Additional helper functions
        def _identify_limiting_factors(gastric_system: GastricSystem) -> list[str]:
            factors = []
            if gastric_system.functional_status in ["impaired", "severely_compromised"]:
                factors.append("functional_impairment")
            if len(gastric_system.involved_regions) >= 3:
                factors.append("extensive_involvement")
            if gastric_system.prior_interventions:
                factors.append("surgical_history")
            return factors

        def _generate_resection_considerations(tumor_unit: TumorUnit) -> list[str]:
            considerations = []
            if tumor_unit.t_stage.value in ["T4a", "T4b"]:
                considerations.append("T4_disease_requires_extended_resection")
            if tumor_unit.tumor_size_cm and tumor_unit.tumor_size_cm > 5:
                considerations.append("large_tumor_size")
            if tumor_unit.n_stage.value in ["N3a", "N3b"]:
                considerations.append("extensive_nodal_involvement")
            return considerations

        def _generate_risk_mitigation(risk_factors: list[str]) -> list[str]:
            mitigation = []
            if "advanced_age" in risk_factors:
                mitigation.append("Geriatric assessment and optimization")
            if "poor_performance_status" in risk_factors:
                mitigation.append("Performance status improvement strategies")
            if "multiple_comorbidities" in risk_factors:
                mitigation.append("Multidisciplinary medical optimization")
            return mitigation

        def _calculate_outcome_confidence(
            precision_scores: dict, risk_assessment: dict
        ) -> str:
            if (
                precision_scores["overall_precision_score"] >= 80
                and risk_assessment["risk_tier"] == "low"
            ):
                return "high"
            if precision_scores["overall_precision_score"] >= 60 and risk_assessment[
                "risk_tier"
            ] in ["low", "moderate"]:
                return "moderate"
            return "low"

        strategy["analyze_function"] = analyze_integrated_gastric_case

        return strategy


# Comprehensive analytics functions
def analyze_precision_decisions(cases: list[IntegratedCase]) -> dict[str, Any]:
    """Analyze precision decisions across a cohort."""
    if not cases:
        return {"error": "No cases provided"}

    engine = PrecisionDecisionEngine()
    decisions = [engine.analyze_integrated_case(case) for case in cases]

    # Decision class distribution
    decision_classes = [d.decision_class.value for d in decisions]
    sequence_distribution = [d.recommended_sequence.value for d in decisions]

    # Risk stratification
    low_risk = [d for d in decisions if d.overall_risk_score <= 30]
    moderate_risk = [d for d in decisions if 30 < d.overall_risk_score <= 60]
    high_risk = [d for d in decisions if d.overall_risk_score > 60]

    # Confidence metrics
    high_confidence = [d for d in decisions if d.confidence_score >= 0.8]
    consensus_achieved = [d for d in decisions if d.consensus_score >= 0.8]

    return {
        "cohort_summary": {
            "total_cases": len(cases),
            "average_risk_score": sum(d.overall_risk_score for d in decisions)
            / len(decisions),
            "average_confidence": sum(d.confidence_score for d in decisions)
            / len(decisions),
        },
        "decision_distribution": {
            "decision_classes": {
                dc: decision_classes.count(dc) for dc in set(decision_classes)
            },
            "treatment_sequences": {
                seq: sequence_distribution.count(seq)
                for seq in set(sequence_distribution)
            },
        },
        "risk_stratification": {
            "low_risk_cases": len(low_risk),
            "moderate_risk_cases": len(moderate_risk),
            "high_risk_cases": len(high_risk),
        },
        "quality_metrics": {
            "high_confidence_rate": len(high_confidence) / len(decisions),
            "consensus_achievement_rate": len(consensus_achieved) / len(decisions),
            "evidence_level_distribution": {
                level.value: sum(1 for d in decisions if d.evidence_level == level)
                for level in EvidenceLevel
            },
        },
        "outcome_predictions": {
            "average_predicted_survival": _safe_average(
                [
                    d.predicted_survival_months
                    for d in decisions
                    if d.predicted_survival_months
                ]
            ),
            "average_predicted_qol": _safe_average(
                [
                    d.predicted_quality_of_life
                    for d in decisions
                    if d.predicted_quality_of_life
                ]
            ),
        },
    }


def optimize_decision_algorithms(cases: list[IntegratedCase]) -> dict[str, Any]:
    """Optimize decision algorithms based on outcomes."""
    if not cases:
        return {"error": "No cases provided"}

    engine = PrecisionDecisionEngine()
    decisions = [engine.analyze_integrated_case(case) for case in cases]

    # Identify patterns in high-confidence decisions
    high_conf_decisions = [d for d in decisions if d.confidence_score >= 0.8]
    low_conf_decisions = [d for d in decisions if d.confidence_score < 0.6]

    # Analyze decision factors
    return {
        "algorithm_performance": {
            "high_confidence_rate": len(high_conf_decisions) / len(decisions),
            "common_high_confidence_patterns": _analyze_decision_patterns(
                high_conf_decisions
            ),
            "low_confidence_challenges": _analyze_decision_patterns(low_conf_decisions),
        },
        "decision_quality_factors": {
            "data_completeness_impact": _analyze_completeness_impact(cases, decisions),
            "staging_clarity_impact": _analyze_staging_impact(cases, decisions),
        },
        "optimization_recommendations": _generate_optimization_recommendations(
            cases, decisions
        ),
    }


def _safe_average(values: list[float]) -> float | None:
    """Safely calculate average of a list."""
    return sum(values) / len(values) if values else None


def _analyze_decision_patterns(decisions: list[PrecisionDecision]) -> dict[str, Any]:
    """Analyze patterns in decisions."""
    return {
        "most_common_sequence": max(
            {d.recommended_sequence.value for d in decisions},
            key=lambda x: [d.recommended_sequence.value for d in decisions].count(x),
        ),
        "average_risk_score": _safe_average([d.overall_risk_score for d in decisions]),
        "evidence_levels": {
            level.value: sum(1 for d in decisions if d.evidence_level == level)
            for level in EvidenceLevel
        },
    }


def _analyze_completeness_impact(
    cases: list[IntegratedCase], decisions: list[PrecisionDecision]
) -> dict[str, Any]:
    """Analyze impact of data completeness on decision quality."""
    complete_cases = []
    incomplete_cases = []

    for case, decision in zip(cases, decisions, strict=False):
        completeness_score = 0
        if case.gastric_surgery_case:
            completeness_score += 0.5
        if case.flot_case:
            completeness_score += 0.5
        if case.age and case.performance_status:
            completeness_score += 0.2

        if completeness_score >= 0.8:
            complete_cases.append(decision)
        else:
            incomplete_cases.append(decision)

    return {
        "complete_cases_confidence": _safe_average(
            [d.confidence_score for d in complete_cases]
        ),
        "incomplete_cases_confidence": _safe_average(
            [d.confidence_score for d in incomplete_cases]
        ),
        "completeness_benefit": (
            _safe_average([d.confidence_score for d in complete_cases]) or 0
        )
        - (_safe_average([d.confidence_score for d in incomplete_cases]) or 0),
    }


def _analyze_staging_impact(
    cases: list[IntegratedCase], decisions: list[PrecisionDecision]
) -> dict[str, Any]:
    """Analyze impact of staging clarity on decisions."""
    clear_staging = []
    unclear_staging = []

    for case, decision in zip(cases, decisions, strict=False):
        has_clear_staging = (case.gastric_surgery_case is not None) or (
            case.flot_case is not None
        )

        if has_clear_staging:
            clear_staging.append(decision)
        else:
            unclear_staging.append(decision)

    return {
        "clear_staging_confidence": _safe_average(
            [d.confidence_score for d in clear_staging]
        ),
        "unclear_staging_confidence": _safe_average(
            [d.confidence_score for d in unclear_staging]
        ),
    }


def _generate_optimization_recommendations(
    cases: list[IntegratedCase], decisions: list[PrecisionDecision]
) -> list[str]:
    """Generate recommendations for algorithm optimization."""
    recommendations = []

    avg_confidence = _safe_average([d.confidence_score for d in decisions])
    if avg_confidence and avg_confidence < 0.7:
        recommendations.append(
            "Improve data collection protocols to increase decision confidence"
        )

    high_risk_rate = len([d for d in decisions if d.overall_risk_score > 70]) / len(
        decisions
    )
    if high_risk_rate > 0.3:
        recommendations.append(
            "Consider risk mitigation strategies for high-risk patient population"
        )

    low_consensus_rate = len([d for d in decisions if d.consensus_score < 0.6]) / len(
        decisions
    )
    if low_consensus_rate > 0.2:
        recommendations.append(
            "Improve multidisciplinary communication and decision protocols"
        )

    return recommendations
