"""Clinical Data Models
Healthcare-grade Pydantic models for gastric oncology decision support.
"""

from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from surge.core.models.base import BaseEntity, ConfidenceLevel
from surge.core.models.medical import (
    DecisionStatus,
    MetastasisStatus,
    NodalStatus,
    PatientPerformanceStatus,
    TumorStage,
)


class GenderType(str, Enum):
    """Patient gender types."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class BloodType(str, Enum):
    """Blood type classification."""

    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    UNKNOWN = "unknown"


class ComorbidityType(str, Enum):
    """Common comorbidity types in gastric cancer patients."""

    DIABETES = "diabetes"
    HYPERTENSION = "hypertension"
    CARDIOVASCULAR_DISEASE = "cardiovascular_disease"
    CHRONIC_KIDNEY_DISEASE = "chronic_kidney_disease"
    LIVER_DISEASE = "liver_disease"
    PULMONARY_DISEASE = "pulmonary_disease"
    PREVIOUS_MALIGNANCY = "previous_malignancy"
    OBESITY = "obesity"
    SMOKING_HISTORY = "smoking_history"
    ALCOHOL_DEPENDENCY = "alcohol_dependency"


class TumorHistology(str, Enum):
    """Gastric tumor histological types."""

    ADENOCARCINOMA = "adenocarcinoma"
    SIGNET_RING_CELL = "signet_ring_cell"
    MUCINOUS = "mucinous"
    NEUROENDOCRINE = "neuroendocrine"
    LYMPHOMA = "lymphoma"
    GASTROINTESTINAL_STROMAL = "gastrointestinal_stromal"
    OTHER = "other"


class TumorLocation(str, Enum):
    """Gastric tumor anatomical locations."""

    CARDIA = "cardia"
    FUNDUS = "fundus"
    BODY = "body"
    ANTRUM = "antrum"
    PYLORUS = "pylorus"
    GASTROESOPHAGEAL_JUNCTION = "gastroesophageal_junction"
    DIFFUSE = "diffuse"


class SurgicalProcedure(str, Enum):
    """Types of gastric surgical procedures."""

    TOTAL_GASTRECTOMY = "total_gastrectomy"
    SUBTOTAL_GASTRECTOMY = "subtotal_gastrectomy"
    PROXIMAL_GASTRECTOMY = "proximal_gastrectomy"
    PYLORUS_PRESERVING_GASTRECTOMY = "pylorus_preserving_gastrectomy"
    ENDOSCOPIC_RESECTION = "endoscopic_resection"
    PALLIATIVE_BYPASS = "palliative_bypass"


class TreatmentProtocol(str, Enum):
    """Treatment protocol types."""

    FLOT = "flot"  # Fluorouracil, Leucovorin, Oxaliplatin, Docetaxel
    ECF = "ecf"  # Epirubicin, Cisplatin, Fluorouracil
    DCF = "dcf"  # Docetaxel, Cisplatin, Fluorouracil
    FOLFOX = "folfox"  # Leucovorin, Fluorouracil, Oxaliplatin
    SURGERY_ONLY = "surgery_only"
    PALLIATIVE = "palliative"
    BEST_SUPPORTIVE_CARE = "best_supportive_care"


# Core Clinical Models


class PatientDemographics(BaseModel):
    """Patient demographic information."""

    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    gender: GenderType = Field(..., description="Patient gender")
    weight_kg: float | None = Field(
        None, ge=20, le=300, description="Weight in kilograms"
    )
    height_cm: float | None = Field(
        None, ge=100, le=250, description="Height in centimeters"
    )
    blood_type: BloodType | None = Field(None, description="Blood type")
    ethnicity: str | None = Field(None, description="Patient ethnicity")

    @property
    def bmi(self) -> float | None:
        """Calculate BMI if height and weight available."""
        if self.weight_kg and self.height_cm:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m**2), 2)
        return None

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if v < 0 or v > 120:
            msg = "Age must be between 0 and 120"
            raise ValueError(msg)
        return v


class Comorbidity(BaseModel):
    """Patient comorbidity information."""

    type: ComorbidityType = Field(..., description="Type of comorbidity")
    severity: str = Field(..., description="Severity level")
    diagnosed_date: date | None = Field(None, description="Date of diagnosis")
    controlled: bool = Field(
        default=False, description="Whether condition is controlled"
    )
    medications: list[str] = Field(default=[], description="Related medications")

    model_config = ConfigDict(str_strip_whitespace=True)


class TumorCharacteristics(BaseModel):
    """Gastric tumor characteristics."""

    histology: TumorHistology = Field(..., description="Histological type")
    location: TumorLocation = Field(..., description="Tumor location")
    size_mm: float | None = Field(None, ge=0, description="Tumor size in millimeters")
    differentiation: str | None = Field(None, description="Tumor differentiation grade")
    her2_status: bool | None = Field(None, description="HER2 receptor status")
    msi_status: str | None = Field(
        None, description="Microsatellite instability status"
    )
    pdl1_expression: float | None = Field(
        None, ge=0, le=100, description="PD-L1 expression percentage"
    )

    # TNM Staging
    t_stage: TumorStage = Field(..., description="Primary tumor (T) stage")
    n_stage: NodalStatus = Field(..., description="Regional lymph nodes (N) stage")
    m_stage: MetastasisStatus = Field(..., description="Distant metastasis (M) stage")

    @property
    def tnm_stage(self) -> str:
        """Complete TNM staging."""
        return f"{self.t_stage.value}{self.n_stage.value}{self.m_stage.value}"


class LaboratoryResults(BaseModel):
    """Laboratory test results."""

    # Hematology
    hemoglobin_g_dl: float | None = Field(
        None, ge=0, le=25, description="Hemoglobin g/dL"
    )
    white_blood_cells: float | None = Field(None, ge=0, description="WBC count")
    platelets: float | None = Field(None, ge=0, description="Platelet count")

    # Chemistry
    albumin_g_dl: float | None = Field(None, ge=0, le=10, description="Albumin g/dL")
    total_protein_g_dl: float | None = Field(
        None, ge=0, le=15, description="Total protein g/dL"
    )
    creatinine_mg_dl: float | None = Field(
        None, ge=0, le=20, description="Creatinine mg/dL"
    )
    bilirubin_mg_dl: float | None = Field(
        None, ge=0, le=50, description="Total bilirubin mg/dL"
    )

    # Tumor markers
    cea_ng_ml: float | None = Field(None, ge=0, description="CEA ng/mL")
    ca19_9_u_ml: float | None = Field(None, ge=0, description="CA 19-9 U/mL")
    ca72_4_u_ml: float | None = Field(None, ge=0, description="CA 72-4 U/mL")

    # Dates
    collection_date: date | None = Field(None, description="Date of collection")

    model_config = ConfigDict(str_strip_whitespace=True)


class PerformanceStatus(BaseModel):
    """Patient performance and functional status."""

    ecog_status: PatientPerformanceStatus = Field(
        ..., description="ECOG Performance Status"
    )
    karnofsky_score: int | None = Field(
        None, ge=0, le=100, description="Karnofsky Performance Scale"
    )
    weight_loss_percent: float | None = Field(
        None, ge=0, le=100, description="Weight loss percentage"
    )
    nutritional_risk: str | None = Field(
        None, description="Nutritional risk assessment"
    )

    @field_validator("karnofsky_score")
    @classmethod
    def validate_karnofsky(cls, v):
        if v is not None and (v < 0 or v > 100 or v % 10 != 0):
            msg = "Karnofsky score must be 0-100 in increments of 10"
            raise ValueError(msg)
        return v


class Patient(BaseEntity):
    """Complete patient model for gastric cancer care."""

    # Identifiers
    medical_record_number: str = Field(..., description="Medical record number")
    external_id: str | None = Field(None, description="External system identifier")

    # Demographics
    demographics: PatientDemographics = Field(..., description="Patient demographics")

    # Medical history
    comorbidities: list[Comorbidity] = Field(
        default=[], description="Patient comorbidities"
    )
    family_history: dict[str, bool] = Field(
        default={}, description="Family history of cancer"
    )
    social_history: dict[str, str] = Field(default={}, description="Social history")

    # Current condition
    tumor_characteristics: TumorCharacteristics | None = Field(
        None, description="Tumor details"
    )
    performance_status: PerformanceStatus | None = Field(
        None, description="Performance status"
    )
    laboratory_results: list[LaboratoryResults] = Field(
        default=[], description="Lab results"
    )

    # Treatment history
    previous_treatments: list[str] = Field(
        default=[], description="Previous treatment history"
    )
    current_medications: list[str] = Field(
        default=[], description="Current medications"
    )

    # Consent and privacy
    consent_research: bool = Field(
        default=False, description="Research participation consent"
    )
    privacy_level: str = Field(
        default="standard", description="Privacy protection level"
    )

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, use_enum_values=True
    )


class TreatmentPlan(BaseEntity):
    """Treatment plan for gastric cancer patient."""

    patient_id: UUID = Field(..., description="Associated patient ID")

    # Treatment details
    protocol: TreatmentProtocol = Field(..., description="Treatment protocol")
    surgical_procedure: SurgicalProcedure | None = Field(
        None, description="Planned surgery"
    )

    # Scheduling
    planned_start_date: date | None = Field(None, description="Planned treatment start")
    estimated_duration_weeks: int | None = Field(
        None, ge=1, description="Estimated duration"
    )

    # Team
    primary_surgeon: str | None = Field(None, description="Primary surgeon")
    medical_oncologist: str | None = Field(None, description="Medical oncologist")
    multidisciplinary_team: list[str] = Field(default=[], description="MDT members")

    # Goals and notes
    treatment_intent: str = Field(
        ..., description="Treatment intent (curative/palliative)"
    )
    clinical_notes: str | None = Field(None, description="Clinical notes")

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)


class ADCIDecision(BaseEntity):
    """ADCI Decision Support Result."""

    patient_id: UUID = Field(..., description="Associated patient ID")
    treatment_plan_id: UUID | None = Field(
        None, description="Associated treatment plan"
    )

    # Decision inputs
    input_parameters: dict[str, str | float | int | bool] = Field(
        ..., description="Input parameters"
    )

    # ADCI outputs
    adci_score: float = Field(..., ge=0, le=100, description="ADCI confidence score")
    confidence_level: ConfidenceLevel = Field(
        ..., description="Confidence level category"
    )

    # Recommendations
    recommended_protocol: TreatmentProtocol = Field(
        ..., description="Recommended treatment"
    )
    alternative_protocols: list[TreatmentProtocol] = Field(
        default=[], description="Alternative options"
    )

    # Supporting data
    evidence_quality: str = Field(..., description="Quality of supporting evidence")
    risk_factors: list[str] = Field(default=[], description="Identified risk factors")
    contraindications: list[str] = Field(
        default=[], description="Treatment contraindications"
    )

    # Decision metadata
    decision_timestamp: datetime = Field(default_factory=datetime.utcnow)
    decision_maker: str = Field(..., description="Clinician making decision")
    status: DecisionStatus = Field(
        default=DecisionStatus.PENDING, description="Decision status"
    )

    # Outcome tracking
    implemented: bool = Field(
        default=False, description="Whether recommendation was implemented"
    )
    outcome_notes: str | None = Field(None, description="Outcome notes")

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
            UUID: lambda uuid: str(uuid),
        },
    )


class ClinicalOutcome(BaseEntity):
    """Patient clinical outcome tracking."""

    patient_id: UUID = Field(..., description="Associated patient ID")
    adci_decision_id: UUID | None = Field(None, description="Associated ADCI decision")

    # Outcome measures
    overall_survival_months: float | None = Field(
        None, ge=0, description="Overall survival"
    )
    disease_free_survival_months: float | None = Field(
        None, ge=0, description="Disease-free survival"
    )
    progression_free_survival_months: float | None = Field(
        None, ge=0, description="Progression-free survival"
    )

    # Quality of life
    quality_of_life_score: float | None = Field(
        None, ge=0, le=100, description="QoL score"
    )
    functional_status_change: str | None = Field(
        None, description="Functional status change"
    )

    # Complications
    complications: list[str] = Field(default=[], description="Treatment complications")
    adverse_events: list[str] = Field(default=[], description="Adverse events")

    # Follow-up
    last_follow_up_date: date | None = Field(None, description="Last follow-up date")
    follow_up_status: str = Field(default="active", description="Follow-up status")

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)


# Request/Response Models for API


class PatientCreateRequest(BaseModel):
    """Request model for creating a new patient."""

    medical_record_number: str = Field(..., description="Medical record number")
    demographics: PatientDemographics = Field(..., description="Patient demographics")
    comorbidities: list[Comorbidity] = Field(
        default=[], description="Patient comorbidities"
    )
    tumor_characteristics: TumorCharacteristics | None = Field(
        None, description="Tumor details"
    )

    model_config = ConfigDict(str_strip_whitespace=True)


class PatientUpdateRequest(BaseModel):
    """Request model for updating patient information."""

    demographics: PatientDemographics | None = None
    comorbidities: list[Comorbidity] | None = None
    tumor_characteristics: TumorCharacteristics | None = None
    performance_status: PerformanceStatus | None = None
    laboratory_results: list[LaboratoryResults] | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class ADCIDecisionRequest(BaseModel):
    """Request model for ADCI decision support."""

    patient_id: UUID = Field(..., description="Patient ID")
    clinical_scenario: str = Field(..., description="Clinical scenario description")
    override_parameters: dict[str, str | float | int | bool] = Field(
        default={}, description="Parameter overrides"
    )

    model_config = ConfigDict(str_strip_whitespace=True)


class TreatmentPlanRequest(BaseModel):
    """Request model for creating treatment plan."""

    patient_id: UUID = Field(..., description="Patient ID")
    protocol: TreatmentProtocol = Field(..., description="Treatment protocol")
    surgical_procedure: SurgicalProcedure | None = None
    treatment_intent: str = Field(..., description="Treatment intent")
    clinical_notes: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)
