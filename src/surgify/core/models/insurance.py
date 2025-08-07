"""
Insurance Models Module

This module provides Pydantic models for insurance-related data structures
used throughout the platform. These models include comprehensive claims,
policies, risk assessment, and cost prediction data with proper validation and type hints.
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class InsuranceType(str, Enum):
    """Supported types of insurance operations in the platform."""

    HEALTH_INSURANCE = "health_insurance"
    DISABILITY = "disability"
    LIFE_INSURANCE = "life_insurance"
    WORKERS_COMP = "workers_comp"
    LIABILITY = "liability"
    PROPERTY = "property"
    GENERAL = "general"


class ClaimStatus(str, Enum):
    """Status values for insurance claims."""

    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"
    CLOSED = "closed"


class RiskCategory(str, Enum):
    """Risk assessment categories."""

    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class InsuranceCaseModel(BaseModel):
    """
    Comprehensive model for insurance case data with all
    required fields for analysis and risk assessment.
    """

    case_id: str = Field(..., description="Unique case identifier")
    claim_id: str = Field(..., description="Insurance claim identifier")
    policy_id: str = Field(..., description="Insurance policy identifier")
    insurance_type: InsuranceType = Field(..., description="Type of insurance")

    # Policyholder Information
    member_id: str = Field(..., description="Member/policyholder identifier")
    patient_id: Optional[str] = Field(None, description="Patient identifier if different from member")
    member_name: Optional[str] = Field(None, description="Member name")
    member_age: Optional[int] = Field(None, ge=0, le=120, description="Member age")
    member_gender: Optional[str] = Field(None, description="Member gender")
    
    # Policy Details
    policy_type: Optional[str] = Field(None, description="Type of insurance policy")
    coverage_amount: Optional[float] = Field(None, ge=0, description="Total coverage amount")
    deductible: Optional[float] = Field(None, ge=0, description="Policy deductible")
    copay: Optional[float] = Field(None, ge=0, description="Copay amount")
    premium: Optional[float] = Field(None, ge=0, description="Monthly premium")
    policy_start_date: Optional[date] = Field(None, description="Policy start date")
    policy_end_date: Optional[date] = Field(None, description="Policy end date")
    
    # Claim Details
    claim_amount: Optional[float] = Field(None, ge=0, description="Claimed amount")
    approved_amount: Optional[float] = Field(None, ge=0, description="Approved amount")
    paid_amount: Optional[float] = Field(None, ge=0, description="Amount paid out")
    claim_date: Optional[date] = Field(None, description="Date claim was filed")
    incident_date: Optional[date] = Field(None, description="Date of incident")
    claim_status: ClaimStatus = Field(default=ClaimStatus.SUBMITTED, description="Current claim status")
    
    # Medical/Service Information
    provider_id: Optional[str] = Field(None, description="Healthcare provider identifier")
    provider_name: Optional[str] = Field(None, description="Provider name")
    service_codes: List[str] = Field(default_factory=list, description="Medical service codes (CPT, ICD)")
    diagnosis_codes: List[str] = Field(default_factory=list, description="Diagnosis codes")
    procedure_codes: List[str] = Field(default_factory=list, description="Procedure codes")
    
    # Risk Assessment
    risk_score: Optional[float] = Field(None, ge=0, le=1, description="Calculated risk score")
    risk_category: Optional[RiskCategory] = Field(None, description="Risk assessment category")
    fraud_indicators: List[str] = Field(default_factory=list, description="Potential fraud indicators")
    
    # Cost Prediction
    estimated_total_cost: Optional[float] = Field(None, ge=0, description="Estimated total cost")
    cost_factors: List[str] = Field(default_factory=list, description="Factors affecting cost")
    cost_category: Optional[str] = Field(None, description="Cost category classification")
    
    # Processing Information
    adjuster_id: Optional[str] = Field(None, description="Claims adjuster identifier")
    review_notes: Optional[str] = Field(None, description="Review and processing notes")
    approval_date: Optional[date] = Field(None, description="Date of approval/denial")
    payment_date: Optional[date] = Field(None, description="Date of payment")

    # Text and Image Data Fields
    claim_description: Optional[str] = Field(
        None, description="Detailed claim description"
    )
    incident_narrative: Optional[str] = Field(
        None, description="Narrative description of the incident"
    )
    adjuster_notes: Optional[str] = Field(
        None, description="Claims adjuster detailed notes"
    )
    medical_summary: Optional[str] = Field(
        None, description="Medical summary and treatment details"
    )
    settlement_terms: Optional[str] = Field(
        None, description="Settlement terms and conditions"
    )
    
    # Image and Media References
    incident_photos: Optional[List[str]] = Field(
        default_factory=list, description="List of incident photo file paths or IDs"
    )
    medical_images: Optional[List[str]] = Field(
        default_factory=list, description="List of medical image file paths or IDs"
    )
    damage_photos: Optional[List[str]] = Field(
        default_factory=list, description="List of damage documentation photo file paths or IDs"
    )
    evidence_images: Optional[List[str]] = Field(
        default_factory=list, description="List of evidence image file paths or IDs"
    )
    witness_statements: Optional[List[str]] = Field(
        default_factory=list, description="List of witness statement file paths or IDs"
    )
    
    # Document References
    policy_documents: Optional[List[str]] = Field(
        default_factory=list, description="List of policy document file paths or IDs"
    )
    medical_records: Optional[List[str]] = Field(
        default_factory=list, description="List of medical record document file paths or IDs"
    )
    claim_forms: Optional[List[str]] = Field(
        default_factory=list, description="List of claim form document file paths or IDs"
    )
    supporting_docs: Optional[List[str]] = Field(
        default_factory=list, description="List of supporting document file paths or IDs"
    )
    legal_documents: Optional[List[str]] = Field(
        default_factory=list, description="List of legal document file paths or IDs"
    )

    # Audit fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(None, description="User who created the record")

    @validator("claim_amount")
    def validate_claim_amount(cls, v, values):
        """Validate claim amount against coverage limits."""
        if v and values.get("coverage_amount"):
            if v > values["coverage_amount"] * 1.1:  # 10% buffer for reasonable claims
                raise ValueError(
                    f"Claim amount {v} exceeds coverage amount {values['coverage_amount']}"
                )
        return v

    @validator("approved_amount") 
    def validate_approved_amount(cls, v, values):
        """Validate approved amount doesn't exceed claim amount."""
        if v and values.get("claim_amount"):
            if v > values["claim_amount"]:
                raise ValueError(
                    f"Approved amount {v} cannot exceed claim amount {values['claim_amount']}"
                )
        return v

    class Config:
        schema_extra = {
            "example": {
                "case_id": "INS001",
                "claim_id": "CLM-2024-001", 
                "policy_id": "POL-12345",
                "insurance_type": "health_insurance",
                "member_id": "MEM-67890",
                "member_name": "John Doe",
                "member_age": 45,
                "member_gender": "male",
                "policy_type": "comprehensive_health",
                "coverage_amount": 100000.00,
                "deductible": 2500.00,
                "copay": 25.00,
                "premium": 450.00,
                "claim_amount": 15000.00,
                "approved_amount": 12750.00,
                "claim_date": "2025-01-15",
                "incident_date": "2025-01-10",
                "claim_status": "approved",
                "provider_name": "City General Hospital",
                "diagnosis_codes": ["K35.9", "Z51.11"],
                "risk_score": 0.25,
                "risk_category": "low",
                "claim_description": "Emergency appendectomy procedure.",
                "medical_summary": "Patient presented with acute appendicitis...",
                "medical_images": ["/path/to/xray1.jpg", "/path/to/ct_scan1.jpg"],
                "medical_records": ["/path/to/medical_record.pdf"],
            }
        }


class InsuranceAnalysisResult(BaseModel):
    """
    Model for storing and presenting comprehensive insurance analysis
    results including risk assessment, cost predictions, and fraud detection.
    """

    case_id: str
    insurance_type: InsuranceType
    analysis_timestamp: datetime

    # Risk Analysis
    overall_risk: RiskCategory
    risk_factors: List[str] = Field(default_factory=list)
    risk_score: float = Field(..., ge=0, le=1, description="Calculated risk score")
    risk_explanation: Optional[str] = Field(None, description="Risk assessment explanation")

    # Cost Analysis
    predicted_cost: Optional[float] = Field(None, description="Predicted total cost")
    cost_range_min: Optional[float] = Field(None, description="Minimum cost estimate")
    cost_range_max: Optional[float] = Field(None, description="Maximum cost estimate")
    cost_factors: List[str] = Field(default_factory=list)
    cost_breakdown: Dict[str, float] = Field(default_factory=dict)

    # Fraud Detection
    fraud_probability: float = Field(..., ge=0, le=1, description="Fraud probability score")
    fraud_indicators: List[str] = Field(default_factory=list)
    fraud_risk_level: str = Field(..., description="Fraud risk assessment level")

    # Claims Processing Recommendations
    processing_recommendation: str = Field(..., description="Recommended processing action")
    approval_probability: Optional[float] = Field(None, ge=0, le=1, description="Approval probability")
    suggested_approved_amount: Optional[float] = Field(None, description="Suggested approval amount")
    investigation_required: bool = Field(default=False, description="Whether investigation is needed")

    # Policy and Coverage Analysis
    coverage_adequacy: Optional[str] = Field(None, description="Coverage adequacy assessment")
    policy_recommendations: List[str] = Field(default_factory=list)
    premium_adjustment_suggestion: Optional[float] = Field(None, description="Suggested premium adjustment")

    # Benchmarking
    industry_benchmarks: Dict[str, float] = Field(default_factory=dict)
    peer_comparison: Optional[str] = Field(None, description="Comparison with peer cases")
    historical_performance: Optional[Dict[str, float]] = Field(None, description="Historical performance metrics")

    # Action Items
    immediate_actions: List[str] = Field(default_factory=list)
    follow_up_required: List[str] = Field(default_factory=list)
    next_review_date: Optional[datetime] = Field(None, description="Next scheduled review")

    # Text and Image Output Data
    generated_report: Optional[str] = Field(
        None, description="Generated comprehensive insurance analysis report"
    )
    risk_assessment_narrative: Optional[str] = Field(
        None, description="Generated risk assessment narrative"
    )
    cost_analysis_summary: Optional[str] = Field(
        None, description="Generated cost analysis summary"
    )
    fraud_investigation_notes: Optional[str] = Field(
        None, description="Generated fraud investigation notes"
    )
    claim_decision_rationale: Optional[str] = Field(
        None, description="Generated claim decision rationale"
    )
    
    # Generated Images and Visualizations
    risk_visualization: Optional[str] = Field(
        None, description="Path to generated risk assessment visualization"
    )
    cost_breakdown_chart: Optional[str] = Field(
        None, description="Path to generated cost breakdown chart"
    )
    fraud_score_visual: Optional[str] = Field(
        None, description="Path to generated fraud score visualization"
    )
    trend_analysis_graphs: Optional[List[str]] = Field(
        default_factory=list, description="List of generated trend analysis graphs"
    )
    comparison_charts: Optional[List[str]] = Field(
        default_factory=list, description="List of generated comparison charts"
    )
    
    # Generated Documents
    full_analysis_pdf: Optional[str] = Field(
        None, description="Path to generated full insurance analysis PDF"
    )
    claims_decision_doc: Optional[str] = Field(
        None, description="Path to generated claims decision document"
    )
    risk_report_pdf: Optional[str] = Field(
        None, description="Path to generated risk assessment report PDF"
    )
    member_communication: Optional[str] = Field(
        None, description="Path to generated member communication document"
    )

    # Confidence and Validation
    confidence_score: float = Field(
        ..., ge=0, le=1, description="Overall confidence in analysis results"
    )
    data_completeness: Optional[float] = Field(
        None, ge=0, le=1, description="Completeness of input data"
    )
    model_accuracy: Optional[float] = Field(
        None, ge=0, le=1, description="Historical model accuracy for similar cases"
    )

    class Config:
        schema_extra = {
            "example": {
                "case_id": "INS001",
                "insurance_type": "health_insurance",
                "analysis_timestamp": "2025-01-20T16:45:00",
                "overall_risk": "low",
                "risk_factors": ["No previous claims", "Young age"],
                "risk_score": 0.25,
                "predicted_cost": 13500.00,
                "cost_range_min": 12000.00,
                "cost_range_max": 15000.00,
                "cost_factors": ["Procedure complexity", "Hospital tier"],
                "fraud_probability": 0.05,
                "fraud_risk_level": "very_low",
                "processing_recommendation": "approve",
                "approval_probability": 0.92,
                "suggested_approved_amount": 12750.00,
                "investigation_required": False,
                "confidence_score": 0.88,
                "generated_report": "Comprehensive insurance analysis indicates...",
                "risk_visualization": "/path/to/risk_chart.png",
                "full_analysis_pdf": "/path/to/insurance_analysis.pdf",
            }
        }
