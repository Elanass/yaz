"""
Surgery Models Module

This module provides Pydantic models for surgery-related data structures
used throughout the platform. These models include comprehensive patient
and surgical case data with proper validation and type hints.

The models follow HIPAA/GDPR compliance requirements with proper 
data validation and sanitization.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


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
    """
    Comprehensive model for surgical case data with all
    required fields for analysis and decision support.
    """

    case_id: str = Field(..., description="Unique case identifier")
    patient_id: str = Field(..., description="Patient identifier")
    surgery_type: SurgeryType = Field(..., description="Type of surgery")

    # Patient Demographics
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    gender: str = Field(
        ..., pattern="^(male|female|other)$", description="Patient gender"
    )
    bmi: Optional[float] = Field(None, ge=10, le=80, description="Body Mass Index")

    # Medical History
    comorbidities: List[str] = Field(
        default=[], description="List of patient comorbidities"
    )
    medications: List[str] = Field(default=[], description="Current medications")
    allergies: List[str] = Field(default=[], description="Known allergies")
    previous_surgeries: List[str] = Field(
        default=[], description="Previous surgical procedures"
    )
    medical_history: List[str] = Field(
        default=[], description="Relevant medical history elements"
    )

    # Clinical Data
    vital_signs: Dict[str, float] = Field(
        default={}, description="Vital sign measurements"
    )
    lab_values: Dict[str, float] = Field(default={}, description="Laboratory values")
    imaging_results: Dict[str, str] = Field(
        default={}, description="Imaging study results"
    )

    # Surgery-Specific Data
    tumor_stage: Optional[str] = Field(None, description="TNM staging if applicable")
    surgical_approach: Optional[str] = Field(
        None, description="Open/Laparoscopic/Robotic"
    )
    urgency: str = Field(
        default="elective",
        pattern="^(elective|urgent|emergency)$",
        description="Surgery urgency level",
    )

    # FLOT-Specific Fields
    flot_cycles_completed: Optional[int] = Field(
        None, ge=0, le=8, description="Number of completed FLOT cycles"
    )
    response_to_neoadjuvant: Optional[str] = Field(
        None, description="Response to neoadjuvant therapy"
    )
    # Enhanced FLOT-specific fields
    flot_timing_weeks: Optional[int] = Field(
        None, ge=0, le=52, description="Timing of FLOT cycles in weeks before surgery"
    )
    flot_start_date: Optional[datetime] = Field(
        None, description="Date of first FLOT cycle"
    )
    flot_completion_date: Optional[datetime] = Field(
        None, description="Date of last FLOT cycle"
    )
    flot_dosage_adjustments: Optional[List[Dict[str, Any]]] = Field(
        None, description="History of FLOT dosage adjustments"
    )
    flot_toxicity_grade: Optional[int] = Field(
        None, ge=0, le=5, description="Maximum toxicity grade observed during FLOT"
    )

    # Tumor Response Grading
    trg_score: Optional[int] = Field(
        None, ge=0, le=5, description="Tumor Regression Grade score (0-5 scale)"
    )
    trg_assessment_method: Optional[str] = Field(
        None, description="Method used for TRG assessment"
    )

    # Nutritional Status
    albumin_level_pre_flot: Optional[float] = Field(
        None, ge=0.5, le=7.0, description="Albumin level before FLOT therapy in g/dL"
    )
    albumin_level_post_flot: Optional[float] = Field(
        None, ge=0.5, le=7.0, description="Albumin level after FLOT therapy in g/dL"
    )
    weight_loss_during_flot: Optional[float] = Field(
        None,
        ge=0.0,
        le=50.0,
        description="Weight loss during FLOT therapy in percentage",
    )
    nutritional_support: Optional[bool] = Field(
        None, description="Whether nutritional support was provided during FLOT"
    )

    # Risk Factors
    asa_score: Optional[int] = Field(
        None, ge=1, le=5, description="ASA physical status"
    )
    frailty_score: Optional[float] = Field(
        None, ge=0, le=10, description="Frailty assessment score"
    )
    smoking_status: Optional[str] = Field(None, description="Current/Former/Never")
    weight_loss_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Recent weight loss percentage"
    )

    # Surgery Planning
    diagnosis_date: Optional[datetime] = Field(
        None, description="Date of initial diagnosis"
    )
    surgery_date: Optional[datetime] = Field(
        None, description="Planned or actual surgery date"
    )

    # Post-surgery data (if available)
    complications: Optional[List[str]] = Field(
        None, description="Post-surgical complications"
    )
    lymph_nodes_examined: Optional[int] = Field(
        None, ge=0, description="Number of lymph nodes examined"
    )
    resection_margin: Optional[str] = Field(
        None, description="Resection margin status (R0/R1/R2)"
    )

    # Text and Image Data Fields
    clinical_notes: Optional[str] = Field(
        None, description="Free-form clinical notes and observations"
    )
    pathology_report: Optional[str] = Field(
        None, description="Detailed pathology report text"
    )
    surgery_notes: Optional[str] = Field(
        None, description="Operative notes and surgical details"
    )
    discharge_summary: Optional[str] = Field(
        None, description="Discharge summary and post-operative care instructions"
    )
    
    # Image and Media References
    ct_scan_images: Optional[List[str]] = Field(
        default_factory=list, description="List of CT scan image file paths or IDs"
    )
    mri_images: Optional[List[str]] = Field(
        default_factory=list, description="List of MRI image file paths or IDs"
    )
    pathology_images: Optional[List[str]] = Field(
        default_factory=list, description="List of pathology slide image file paths or IDs"
    )
    endoscopy_images: Optional[List[str]] = Field(
        default_factory=list, description="List of endoscopic image file paths or IDs"
    )
    surgical_photos: Optional[List[str]] = Field(
        default_factory=list, description="List of surgical photography file paths or IDs"
    )
    other_images: Optional[List[str]] = Field(
        default_factory=list, description="List of other medical image file paths or IDs"
    )
    
    # Document References
    consent_forms: Optional[List[str]] = Field(
        default_factory=list, description="List of consent form document file paths or IDs"
    )
    lab_reports: Optional[List[str]] = Field(
        default_factory=list, description="List of laboratory report document file paths or IDs"
    )
    radiology_reports: Optional[List[str]] = Field(
        default_factory=list, description="List of radiology report document file paths or IDs"
    )

    # Audit fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(None, description="User who created the record")

    @validator("lab_values")
    def validate_lab_values(cls, v):
        """Validate that lab values are within reasonable ranges."""
        if "albumin" in v and (v["albumin"] < 0.5 or v["albumin"] > 8):
            raise ValueError(f"Albumin value outside reasonable range: {v['albumin']}")
        if "creatinine" in v and (v["creatinine"] < 0.1 or v["creatinine"] > 30):
            raise ValueError(
                f"Creatinine value outside reasonable range: {v['creatinine']}"
            )
        return v

    @validator("vital_signs")
    def validate_vital_signs(cls, v):
        """Validate that vital signs are within reasonable ranges."""
        if "heart_rate" in v and (v["heart_rate"] < 30 or v["heart_rate"] > 250):
            raise ValueError(f"Heart rate outside reasonable range: {v['heart_rate']}")
        if "systolic_bp" in v and (v["systolic_bp"] < 50 or v["systolic_bp"] > 250):
            raise ValueError(
                f"Systolic BP outside reasonable range: {v['systolic_bp']}"
            )
        return v

    class Config:
        schema_extra = {
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
                "surgery_notes": "Laparoscopic approach, no complications.",
                "discharge_summary": "Stable, follow-up in 1 week.",
                "ct_scan_images": ["/path/to/ct_image1.jpg"],
                "mri_images": ["/path/to/mri_image1.jpg"],
                "pathology_images": ["/path/to/pathology_image1.jpg"],
                "endoscopy_images": ["/path/to/endoscopy_image1.jpg"],
                "surgical_photos": ["/path/to/surgical_photo1.jpg"],
                "other_images": ["/path/to/other_image1.jpg"],
                "consent_forms": ["/path/to/consent_form1.pdf"],
                "lab_reports": ["/path/to/lab_report1.pdf"],
                "radiology_reports": ["/path/to/radiology_report1.pdf"],
            }
        }


class SurgicalAnalysisResult(BaseModel):
    """
    Model for storing and presenting comprehensive surgical analysis
    results including risk assessment, recommendations, and outcomes.
    """

    case_id: str
    surgery_type: SurgeryType
    analysis_timestamp: datetime

    # Risk Assessment
    overall_risk: RiskLevel
    risk_factors: List[str]
    risk_mitigation: List[str]

    # Protocol Recommendations
    recommended_protocol: str
    protocol_modifications: List[str]
    contraindications: List[str]

    # Outcome Predictions
    predicted_outcomes: Dict[str, Union[str, float]]
    complication_risk: Dict[str, float]
    length_of_stay_prediction: int

    # Quality Metrics
    quality_indicators: Dict[str, float]
    benchmarking_data: Dict[str, float]

    # Decision Support
    recommendations: List[str]
    alerts: List[str]
    next_steps: List[str]

    # Text and Image Output Data
    generated_report: Optional[str] = Field(
        None, description="Generated comprehensive surgical analysis report"
    )
    patient_education_text: Optional[str] = Field(
        None, description="Generated patient education materials"
    )
    clinical_summary: Optional[str] = Field(
        None, description="Clinical summary for other healthcare providers"
    )
    discharge_instructions: Optional[str] = Field(
        None, description="Generated discharge instructions"
    )
    
    # Generated Images and Visualizations
    risk_visualization: Optional[str] = Field(
        None, description="Path to generated risk assessment visualization"
    )
    outcome_charts: Optional[List[str]] = Field(
        default_factory=list, description="List of generated outcome prediction charts"
    )
    comparison_images: Optional[List[str]] = Field(
        default_factory=list, description="List of generated comparison visualization images"
    )
    infographic_path: Optional[str] = Field(
        None, description="Path to generated patient education infographic"
    )
    
    # Generated Documents
    full_report_pdf: Optional[str] = Field(
        None, description="Path to generated full analysis report PDF"
    )
    patient_handout_pdf: Optional[str] = Field(
        None, description="Path to generated patient handout PDF"
    )
    clinical_decision_doc: Optional[str] = Field(
        None, description="Path to generated clinical decision support document"
    )

    # Confidence and Validation
    confidence_score: float = Field(
        ..., ge=0, le=1, description="Overall confidence in analysis results"
    )
    evidence_sources: Optional[List[str]] = Field(
        default=[], description="Supporting evidence sources"
    )

    class Config:
        schema_extra = {
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
                "quality_indicators": {
                    "protocol_adherence": 0.9,
                    "time_to_surgery": 0.85,
                },
                "benchmarking_data": {
                    "national_average_los": 8.5,
                    "national_complication_rate": 0.15,
                },
                "recommendations": [
                    "Follow FLOT-Enhanced Recovery protocol",
                    "Optimize glycemic control",
                ],
                "alerts": ["Diabetes requires perioperative management"],
                "next_steps": [
                    "Complete preoperative assessment",
                    "Schedule follow-up",
                ],
                "confidence_score": 0.85,
            }
        }
