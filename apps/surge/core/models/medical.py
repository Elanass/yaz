"""Medical Models - Enhanced SurgifyAI medical classifications
Comprehensive SRCC (Signet Ring Cell Carcinoma) support with French terminology
Advanced TNM staging, survival analysis, and treatment protocols.
"""

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from apps.surge.common.pydantic_base import APIModel

from .base import BaseEntity, ConfidenceLevel


class TumorStage(str, Enum):
    """Enhanced TNM Tumor staging classifications."""

    T0 = "T0"
    TIS = "Tis"
    T1 = "T1"
    T1A = "T1a"
    T1B = "T1b"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"
    T4A = "T4a"
    T4B = "T4b"
    TX = "Tx"


class NodeStage(str, Enum):
    """Enhanced TNM Node staging classifications."""

    N0 = "N0"
    N1 = "N1"
    N2 = "N2"
    N3 = "N3"
    N3A = "N3a"
    N3B = "N3b"
    NX = "Nx"


class MetastasisStage(str, Enum):
    """Enhanced TNM Metastasis staging classifications."""

    M0 = "M0"
    M1 = "M1"
    M1A = "M1a"
    M1B = "M1b"
    MX = "Mx"


class TreatmentProtocol(str, Enum):
    """Treatment protocol classifications."""

    FLOT = "FLOT"  # Fluorouracil, Leucovorin, Oxaliplatin, Docetaxel
    XELOX = "XELOX"  # Capecitabine, Oxaliplatin
    ECF = "ECF"  # Epirubicin, Cisplatin, Fluorouracil
    ECX = "ECX"  # Epirubicin, Cisplatin, Capecitabine
    FOLFOX = "FOLFOX"  # Fluorouracil, Leucovorin, Oxaliplatin
    SURGERY_ONLY = "Surgery Only"
    NEOADJUVANT = "Neoadjuvant"
    ADJUVANT = "Adjuvant"


class HistologyType(str, Enum):
    """Histological classifications."""

    ADENOCARCINOMA = "Adenocarcinoma"
    SIGNET_RING = "Signet Ring Cell Carcinoma"
    MUCINOUS = "Mucinous Adenocarcinoma"
    POORLY_DIFFERENTIATED = "Poorly Differentiated"
    WELL_DIFFERENTIATED = "Well Differentiated"
    MODERATELY_DIFFERENTIATED = "Moderately Differentiated"


class SurgicalOutcome(str, Enum):
    """Surgical outcome classifications."""

    COMPLETE = "Complete"
    PARTIAL = "Partial"
    INCOMPLETE = "Incomplete"
    R0 = "R0"  # Complete resection, no residual tumor
    R1 = "R1"  # Microscopic residual tumor
    R2 = "R2"  # Macroscopic residual tumor


class FrenchSymptoms(str, Enum):
    """French medical terminology for symptoms."""

    EPIGASTRALGIE = "Épigastralgie"  # Epigastric pain
    VOMISSEMENT = "Vomissement"  # Vomiting
    DYSPHAGIE = "Dysphagie"  # Dysphagia
    AMAIGRISSEMENT = "Amaigrissement"  # Weight loss
    ASTHENIE = "Asthénie"  # Fatigue
    ANOREXIE = "Anorexie"  # Loss of appetite
    HEMATEMESE = "Hématémèse"  # Hematemesis
    MELENA = "Méléna"  # Melena
    DYSPEPSIE = "Dyspepsie"  # Dyspepsia


class PatientPerformanceStatus(str, Enum):
    """Patient performance status (ECOG scale)."""

    NORMAL = "normal"  # ECOG 0
    RESTRICTED = "restricted"  # ECOG 1
    AMBULATORY = "ambulatory"  # ECOG 2
    SYMPTOMATIC = "symptomatic"  # ECOG 3
    BEDRIDDEN = "bedridden"  # ECOG 4


# Backward compatibility aliases
NodalStatus = NodeStage
MetastasisStatus = MetastasisStage


class ClinicalUserRole(str, Enum):
    """Medical-specific user roles."""

    PATIENT = "patient"
    CLINICIAN = "clinician"
    SURGEON = "surgeon"
    ONCOLOGIST = "oncologist"
    PATHOLOGIST = "pathologist"
    RESEARCHER = "researcher"
    RADIOLOGIST = "radiologist"


class DecisionStatus(str, Enum):
    """Medical decision processing status."""

    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REQUIRES_CONSULTATION = "requires_consultation"
    FAILED = "failed"


# Medical Models
class TNMClassification(BaseModel):
    """TNM staging classification."""

    tumor_stage: TumorStage
    nodal_status: NodalStatus
    metastasis_status: MetastasisStatus
    overall_stage: str | None = None

    class Config:
        from_attributes = True


class PatientInfo(BaseEntity):
    """Patient information model."""

    patient_id: str
    age: int | None = None
    gender: str | None = None
    performance_status: PatientPerformanceStatus | None = None
    medical_history: dict | None = None

    class Config:
        from_attributes = True


class ClinicalDecision(BaseEntity):
    """Clinical decision model."""

    patient_id: str
    decision_type: str
    status: DecisionStatus = DecisionStatus.PENDING
    confidence: ConfidenceLevel | None = None
    recommendations: dict | None = None
    reasoning: str | None = None
    reviewed_by: str | None = None

    class Config:
        from_attributes = True


class TNMStaging(APIModel):
    """Enhanced TNM staging model with validation."""

    tumor: TumorStage
    node: NodeStage
    metastasis: MetastasisStage
    stage_group: str | None = None

    @field_validator("stage_group")
    @classmethod
    def calculate_stage_group(cls, v: str, info) -> str:
        """Calculate overall stage group from TNM components."""
        if info.data and all(
            key in info.data for key in ["tumor", "node", "metastasis"]
        ):
            t, n, m = info.data["tumor"], info.data["node"], info.data["metastasis"]

            # Simplified staging logic (would need full AJCC guidelines)
            if m.value.startswith("M1"):
                return "Stage IV"
            if t.value in ["T4", "T4a", "T4b"] or n.value in ["N3", "N3a", "N3b"]:
                return "Stage III"
            if t.value in ["T2", "T3"] or n.value in ["N1", "N2"]:
                return "Stage II"
            if t.value in ["T1", "T1a", "T1b"]:
                return "Stage I"
            return "Stage Unknown"
        return v

    @property
    def tnm_string(self) -> str:
        """Return formatted TNM string."""
        return f"{self.tumor.value}{self.node.value}{self.metastasis.value}"


class TreatmentProtocolModel(BaseModel):
    """Treatment protocol model with French medical support."""

    protocol: TreatmentProtocol
    cycles_planned: int | None = None
    cycles_completed: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    response: str | None = None
    toxicity_grade: int | None = Field(None, ge=0, le=5)
    dose_modifications: list[str] | None = []

    @property
    def completion_rate(self) -> float | None:
        """Calculate treatment completion rate."""
        if self.cycles_planned and self.cycles_completed:
            return (self.cycles_completed / self.cycles_planned) * 100
        return None


class SurvivalMetrics(BaseModel):
    """Survival analysis metrics for outcomes research."""

    overall_survival_months: float | None = None
    progression_free_survival_months: float | None = None
    disease_free_survival_months: float | None = None
    event_occurred: bool = False
    event_type: str | None = None  # Death, Progression, Recurrence
    last_follow_up: date | None = None
    vital_status: str | None = None  # Alive, Dead, Lost to follow-up

    @property
    def survival_status(self) -> str:
        """Return formatted survival status."""
        if self.vital_status == "Alive" and self.overall_survival_months:
            return f"Alive at {self.overall_survival_months:.1f} months"
        if self.vital_status == "Dead" and self.overall_survival_months:
            return f"Deceased at {self.overall_survival_months:.1f} months"
        return "Status unknown"


class RegionalAnalysis(BaseModel):
    """Regional/geographic analysis model for population studies."""

    region: str | None = None
    country: str | None = None
    institution: str | None = None
    population_density: str | None = None
    healthcare_access_score: float | None = Field(None, ge=0, le=100)
    socioeconomic_index: float | None = Field(None, ge=0, le=100)


class SRCCCase(APIModel):
    """Comprehensive Signet Ring Cell Carcinoma case model."""

    # Patient identifiers
    patient_id: str = Field(..., min_length=1)
    case_id: str | None = None

    # Demographics
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., pattern="^[MF]$")
    bmi: float | None = Field(None, ge=10, le=60)

    # Clinical presentation with French terminology support
    symptoms_french: list[FrenchSymptoms] | None = []
    symptoms_english: list[str] | None = []
    presentation_date: date | None = None
    diagnosis_date: date | None = None

    # Tumor characteristics
    tnm_staging: TNMStaging
    histology: HistologyType
    tumor_size_mm: float | None = Field(None, ge=0)
    tumor_location: str | None = None
    differentiation_grade: str | None = None
    lymphovascular_invasion: bool | None = None
    perineural_invasion: bool | None = None

    # Treatment protocols
    treatment_protocols: list[TreatmentProtocolModel] = []
    surgical_procedure: str | None = None
    surgical_date: date | None = None
    surgical_outcome: SurgicalOutcome | None = None
    resection_margins: str | None = None

    # Outcomes and follow-up
    survival_metrics: SurvivalMetrics | None = None
    complications: list[str] | None = []
    quality_of_life_score: float | None = Field(None, ge=0, le=100)

    # Geographic and institutional data
    regional_data: RegionalAnalysis | None = None

    # Research and collaboration
    study_enrollment: list[str] | None = []
    consent_status: str | None = None
    data_sharing_permissions: dict[str, bool] | None = {}

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None
    created_by: str | None = None
    data_version: str = "1.0"

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "patient_id": "SRCC001",
                "age": 65,
                "gender": "M",
                "tnm_staging": {"tumor": "T3", "node": "N1", "metastasis": "M0"},
                "histology": "Signet Ring Cell Carcinoma",
                "treatment_protocols": [
                    {"protocol": "FLOT", "cycles_planned": 8, "cycles_completed": 8}
                ],
                "surgical_outcome": "Complete",
            }
        },
    )

    @field_validator("case_id")
    @classmethod
    def generate_case_id(cls, v: str, info) -> str:
        """Generate case ID if not provided."""
        if not v and info.data and "patient_id" in info.data:
            return f"CASE_{info.data['patient_id']}_{datetime.now().strftime('%Y%m%d')}"
        return v

    @property
    def stage_summary(self) -> str:
        """Return formatted stage summary."""
        return f"{self.tnm_staging.tnm_string} ({self.tnm_staging.stage_group})"

    @property
    def primary_treatment(self) -> TreatmentProtocolModel | None:
        """Get primary treatment protocol."""
        return self.treatment_protocols[0] if self.treatment_protocols else None

    @property
    def is_high_risk(self) -> bool:
        """Determine if case is high-risk based on staging."""
        high_risk_tumors = ["T3", "T4", "T4a", "T4b"]
        high_risk_nodes = ["N2", "N3", "N3a", "N3b"]
        return (
            self.tnm_staging.tumor.value in high_risk_tumors
            or self.tnm_staging.node.value in high_risk_nodes
            or self.tnm_staging.metastasis.value.startswith("M1")
        )

    def calculate_risk_score(self) -> float:
        """Calculate composite risk score (0-100)."""
        score = 0

        # Age factor (0-20 points)
        if self.age > 70:
            score += 20
        elif self.age > 60:
            score += 10

        # TNM staging (0-40 points)
        if self.tnm_staging.metastasis.value.startswith("M1"):
            score += 40
        elif self.tnm_staging.tumor.value in ["T4", "T4a", "T4b"]:
            score += 30
        elif self.tnm_staging.node.value in ["N3", "N3a", "N3b"]:
            score += 25
        elif self.tnm_staging.tumor.value == "T3":
            score += 20
        elif self.tnm_staging.node.value in ["N1", "N2"]:
            score += 15

        # Histology factor (0-20 points)
        if self.histology == HistologyType.SIGNET_RING:
            score += 15
        elif self.histology == HistologyType.POORLY_DIFFERENTIATED:
            score += 10

        # Complication factor (0-20 points)
        if self.complications:
            score += len(self.complications) * 5

        return min(score, 100)  # Cap at 100


class CohortAnalysis(BaseModel):
    """Cohort-level analysis for research collaboration."""

    cohort_id: str
    name: str
    description: str | None = None
    cases: list[SRCCCase]
    analysis_date: datetime = Field(default_factory=datetime.now)

    @property
    def total_cases(self) -> int:
        """Total number of cases in cohort."""
        return len(self.cases)

    @property
    def median_age(self) -> float:
        """Median age of cohort."""
        ages = [case.age for case in self.cases]
        ages.sort()
        n = len(ages)
        return ages[n // 2] if n % 2 == 1 else (ages[n // 2 - 1] + ages[n // 2]) / 2

    @property
    def gender_distribution(self) -> dict[str, int]:
        """Gender distribution."""
        distribution = {"M": 0, "F": 0}
        for case in self.cases:
            distribution[case.gender] += 1
        return distribution

    @property
    def stage_distribution(self) -> dict[str, int]:
        """Stage distribution."""
        distribution = {}
        for case in self.cases:
            stage = case.tnm_staging.stage_group or "Unknown"
            distribution[stage] = distribution.get(stage, 0) + 1
        return distribution

    @property
    def median_survival(self) -> float | None:
        """Median overall survival in months."""
        survivals = [
            case.survival_metrics.overall_survival_months
            for case in self.cases
            if case.survival_metrics and case.survival_metrics.overall_survival_months
        ]
        if survivals:
            survivals.sort()
            n = len(survivals)
            return (
                survivals[n // 2]
                if n % 2 == 1
                else (survivals[n // 2 - 1] + survivals[n // 2]) / 2
            )
        return None

    def get_treatment_effectiveness(self) -> dict[str, dict[str, Any]]:
        """Analyze treatment effectiveness by protocol."""
        effectiveness = {}

        for case in self.cases:
            for protocol in case.treatment_protocols:
                protocol_name = protocol.protocol.value
                if protocol_name not in effectiveness:
                    effectiveness[protocol_name] = {
                        "cases": 0,
                        "complete_responses": 0,
                        "median_survival": [],
                        "completion_rate": [],
                    }

                effectiveness[protocol_name]["cases"] += 1

                if case.surgical_outcome == SurgicalOutcome.COMPLETE:
                    effectiveness[protocol_name]["complete_responses"] += 1

                if (
                    case.survival_metrics
                    and case.survival_metrics.overall_survival_months
                ):
                    effectiveness[protocol_name]["median_survival"].append(
                        case.survival_metrics.overall_survival_months
                    )

                if protocol.completion_rate:
                    effectiveness[protocol_name]["completion_rate"].append(
                        protocol.completion_rate
                    )

        # Calculate summary statistics
        for protocol_name in effectiveness:
            data = effectiveness[protocol_name]
            data["response_rate"] = (
                (data["complete_responses"] / data["cases"] * 100)
                if data["cases"] > 0
                else 0
            )

            if data["median_survival"]:
                survivals = sorted(data["median_survival"])
                n = len(survivals)
                data["median_survival"] = (
                    survivals[n // 2]
                    if n % 2 == 1
                    else (survivals[n // 2 - 1] + survivals[n // 2]) / 2
                )
            else:
                data["median_survival"] = None

            if data["completion_rate"]:
                data["avg_completion_rate"] = sum(data["completion_rate"]) / len(
                    data["completion_rate"]
                )
            else:
                data["avg_completion_rate"] = None

        return effectiveness


def create_sample_srcc_case() -> SRCCCase:
    """Create a sample SRCC case for testing and demonstration."""
    return SRCCCase(
        patient_id="SRCC_SAMPLE_001",
        age=65,
        gender="M",
        tnm_staging=TNMStaging(
            tumor=TumorStage.T3, node=NodeStage.N1, metastasis=MetastasisStage.M0
        ),
        histology=HistologyType.SIGNET_RING,
        treatment_protocols=[
            TreatmentProtocolModel(
                protocol=TreatmentProtocol.FLOT, cycles_planned=8, cycles_completed=8
            )
        ],
        surgical_outcome=SurgicalOutcome.COMPLETE,
        survival_metrics=SurvivalMetrics(
            overall_survival_months=24.5, vital_status="Alive"
        ),
    )


# === New Entity Models for Extended Surgery Domain ===


class GastricSystemStatus(str, Enum):
    """Gastric system functional status."""

    NORMAL = "normal"
    IMPAIRED = "impaired"
    SEVERELY_COMPROMISED = "severely_compromised"
    POST_SURGICAL = "post_surgical"


class AnatomicalRegion(str, Enum):
    """Gastric anatomical regions."""

    FUNDUS = "fundus"
    BODY = "body"
    ANTRUM = "antrum"
    PYLORUS = "pylorus"
    CARDIA = "cardia"
    GE_JUNCTION = "ge_junction"


class GastricSystem(BaseEntity):
    """Gastric system entity - organ/system level modeling."""

    system_id: str = Field(..., description="Unique gastric system identifier")
    patient_id: str = Field(..., description="Associated patient ID")

    # Anatomical characteristics
    primary_region: AnatomicalRegion = Field(..., description="Primary affected region")
    involved_regions: list[AnatomicalRegion] = Field(
        default=[], description="All involved regions"
    )

    # Functional status
    functional_status: GastricSystemStatus = Field(
        ..., description="Overall functional status"
    )
    gastric_emptying_time: float | None = Field(
        None, ge=0, description="Gastric emptying time in minutes"
    )
    acid_production_level: str | None = Field(
        None, description="Acid production assessment"
    )

    # Structural integrity
    wall_thickness_mm: float | None = Field(
        None, ge=0, description="Gastric wall thickness in mm"
    )
    mucosal_integrity: str | None = Field(
        None, description="Mucosal integrity assessment"
    )
    vascular_supply: str | None = Field(None, description="Vascular supply assessment")

    # Surgical context
    prior_interventions: list[str] = Field(
        default=[], description="Previous gastric interventions"
    )
    anatomical_variants: list[str] = Field(
        default=[], description="Notable anatomical variants"
    )

    # Metadata
    assessment_date: datetime = Field(default_factory=datetime.now)
    assessed_by: str | None = Field(
        None, description="Clinician who performed assessment"
    )


class TumorGrade(str, Enum):
    """Tumor differentiation grade."""

    G1 = "G1"  # Well differentiated
    G2 = "G2"  # Moderately differentiated
    G3 = "G3"  # Poorly differentiated
    G4 = "G4"  # Undifferentiated
    GX = "Gx"  # Cannot be assessed


class ResectionMargin(str, Enum):
    """Surgical resection margin status."""

    R0 = "R0"  # Complete resection, no residual tumor
    R1 = "R1"  # Microscopic residual tumor
    R2 = "R2"  # Macroscopic residual tumor
    RX = "Rx"  # Presence of residual tumor cannot be assessed


class TumorUnit(BaseEntity):
    """Tumor unit entity - tumor phenotype, stage, margins, biomarkers."""

    tumor_id: str = Field(..., description="Unique tumor identifier")
    case_id: str = Field(..., description="Associated case ID")
    patient_id: str = Field(..., description="Associated patient ID")

    # TNM Staging (enhanced)
    t_stage: TumorStage = Field(..., description="Primary tumor stage")
    n_stage: NodeStage = Field(..., description="Regional lymph node stage")
    m_stage: MetastasisStage = Field(..., description="Distant metastasis stage")
    overall_stage: str | None = Field(None, description="Combined TNM stage (I-IV)")

    # Tumor characteristics
    histology_type: HistologyType = Field(..., description="Histological type")
    tumor_grade: TumorGrade = Field(..., description="Tumor differentiation grade")
    primary_location: AnatomicalRegion = Field(
        ..., description="Primary tumor location"
    )

    # Size and extent
    tumor_size_cm: float | None = Field(
        None, ge=0, description="Maximum tumor diameter in cm"
    )
    depth_of_invasion: str | None = Field(
        None, description="Depth of gastric wall invasion"
    )
    lymph_nodes_examined: int | None = Field(
        None, ge=0, description="Total lymph nodes examined"
    )
    lymph_nodes_positive: int | None = Field(
        None, ge=0, description="Positive lymph nodes"
    )

    # Margins and resection
    resection_margin: ResectionMargin | None = Field(
        None, description="Resection margin status"
    )
    proximal_margin_cm: float | None = Field(
        None, ge=0, description="Proximal margin distance in cm"
    )
    distal_margin_cm: float | None = Field(
        None, ge=0, description="Distal margin distance in cm"
    )
    circumferential_margin_mm: float | None = Field(
        None, ge=0, description="Circumferential margin in mm"
    )

    # Biomarkers
    her2_status: str | None = Field(
        None, description="HER2 status (positive/negative/equivocal)"
    )
    her2_score: str | None = Field(None, description="HER2 IHC score (0, 1+, 2+, 3+)")
    msi_status: str | None = Field(
        None, description="Microsatellite instability status"
    )
    pdl1_expression: float | None = Field(
        None, ge=0, le=100, description="PD-L1 expression percentage"
    )
    ebv_status: str | None = Field(None, description="Epstein-Barr virus status")

    # Molecular features
    molecular_subtype: str | None = Field(
        None, description="Molecular subtype classification"
    )
    genetic_alterations: list[str] = Field(
        default=[], description="Identified genetic alterations"
    )
    mutation_burden: str | None = Field(
        None, description="Tumor mutation burden (high/low)"
    )

    # Imaging correlation
    radiological_size_cm: float | None = Field(
        None, ge=0, description="Radiological tumor size in cm"
    )
    imaging_features: list[str] = Field(
        default=[], description="Notable imaging features"
    )

    # Pathology metadata
    pathology_date: datetime | None = Field(
        None, description="Date of pathological examination"
    )
    pathologist: str | None = Field(None, description="Reporting pathologist")
    specimen_type: str | None = Field(None, description="Type of specimen examined")


class CellularMarker(str, Enum):
    """Cellular biomarkers."""

    KI67 = "Ki-67"
    P53 = "p53"
    ECADHERIN = "E-cadherin"
    BETACATENIN = "beta-catenin"
    CDH1 = "CDH1"
    MLH1 = "MLH1"
    MSH2 = "MSH2"
    MSH6 = "MSH6"
    PMS2 = "PMS2"


class ExpressionLevel(str, Enum):
    """Biomarker expression levels."""

    NEGATIVE = "negative"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    INDETERMINATE = "indeterminate"


class IndependentCellEntity(BaseEntity):
    """Independent cell entity - cell-level attributes like HER2, MSI, PD-L1, Ki-67."""

    cell_entity_id: str = Field(..., description="Unique cell entity identifier")
    tumor_id: str = Field(..., description="Associated tumor ID")
    sample_id: str | None = Field(None, description="Tissue sample identifier")

    # Core biomarkers
    her2_expression: ExpressionLevel | None = Field(
        None, description="HER2 protein expression level"
    )
    her2_gene_amplification: bool | None = Field(
        None, description="HER2 gene amplification status"
    )
    her2_fish_ratio: float | None = Field(None, ge=0, description="HER2 FISH ratio")

    # Proliferation markers
    ki67_percentage: float | None = Field(
        None, ge=0, le=100, description="Ki-67 proliferation index"
    )
    mitotic_rate: int | None = Field(None, ge=0, description="Mitotic figures per HPF")

    # Mismatch repair
    mlh1_expression: ExpressionLevel | None = Field(None, description="MLH1 expression")
    msh2_expression: ExpressionLevel | None = Field(None, description="MSH2 expression")
    msh6_expression: ExpressionLevel | None = Field(None, description="MSH6 expression")
    pms2_expression: ExpressionLevel | None = Field(None, description="PMS2 expression")
    msi_status: str | None = Field(
        None, description="Microsatellite instability status"
    )

    # Immune markers
    pdl1_expression: float | None = Field(
        None, ge=0, le=100, description="PD-L1 expression percentage"
    )
    pdl1_cps_score: float | None = Field(
        None, ge=0, description="PD-L1 Combined Positive Score"
    )
    cd8_til_density: str | None = Field(
        None, description="CD8+ T-cell infiltration density"
    )

    # Tumor suppressor
    p53_expression: ExpressionLevel | None = Field(
        None, description="p53 expression level"
    )
    p53_mutation_status: str | None = Field(None, description="p53 mutation status")

    # Adhesion molecules
    e_cadherin_expression: ExpressionLevel | None = Field(
        None, description="E-cadherin expression"
    )
    beta_catenin_pattern: str | None = Field(
        None, description="Beta-catenin staining pattern"
    )

    # Cell cycle markers
    cyclin_d1_expression: ExpressionLevel | None = Field(
        None, description="Cyclin D1 expression"
    )
    rb_expression: ExpressionLevel | None = Field(
        None, description="Rb protein expression"
    )

    # Cellular context
    cell_morphology: str | None = Field(
        None, description="Cellular morphology description"
    )
    tissue_architecture: str | None = Field(
        None, description="Tissue architecture pattern"
    )
    stromal_reaction: str | None = Field(
        None, description="Stromal reaction assessment"
    )

    # Technical details
    staining_method: str | None = Field(
        None, description="Immunohistochemical staining method"
    )
    antibody_clone: str | None = Field(None, description="Antibody clone used")
    analysis_date: datetime = Field(default_factory=datetime.now)
    analyzed_by: str | None = Field(None, description="Pathologist/technician")

    # Quality metrics
    tissue_quality: str | None = Field(None, description="Tissue quality assessment")
    fixation_time: float | None = Field(
        None, ge=0, description="Fixation time in hours"
    )
    processing_protocol: str | None = Field(
        None, description="Tissue processing protocol"
    )
