"""Surgery Models Module.

This module provides Pydantic models for surgery-related data structures
used throughout the platform. These models include comprehensive patient
and surgical case data with proper validation and type hints.

The models follow HIPAA/GDPR compliance requirements with proper
data validation and sanitization.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SurgeryType(str, Enum):
    """Supported types of surgeries in the platform."""

    GASTRIC_FLOT = "gastric_flot"
    COLORECTAL_ERAS = "colorectal_eras"
    HEPATOBILIARY = "hepatobiliary"
    EMERGENCY = "emergency"
    GENERAL = "general"


class RiskLevel(str, Enum):
    """Risk levels for surgical risk assessment."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class SurgicalCaseModel(BaseModel):
    """Comprehensive model for surgical case data with all
    required fields for analysis and decision support.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "case_id": "GS001",
                "patient_id": "PT001",
                "surgery_type": "gastric_flot",
                "age": 65,
                "gender": "male",
                "bmi": 28.5,
                "comorbidities": ["hypertension", "diabetes"],
                "lab_values": {"albumin": 3.5, "creatinine": 1.2},
                "tumor_stage": "T3N1M0",
                "surgical_approach": "laparoscopic",
                "urgency": "elective",
                "flot_cycles_completed": 4,
                "asa_score": 3,
                "clinical_notes": "Patient shows signs of improvement.",
                "pathology_report": "Invasive adenocarcinoma, moderately differentiated.",
            }
        }
    )

    case_id: str = Field(..., description="Unique case identifier")
    patient_id: str = Field(..., description="Patient identifier")
    surgery_type: SurgeryType = Field(..., description="Type of surgery")

    # Patient Demographics
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    gender: str = Field(
        ..., pattern="^(male|female|other)$", description="Patient gender"
    )
    bmi: float | None = Field(None, ge=10, le=80, description="Body Mass Index")

    # Medical History
    comorbidities: list[str] = Field(
        default=[], description="List of patient comorbidities"
    )
    medications: list[str] = Field(default=[], description="Current medications")
    allergies: list[str] = Field(default=[], description="Known allergies")
    previous_surgeries: list[str] = Field(
        default=[], description="Previous surgical procedures"
    )
    medical_history: list[str] = Field(
        default=[], description="Relevant medical history elements"
    )

    # Clinical Data
    vital_signs: dict[str, float] = Field(
        default={}, description="Vital sign measurements"
    )
    lab_values: dict[str, float] = Field(default={}, description="Laboratory values")
    imaging_results: dict[str, str] = Field(
        default={}, description="Imaging study results"
    )

    # Surgery-Specific Data
    tumor_stage: str | None = Field(None, description="TNM staging if applicable")
    surgical_approach: str | None = Field(None, description="Open/Laparoscopic/Robotic")
    urgency: str = Field(
        default="elective",
        pattern="^(elective|urgent|emergency)$",
        description="Surgery urgency level",
    )

    # FLOT-Specific Fields
    flot_cycles_completed: int | None = Field(
        None, ge=0, le=8, description="Number of completed FLOT cycles"
    )
    response_to_neoadjuvant: str | None = Field(
        None, description="Response to neoadjuvant therapy"
    )
    # Enhanced FLOT-specific fields
    flot_timing_weeks: int | None = Field(
        None, ge=0, le=52, description="Timing of FLOT cycles in weeks before surgery"
    )
    flot_start_date: datetime | None = Field(
        None, description="Date of first FLOT cycle"
    )
    flot_completion_date: datetime | None = Field(
        None, description="Date of last FLOT cycle"
    )
    flot_dosage_adjustments: list[dict[str, Any]] | None = Field(
        None, description="History of FLOT dosage adjustments"
    )
    flot_toxicity_grade: int | None = Field(
        None, ge=0, le=5, description="Maximum toxicity grade observed during FLOT"
    )

    # Tumor Response Grading
    trg_score: int | None = Field(
        None, ge=0, le=5, description="Tumor Regression Grade score (0-5 scale)"
    )
    trg_assessment_method: str | None = Field(
        None, description="Method used for TRG assessment"
    )

    # Nutritional Status
    albumin_level_pre_flot: float | None = Field(
        None, ge=0.5, le=7.0, description="Albumin level before FLOT therapy in g/dL"
    )
    albumin_level_post_flot: float | None = Field(
        None, ge=0.5, le=7.0, description="Albumin level after FLOT therapy in g/dL"
    )
    weight_loss_during_flot: float | None = Field(
        None,
        ge=0.0,
        le=50.0,
        description="Weight loss during FLOT therapy in percentage",
    )
    nutritional_support: bool | None = Field(
        None, description="Whether nutritional support was provided during FLOT"
    )

    # Risk Factors
    asa_score: int | None = Field(None, ge=1, le=5, description="ASA physical status")
    frailty_score: float | None = Field(
        None, ge=0, le=10, description="Frailty assessment score"
    )
    smoking_status: str | None = Field(None, description="Current/Former/Never")
    weight_loss_percentage: float | None = Field(
        None, ge=0, le=100, description="Recent weight loss percentage"
    )

    # Surgery Planning
    diagnosis_date: datetime | None = Field(
        None, description="Date of initial diagnosis"
    )
    surgery_date: datetime | None = Field(
        None, description="Planned or actual surgery date"
    )

    # Post-surgery data (if available)
    complications: list[str] | None = Field(
        None, description="Post-surgical complications"
    )
    lymph_nodes_examined: int | None = Field(
        None, ge=0, description="Number of lymph nodes examined"
    )
    resection_margin: str | None = Field(
        None, description="Resection margin status (R0/R1/R2)"
    )

    # Text and Image Data Fields
    clinical_notes: str | None = Field(
        None, description="Free-form clinical notes and observations"
    )
    pathology_report: str | None = Field(
        None, description="Detailed pathology report text"
    )
    surgery_notes: str | None = Field(
        None, description="Operative notes and surgical details"
    )
    discharge_summary: str | None = Field(
        None, description="Discharge summary and post-operative care instructions"
    )

    # Image and Media References
    ct_scan_images: list[str] | None = Field(
        default_factory=list, description="List of CT scan image file paths or IDs"
    )
    mri_images: list[str] | None = Field(
        default_factory=list, description="List of MRI image file paths or IDs"
    )
    pathology_images: list[str] | None = Field(
        default_factory=list,
        description="List of pathology slide image file paths or IDs",
    )
    endoscopy_images: list[str] | None = Field(
        default_factory=list, description="List of endoscopic image file paths or IDs"
    )
    surgical_photos: list[str] | None = Field(
        default_factory=list,
        description="List of surgical photography file paths or IDs",
    )
    other_images: list[str] | None = Field(
        default_factory=list,
        description="List of other medical image file paths or IDs",
    )

    # Document References
    consent_forms: list[str] | None = Field(
        default_factory=list,
        description="List of consent form document file paths or IDs",
    )
    lab_reports: list[str] | None = Field(
        default_factory=list,
        description="List of laboratory report document file paths or IDs",
    )
    radiology_reports: list[str] | None = Field(
        default_factory=list,
        description="List of radiology report document file paths or IDs",
    )

    # Audit fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str | None = Field(None, description="User who created the record")

    @field_validator("lab_values")
    @classmethod
    def validate_lab_values(cls, v):
        """Validate that lab values are within reasonable ranges."""
        if "albumin" in v and (v["albumin"] < 0.5 or v["albumin"] > 8):
            msg = f"Albumin value outside reasonable range: {v['albumin']}"
            raise ValueError(msg)
        if "creatinine" in v and (v["creatinine"] < 0.1 or v["creatinine"] > 30):
            msg = f"Creatinine value outside reasonable range: {v['creatinine']}"
            raise ValueError(msg)
        return v

    @field_validator("vital_signs")
    @classmethod
    def validate_vital_signs(cls, v):
        """Validate that vital signs are within reasonable ranges."""
        if "heart_rate" in v and (v["heart_rate"] < 30 or v["heart_rate"] > 250):
            msg = f"Heart rate outside reasonable range: {v['heart_rate']}"
            raise ValueError(msg)
        if "systolic_bp" in v and (v["systolic_bp"] < 50 or v["systolic_bp"] > 250):
            msg = f"Systolic BP outside reasonable range: {v['systolic_bp']}"
            raise ValueError(msg)
        return v


class SurgicalAnalysisResult(BaseModel):
    """Model for storing and presenting comprehensive surgical analysis
    results including risk assessment, recommendations, and outcomes.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "case_id": "GS001",
                "surgery_type": "gastric_flot",
                "analysis_timestamp": "2025-07-29T10:30:00",
                "overall_risk": "moderate",
                "risk_factors": ["Age > 65", "Diabetes"],
                "risk_mitigation": [
                    "Optimize glycemic control",
                    "Preoperative respiratory therapy",
                ],
                "recommended_protocol": "FLOT-Enhanced Recovery",
                "protocol_modifications": ["Extended VTE prophylaxis"],
                "contraindications": [],
                "predicted_outcomes": {"mortality": "standard_risk", "los": 7},
                "complication_risk": {"anastomotic_leak": 0.08, "pneumonia": 0.12},
                "length_of_stay_prediction": 7,
            }
        }
    )

    case_id: str
    surgery_type: SurgeryType
    analysis_timestamp: datetime

    # Risk Assessment
    overall_risk: RiskLevel
    risk_factors: list[str]
    risk_mitigation: list[str]

    # Protocol Recommendations
    recommended_protocol: str
    protocol_modifications: list[str]
    contraindications: list[str]

    # Outcome Predictions
    predicted_outcomes: dict[str, str | float]
    complication_risk: dict[str, float]
    length_of_stay_prediction: int

    # Quality Metrics
    quality_indicators: dict[str, float]
    benchmarking_data: dict[str, float]

    # Decision Support
    recommendations: list[str]
    alerts: list[str]
    next_steps: list[str]

    # Text and Image Output Data
    generated_report: str | None = Field(
        None, description="Generated comprehensive surgical analysis report"
    )
    patient_education_text: str | None = Field(
        None, description="Generated patient education materials"
    )
    clinical_summary: str | None = Field(
        None, description="Clinical summary for other healthcare providers"
    )
    discharge_instructions: str | None = Field(
        None, description="Generated discharge instructions"
    )

    # Generated Images and Visualizations
    risk_visualization: str | None = Field(
        None, description="Path to generated risk assessment visualization"
    )
    outcome_charts: list[str] | None = Field(
        default_factory=list, description="List of generated outcome prediction charts"
    )
    comparison_images: list[str] | None = Field(
        default_factory=list,
        description="List of generated comparison visualization images",
    )
    infographic_path: str | None = Field(
        None, description="Path to generated patient education infographic"
    )

    # Generated Documents
    full_report_pdf: str | None = Field(
        None, description="Path to generated full analysis report PDF"
    )
    patient_handout_pdf: str | None = Field(
        None, description="Path to generated patient handout PDF"
    )
    clinical_decision_doc: str | None = Field(
        None, description="Path to generated clinical decision support document"
    )

    # Confidence and Validation
    confidence_score: float = Field(
        ..., ge=0, le=1, description="Overall confidence in analysis results"
    )
    evidence_sources: list[str] | None = Field(
        default=[], description="Supporting evidence sources"
    )
