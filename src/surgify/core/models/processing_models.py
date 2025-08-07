"""
Data models for CSV processing and analytics pipeline
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field


class DataDomain(Enum):
    """Supported data domains"""

    SURGERY = "surgery"
    LOGISTICS = "logistics"
    INSURANCE = "insurance"
    GENERAL = "general"


class FieldType(Enum):
    """Field data types"""

    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATE = "date"
    TEXT = "text"
    LONG_TEXT = "long_text"
    MEDICAL_CODE = "medical_code"
    IDENTIFIER = "identifier"
    IMAGE = "image"
    PIXEL_DATA = "pixel_data"
    MEDIA_FILE = "media_file"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"


class ValidationError(BaseModel):
    """Data validation error"""

    field: str
    error_type: str
    message: str
    severity: str = "error"
    row_indices: Optional[List[int]] = None


class FieldSchema(BaseModel):
    """Schema definition for a data field"""

    name: str
    field_type: FieldType
    is_required: bool = False
    constraints: Dict[str, Any] = Field(default_factory=dict)
    domain_specific: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class DataSchema(BaseModel):
    """Complete schema for a dataset"""

    domain: DataDomain
    fields: List[FieldSchema]
    total_fields: int
    detected_at: datetime
    confidence_score: float = 0.0

    class Config:
        use_enum_values = True


class QualityReport(BaseModel):
    """Data quality assessment report"""

    completeness_score: float = Field(..., ge=0, le=1)
    consistency_score: float = Field(..., ge=0, le=1)
    validity_score: float = Field(..., ge=0, le=1)
    outlier_percentage: float = Field(..., ge=0, le=1)
    overall_score: Optional[float] = None

    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    total_records: int
    valid_records: int

    def __post_init__(self):
        """Calculate overall quality score"""
        if self.overall_score is None:
            weights = {"completeness": 0.3, "consistency": 0.3, "validity": 0.4}
            self.overall_score = (
                self.completeness_score * weights["completeness"]
                + self.consistency_score * weights["consistency"]
                + self.validity_score * weights["validity"]
            )


class DomainInsights(BaseModel):
    """Domain-specific insights from data analysis"""

    domain: DataDomain
    statistical_summary: Dict[str, Any] = Field(default_factory=dict)
    categorical_summary: Dict[str, Any] = Field(default_factory=dict)
    correlations: Dict[str, Any] = Field(default_factory=dict)
    patterns: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    risk_indicators: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class ProcessingResult(BaseModel):
    """Complete result of CSV processing"""

    schema: DataSchema
    quality_report: QualityReport
    insights: DomainInsights
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)

    # Note: We don't include the actual DataFrame in the Pydantic model
    # It will be handled separately to avoid serialization issues
    _data: Optional[pd.DataFrame] = None

    @property
    def data(self) -> Optional[pd.DataFrame]:
        """Get the processed data"""
        return self._data

    @data.setter
    def data(self, value: pd.DataFrame):
        """Set the processed data"""
        self._data = value

    class Config:
        arbitrary_types_allowed = True


# Insight Generation Models


class ExecutiveSummary(BaseModel):
    """Executive summary for leadership"""

    key_metrics: Dict[str, Union[str, float, int]]
    critical_findings: List[str]
    business_impact: str
    recommendations: List[str]
    roi_implications: Optional[str] = None


class ClinicalFindings(BaseModel):
    """Clinical findings for healthcare professionals"""

    patient_outcomes: Dict[str, Any] = Field(default_factory=dict)
    risk_factors: List[Dict[str, Any]] = Field(default_factory=list)
    treatment_efficacy: Dict[str, Any] = Field(default_factory=dict)
    evidence_strength: str = "moderate"
    clinical_recommendations: List[str] = Field(default_factory=list)


class TechnicalAnalysis(BaseModel):
    """Technical analysis for researchers"""

    methodology: str
    statistical_tests: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_intervals: Dict[str, Any] = Field(default_factory=dict)
    limitations: List[str] = Field(default_factory=list)
    data_quality_notes: List[str] = Field(default_factory=list)


class OperationalGuide(BaseModel):
    """Operational guidance for managers"""

    action_items: List[Dict[str, Any]] = Field(default_factory=list)
    implementation_steps: List[str] = Field(default_factory=list)
    resource_requirements: Dict[str, Any] = Field(default_factory=dict)
    timeline: Optional[str] = None
    success_metrics: List[str] = Field(default_factory=list)


class InsightPackage(BaseModel):
    """Comprehensive insight package"""

    executive_summary: ExecutiveSummary
    clinical_findings: Optional[ClinicalFindings] = None
    technical_analysis: TechnicalAnalysis
    operational_guide: OperationalGuide

    # Visual analytics metadata (actual plots stored separately)
    visualizations: List[Dict[str, Any]] = Field(default_factory=list)

    generated_at: datetime = Field(default_factory=datetime.utcnow)
    confidence_level: float = Field(..., ge=0, le=1)


# Deliverable Models


class AudienceType(Enum):
    """Target audience types"""

    EXECUTIVE = "executive"
    CLINICAL = "clinical"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    PATIENT = "patient"


class DeliverableFormat(Enum):
    """Supported deliverable formats"""

    PDF = "pdf"
    INTERACTIVE = "interactive"
    PRESENTATION = "presentation"
    API = "api"
    INFOGRAPHIC = "infographic"


class DeliverableRequest(BaseModel):
    """Request for deliverable generation"""

    processing_result_id: str
    audience: AudienceType
    format: DeliverableFormat
    customization: Dict[str, Any] = Field(default_factory=dict)
    include_raw_data: bool = False

    class Config:
        use_enum_values = True


class DeliverableMetadata(BaseModel):
    """Metadata for generated deliverable"""

    id: str
    title: str
    audience: AudienceType
    format: DeliverableFormat
    generated_at: datetime
    file_size_bytes: Optional[int] = None
    page_count: Optional[int] = None
    download_url: Optional[str] = None

    class Config:
        use_enum_values = True


class Deliverable(BaseModel):
    """Generated deliverable"""

    metadata: DeliverableMetadata
    content: Optional[bytes] = None  # For PDF/binary content
    html_content: Optional[str] = None  # For web deliverables
    api_response: Optional[Dict[str, Any]] = None  # For API format

    class Config:
        arbitrary_types_allowed = True


# Feedback Models


class FeedbackType(Enum):
    """Types of feedback"""

    RATING = "rating"
    COMMENT = "comment"
    CORRECTION = "correction"
    SUGGESTION = "suggestion"
    OUTCOME_VALIDATION = "outcome_validation"


class FeedbackData(BaseModel):
    """User feedback data"""

    deliverable_id: str
    feedback_type: FeedbackType
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    specific_field: Optional[str] = None
    suggested_value: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class AggregatedFeedback(BaseModel):
    """Aggregated feedback for continuous improvement"""

    deliverable_type: str
    average_rating: float
    total_feedback_count: int
    common_issues: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    accuracy_metrics: Dict[str, float] = Field(default_factory=dict)
