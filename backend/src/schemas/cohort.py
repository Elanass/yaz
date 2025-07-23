"""
Cohort Management Schemas
Data models for cohort input, processing, and analysis
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid

class CohortUploadFormat(str, Enum):
    """Supported cohort upload formats"""
    CSV = "csv"
    JSON = "json"
    FHIR_BUNDLE = "fhir_bundle"
    MANUAL = "manual"

class CohortStatus(str, Enum):
    """Cohort processing status"""
    DRAFT = "draft"
    VALIDATING = "validating"
    VALIDATED = "validated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class InferenceStatus(str, Enum):
    """Inference session status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Input Schemas
class CohortPatientInput(BaseModel):
    """Input schema for individual patient in cohort"""
    patient_identifier: str = Field(..., description="Study-specific patient ID")
    external_patient_id: Optional[str] = Field(None, description="Original system patient ID")
    
    # Demographics
    age: Optional[int] = Field(None, ge=0, le=150, description="Patient age")
    gender: Optional[str] = Field(None, description="Patient gender")
    ethnicity: Optional[str] = Field(None, description="Patient ethnicity")
    
    # Clinical data
    primary_diagnosis: Optional[str] = Field(None, description="Primary cancer diagnosis")
    tumor_stage: Optional[str] = Field(None, description="TNM tumor stage")
    tumor_grade: Optional[str] = Field(None, description="Tumor grade")
    tumor_location: Optional[str] = Field(None, description="Anatomical tumor location")
    
    # Performance status
    ecog_score: Optional[int] = Field(None, ge=0, le=5, description="ECOG performance status")
    karnofsky_score: Optional[int] = Field(None, ge=0, le=100, description="Karnofsky performance score")
    
    # Biomarkers
    biomarkers: Optional[Dict[str, Any]] = Field(None, description="Biomarker data")
    genetic_mutations: Optional[Dict[str, Any]] = Field(None, description="Genetic mutation data")
    
    # Treatment history
    prior_treatments: Optional[List[str]] = Field(None, description="Previous treatments")
    current_medications: Optional[List[str]] = Field(None, description="Current medications")
    comorbidities: Optional[List[str]] = Field(None, description="Comorbid conditions")
    
    # Lab values
    lab_values: Optional[Dict[str, float]] = Field(None, description="Laboratory values")
    vital_signs: Optional[Dict[str, float]] = Field(None, description="Vital signs")
    
    @validator('patient_identifier')
    def validate_patient_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Patient identifier cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_identifier": "COHORT_001_P001",
                "age": 65,
                "gender": "male",
                "primary_diagnosis": "Gastric adenocarcinoma",
                "tumor_stage": "T3N1M0",
                "tumor_grade": "G2",
                "tumor_location": "antrum",
                "ecog_score": 1,
                "biomarkers": {
                    "HER2": "negative",
                    "MSI": "stable",
                    "PD_L1": 5
                },
                "lab_values": {
                    "hemoglobin": 12.5,
                    "albumin": 3.8,
                    "creatinine": 1.0
                }
            }
        }

class CohortUploadRequest(BaseModel):
    """Request schema for cohort upload"""
    name: str = Field(..., min_length=1, max_length=255, description="Cohort study name")
    description: Optional[str] = Field(None, description="Study description")
    upload_format: CohortUploadFormat = Field(..., description="Upload format")
    study_type: str = Field("gastric_cancer", description="Type of study")
    
    # Data compliance
    contains_phi: bool = Field(True, description="Contains protected health information")
    anonymization_level: str = Field("identified", description="Level of anonymization")
    consent_status: str = Field("required", description="Patient consent status")
    
    # For manual upload
    patients: Optional[List[CohortPatientInput]] = Field(None, description="Patient data for manual upload")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Gastric Cancer Treatment Response Study",
                "description": "Analysis of treatment responses in gastric cancer patients",
                "upload_format": "manual",
                "contains_phi": True,
                "anonymization_level": "identified",
                "consent_status": "obtained",
                "patients": []
            }
        }

class CohortFileUploadRequest(BaseModel):
    """Request schema for file-based cohort upload"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    upload_format: CohortUploadFormat = Field(...)
    file_content: str = Field(..., description="Base64 encoded file content")
    filename: str = Field(..., description="Original filename")
    
    # Validation parameters
    skip_validation: bool = Field(False, description="Skip data validation")
    allow_partial: bool = Field(True, description="Allow partial/incomplete data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Cohort from CSV",
                "upload_format": "csv",
                "file_content": "cGF0aWVudF9pZCxhZ2UsZ2VuZGVy...",
                "filename": "cohort_data.csv"
            }
        }

# Processing Schemas
class InferenceSessionRequest(BaseModel):
    """Request to start inference session"""
    cohort_study_id: str = Field(..., description="Cohort study UUID")
    session_name: str = Field(..., min_length=1, max_length=255)
    session_description: Optional[str] = Field(None)
    decision_engines: List[str] = Field(
        default=["adci", "gastrectomy", "flot"],
        description="Decision engines to run"
    )
    processing_parameters: Optional[Dict[str, Any]] = Field(None, description="Processing parameters")
    
    @validator('decision_engines')
    def validate_engines(cls, v):
        valid_engines = {"adci", "gastrectomy", "flot"}
        for engine in v:
            if engine not in valid_engines:
                raise ValueError(f"Invalid decision engine: {engine}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "cohort_study_id": "123e4567-e89b-12d3-a456-426614174000",
                "session_name": "ADCI Analysis Session 1",
                "decision_engines": ["adci", "gastrectomy", "flot"],
                "processing_parameters": {
                    "confidence_threshold": 0.7,
                    "include_explanations": True
                }
            }
        }

# Response Schemas
class CohortStudyInfo(BaseModel):
    """Cohort study information response"""
    id: str = Field(..., description="Cohort study UUID")
    name: str = Field(..., description="Study name")
    description: Optional[str] = Field(None, description="Study description")
    status: CohortStatus = Field(..., description="Current status")
    upload_format: CohortUploadFormat = Field(..., description="Upload format used")
    
    # Statistics
    total_patients: int = Field(..., description="Total number of patients")
    valid_patients: int = Field(..., description="Number of valid patients")
    invalid_patients: int = Field(..., description="Number of invalid patients")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    processing_started_at: Optional[datetime] = Field(None)
    processing_completed_at: Optional[datetime] = Field(None)
    
    # Validation
    validation_errors: Optional[List[str]] = Field(None)
    validation_warnings: Optional[List[str]] = Field(None)
    
    # Creator info
    created_by: str = Field(..., description="Creator user ID")
    
    class Config:
        from_attributes = True

class PatientDecisionResultInfo(BaseModel):
    """Patient decision result information"""
    patient_identifier: str = Field(..., description="Patient ID")
    
    # ADCI results
    adci_score: Optional[float] = Field(None, description="ADCI index score")
    adci_confidence: Optional[float] = Field(None, description="ADCI confidence level")
    adci_recommendation: Optional[str] = Field(None, description="ADCI recommendation")
    
    # Gastrectomy results
    gastrectomy_recommendation: Optional[str] = Field(None)
    gastrectomy_confidence: Optional[float] = Field(None)
    gastrectomy_risk_factors: Optional[List[str]] = Field(None)
    
    # FLOT results
    flot_eligibility: Optional[bool] = Field(None)
    flot_recommendation: Optional[str] = Field(None)
    flot_confidence: Optional[float] = Field(None)
    
    # Overall recommendation
    primary_recommendation: Optional[str] = Field(None)
    recommendation_confidence: Optional[float] = Field(None)
    treatment_pathway: Optional[str] = Field(None)
    
    # Risk scores
    surgical_risk_score: Optional[float] = Field(None)
    mortality_risk: Optional[float] = Field(None)
    complication_risk: Optional[float] = Field(None)
    
    # Explanatory data
    decision_factors: Optional[Dict[str, Any]] = Field(None)
    evidence_links: Optional[List[str]] = Field(None)
    contraindications: Optional[List[str]] = Field(None)
    
    class Config:
        from_attributes = True

class InferenceSessionInfo(BaseModel):
    """Inference session information"""
    id: str = Field(..., description="Session UUID")
    session_name: str = Field(..., description="Session name")
    status: InferenceStatus = Field(..., description="Current status")
    decision_engines: List[str] = Field(..., description="Decision engines used")
    
    # Progress
    total_patients: int = Field(..., description="Total patients to process")
    processed_patients: int = Field(..., description="Patients processed")
    failed_patients: int = Field(..., description="Failed patient processes")
    progress_percentage: float = Field(..., description="Progress percentage")
    
    # Timing
    started_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)
    duration_seconds: Optional[float] = Field(None)
    
    # Results
    results_summary: Optional[Dict[str, Any]] = Field(None)
    
    class Config:
        from_attributes = True

class CohortAnalysisResults(BaseModel):
    """Complete cohort analysis results"""
    cohort_study: CohortStudyInfo = Field(..., description="Cohort study information")
    inference_session: InferenceSessionInfo = Field(..., description="Inference session info")
    patient_results: List[PatientDecisionResultInfo] = Field(..., description="Individual patient results")
    
    # Summary statistics
    summary_stats: Dict[str, Any] = Field(..., description="Summary statistics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cohort_study": {},
                "inference_session": {},
                "patient_results": [],
                "summary_stats": {
                    "average_adci_score": 0.75,
                    "high_confidence_recommendations": 85,
                    "surgical_candidates": 60,
                    "flot_eligible_patients": 45
                }
            }
        }

# Export Schemas
class CohortExportRequest(BaseModel):
    """Request for cohort data export"""
    cohort_study_id: str = Field(..., description="Cohort study UUID")
    inference_session_id: Optional[str] = Field(None, description="Specific inference session")
    export_format: str = Field(..., regex="^(csv|pdf|fhir|json)$", description="Export format")
    export_type: str = Field(..., regex="^(full_results|summary|report)$", description="Export type")
    
    # Export parameters
    include_patient_ids: bool = Field(True, description="Include patient identifiers")
    include_phi: bool = Field(False, description="Include protected health information")
    include_raw_data: bool = Field(True, description="Include raw input data")
    include_decisions: bool = Field(True, description="Include decision results")
    include_explanations: bool = Field(True, description="Include decision explanations")
    
    # Filtering
    patient_filters: Optional[Dict[str, Any]] = Field(None, description="Patient filtering criteria")
    confidence_threshold: Optional[float] = Field(None, description="Minimum confidence threshold")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cohort_study_id": "123e4567-e89b-12d3-a456-426614174000",
                "export_format": "csv",
                "export_type": "full_results",
                "include_patient_ids": True,
                "include_phi": False,
                "confidence_threshold": 0.7
            }
        }

class CohortExportResponse(BaseModel):
    """Response for export request"""
    task_id: str = Field(..., description="Export task UUID")
    status: str = Field(..., description="Export status")
    download_url: Optional[str] = Field(None, description="Download URL when ready")
    filename: Optional[str] = Field(None, description="Generated filename")
    expires_at: Optional[datetime] = Field(None, description="Download expiration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "export_123456",
                "status": "processing",
                "download_url": None,
                "filename": "cohort_results_20240115.csv",
                "expires_at": "2024-01-16T10:30:00Z"
            }
        }

# Hypothesis Schemas
class HypothesisRequest(BaseModel):
    """Request to create and test hypothesis"""
    cohort_study_id: str = Field(..., description="Cohort study UUID")
    base_inference_session_id: Optional[str] = Field(None, description="Base session for comparison")
    
    hypothesis_name: str = Field(..., min_length=1, max_length=255)
    hypothesis_description: Optional[str] = Field(None)
    hypothesis_type: str = Field(..., description="Type of hypothesis test")
    
    # Parameter modifications
    parameter_changes: Dict[str, Any] = Field(..., description="Parameters to modify")
    patient_filters: Optional[Dict[str, Any]] = Field(None, description="Patient subset filters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cohort_study_id": "123e4567-e89b-12d3-a456-426614174000",
                "hypothesis_name": "Lower ECOG Impact on FLOT",
                "hypothesis_type": "parameter_change",
                "parameter_changes": {
                    "ecog_score": 0
                },
                "patient_filters": {
                    "tumor_stage": ["T3", "T4"]
                }
            }
        }

class HypothesisResult(BaseModel):
    """Hypothesis test results"""
    hypothesis_id: str = Field(..., description="Hypothesis UUID")
    hypothesis_name: str = Field(..., description="Hypothesis name")
    
    # Comparison results
    baseline_results: Dict[str, Any] = Field(..., description="Original cohort results")
    modified_results: Dict[str, Any] = Field(..., description="Modified parameter results")
    comparison_summary: Dict[str, Any] = Field(..., description="Statistical comparison")
    
    # Significance
    statistical_significance: Optional[float] = Field(None, description="P-value if applicable")
    effect_size: Optional[float] = Field(None, description="Effect size measure")
    
    class Config:
        json_schema_extra = {
            "example": {
                "hypothesis_id": "hyp_123456",
                "hypothesis_name": "Lower ECOG Impact on FLOT",
                "baseline_results": {
                    "flot_eligible": 45,
                    "flot_percentage": 0.45
                },
                "modified_results": {
                    "flot_eligible": 78,
                    "flot_percentage": 0.78
                },
                "comparison_summary": {
                    "improvement": 0.33,
                    "patients_affected": 33
                }
            }
        }
