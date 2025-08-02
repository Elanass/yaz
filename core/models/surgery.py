"""
Surgery Models Module

This module provides Pydantic models for surgery-related data structures
used throughout the platform. These models include comprehensive patient
and surgical case data with proper validation and type hints.

The models follow HIPAA/GDPR compliance requirements with proper 
data validation and sanitization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


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
    gender: str = Field(..., pattern="^(male|female|other)$", description="Patient gender")
    bmi: Optional[float] = Field(None, ge=10, le=80, description="Body Mass Index")
    
    # Medical History
    comorbidities: List[str] = Field(default=[], description="List of patient comorbidities")
    medications: List[str] = Field(default=[], description="Current medications")
    allergies: List[str] = Field(default=[], description="Known allergies")
    previous_surgeries: List[str] = Field(default=[], description="Previous surgical procedures")
    medical_history: List[str] = Field(default=[], description="Relevant medical history elements")
    
    # Clinical Data
    vital_signs: Dict[str, float] = Field(default={}, description="Vital sign measurements")
    lab_values: Dict[str, float] = Field(default={}, description="Laboratory values")
    imaging_results: Dict[str, str] = Field(default={}, description="Imaging study results")
    
    # Surgery-Specific Data
    tumor_stage: Optional[str] = Field(None, description="TNM staging if applicable")
    surgical_approach: Optional[str] = Field(None, description="Open/Laparoscopic/Robotic")
    urgency: str = Field(default="elective", pattern="^(elective|urgent|emergency)$", 
                        description="Surgery urgency level")
    
    # FLOT-Specific Fields
    flot_cycles_completed: Optional[int] = Field(None, ge=0, le=8, 
                                               description="Number of completed FLOT cycles")
    response_to_neoadjuvant: Optional[str] = Field(None, 
                                                 description="Response to neoadjuvant therapy")
    # Enhanced FLOT-specific fields
    flot_timing_weeks: Optional[int] = Field(None, ge=0, le=52, 
                                           description="Timing of FLOT cycles in weeks before surgery")
    flot_start_date: Optional[datetime] = Field(None, description="Date of first FLOT cycle")
    flot_completion_date: Optional[datetime] = Field(None, description="Date of last FLOT cycle")
    flot_dosage_adjustments: Optional[List[Dict[str, Any]]] = Field(None, 
                                                                  description="History of FLOT dosage adjustments")
    flot_toxicity_grade: Optional[int] = Field(None, ge=0, le=5, 
                                             description="Maximum toxicity grade observed during FLOT")
    
    # Tumor Response Grading
    trg_score: Optional[int] = Field(None, ge=0, le=5, 
                                   description="Tumor Regression Grade score (0-5 scale)")
    trg_assessment_method: Optional[str] = Field(None, 
                                              description="Method used for TRG assessment")
    
    # Nutritional Status
    albumin_level_pre_flot: Optional[float] = Field(None, ge=0.5, le=7.0, 
                                                 description="Albumin level before FLOT therapy in g/dL")
    albumin_level_post_flot: Optional[float] = Field(None, ge=0.5, le=7.0, 
                                                  description="Albumin level after FLOT therapy in g/dL")
    weight_loss_during_flot: Optional[float] = Field(None, ge=0.0, le=50.0, 
                                                  description="Weight loss during FLOT therapy in percentage")
    nutritional_support: Optional[bool] = Field(None, 
                                             description="Whether nutritional support was provided during FLOT")
    
    # Risk Factors
    asa_score: Optional[int] = Field(None, ge=1, le=5, description="ASA physical status")
    frailty_score: Optional[float] = Field(None, ge=0, le=10, description="Frailty assessment score")
    smoking_status: Optional[str] = Field(None, description="Current/Former/Never")
    weight_loss_percentage: Optional[float] = Field(None, ge=0, le=100, 
                                                  description="Recent weight loss percentage")
    
    # Surgery Planning
    diagnosis_date: Optional[datetime] = Field(None, description="Date of initial diagnosis")
    surgery_date: Optional[datetime] = Field(None, description="Planned or actual surgery date")
    
    # Post-surgery data (if available)
    complications: Optional[List[str]] = Field(None, description="Post-surgical complications")
    lymph_nodes_examined: Optional[int] = Field(None, ge=0, description="Number of lymph nodes examined")
    resection_margin: Optional[str] = Field(None, description="Resection margin status (R0/R1/R2)")
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(None, description="User who created the record")
    
    @validator('lab_values')
    def validate_lab_values(cls, v):
        """Validate that lab values are within reasonable ranges."""
        if 'albumin' in v and (v['albumin'] < 0.5 or v['albumin'] > 8):
            raise ValueError(f"Albumin value outside reasonable range: {v['albumin']}")
        if 'creatinine' in v and (v['creatinine'] < 0.1 or v['creatinine'] > 30):
            raise ValueError(f"Creatinine value outside reasonable range: {v['creatinine']}")
        return v

    @validator('vital_signs')
    def validate_vital_signs(cls, v):
        """Validate that vital signs are within reasonable ranges."""
        if 'heart_rate' in v and (v['heart_rate'] < 30 or v['heart_rate'] > 250):
            raise ValueError(f"Heart rate outside reasonable range: {v['heart_rate']}")
        if 'systolic_bp' in v and (v['systolic_bp'] < 50 or v['systolic_bp'] > 250):
            raise ValueError(f"Systolic BP outside reasonable range: {v['systolic_bp']}")
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
                "asa_score": 3
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
    
    # Confidence and Validation
    confidence_score: float = Field(..., ge=0, le=1, 
                                   description="Overall confidence in analysis results")
    evidence_sources: Optional[List[str]] = Field(default=[], 
                                                description="Supporting evidence sources")
    
    class Config:
        schema_extra = {
            "example": {
                "case_id": "GS001",
                "surgery_type": "gastric_flot",
                "analysis_timestamp": "2025-07-29T10:30:00",
                "overall_risk": "moderate",
                "risk_factors": ["Age > 65", "Diabetes"],
                "risk_mitigation": ["Optimize glycemic control", "Preoperative respiratory therapy"],
                "recommended_protocol": "FLOT-Enhanced Recovery",
                "protocol_modifications": ["Extended VTE prophylaxis"],
                "contraindications": [],
                "predicted_outcomes": {"mortality": "standard_risk", "los": 7},
                "complication_risk": {"anastomotic_leak": 0.08, "pneumonia": 0.12},
                "length_of_stay_prediction": 7,
                "quality_indicators": {"protocol_adherence": 0.9, "time_to_surgery": 0.85},
                "benchmarking_data": {"national_average_los": 8.5, "national_complication_rate": 0.15},
                "recommendations": ["Follow FLOT-Enhanced Recovery protocol", "Optimize glycemic control"],
                "alerts": ["Diabetes requires perioperative management"],
                "next_steps": ["Complete preoperative assessment", "Schedule follow-up"],
                "confidence_score": 0.85
            }
        }
