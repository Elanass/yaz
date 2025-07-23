"""
Confidence Visualization Pydantic Schemas
Data models for ADCI confidence visualization and metrics
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

class VisualizationType(str, Enum):
    """Types of confidence visualizations"""
    REAL_TIME_GAUGE = "real_time_gauge"
    HISTORICAL_TREND = "historical_trend"
    THRESHOLD_ANALYSIS = "threshold_analysis"
    DECISION_TREE = "decision_tree"
    COMPARATIVE_CHART = "comparative_chart"
    HEATMAP = "heatmap"
    RISK_PROFILE = "risk_profile"
    UNCERTAINTY_BANDS = "uncertainty_bands"

class ConfidenceThreshold(str, Enum):
    """Predefined confidence thresholds"""
    VERY_LOW = "very_low"      # < 0.3
    LOW = "low"                # 0.3 - 0.5
    MODERATE = "moderate"      # 0.5 - 0.7
    HIGH = "high"              # 0.7 - 0.85
    VERY_HIGH = "very_high"    # > 0.85

class ConfidenceFactor(str, Enum):
    """Factors contributing to confidence score"""
    DATA_COMPLETENESS = "data_completeness"
    EVIDENCE_QUALITY = "evidence_quality"
    CLINICAL_ALIGNMENT = "clinical_alignment"
    PROTOCOL_ADHERENCE = "protocol_adherence"
    PATIENT_COMPLEXITY = "patient_complexity"
    TEMPORAL_STABILITY = "temporal_stability"

class VisualizationRequest(BaseModel):
    """Base request for confidence visualizations"""
    patient_id: str = Field(..., description="Patient identifier")
    protocol_id: str = Field(..., description="Clinical protocol identifier")
    visualization_type: VisualizationType
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Visualization-specific parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "patient_123",
                "protocol_id": "protocol_456",
                "visualization_type": "real_time_gauge",
                "parameters": {
                    "decision_point": "treatment_selection",
                    "include_factors": True
                }
            }
        }

class GaugeVisualizationRequest(VisualizationRequest):
    """Request for real-time gauge visualization"""
    decision_point: str = Field(..., description="Specific decision point to visualize")
    show_factors: bool = Field(True, description="Include confidence factors breakdown")
    show_recommendations: bool = Field(True, description="Include actionable recommendations")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.visualization_type = VisualizationType.REAL_TIME_GAUGE

class TrendVisualizationRequest(VisualizationRequest):
    """Request for historical trend visualization"""
    days_back: int = Field(30, ge=1, le=365, description="Number of days to look back")
    include_thresholds: bool = Field(True, description="Show threshold lines")
    granularity: str = Field("daily", regex="^(hourly|daily|weekly)$", description="Data granularity")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.visualization_type = VisualizationType.HISTORICAL_TREND

class ComparativeVisualizationRequest(BaseModel):
    """Request for comparative analysis across patients"""
    patient_ids: List[str] = Field(..., min_items=2, max_items=10, description="Patient identifiers to compare")
    protocol_id: str = Field(..., description="Clinical protocol identifier")
    comparison_type: str = Field("box_plot", regex="^(box_plot|violin_plot|scatter)$")
    include_statistics: bool = Field(True, description="Include statistical analysis")
    
    @validator('patient_ids')
    def validate_patient_ids(cls, v):
        if len(set(v)) != len(v):
            raise ValueError("Duplicate patient IDs not allowed")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_ids": ["patient_123", "patient_456", "patient_789"],
                "protocol_id": "protocol_001",
                "comparison_type": "box_plot",
                "include_statistics": True
            }
        }

class ConfidenceMetrics(BaseModel):
    """Confidence score metrics and analysis"""
    current_score: float = Field(..., ge=0.0, le=1.0, description="Current confidence score")
    threshold: ConfidenceThreshold
    uncertainty: float = Field(..., ge=0.0, le=1.0, description="Uncertainty estimate")
    factors: Dict[ConfidenceFactor, float] = Field(..., description="Contributing factors")
    trend: str = Field(..., description="Recent trend direction")
    stability: float = Field(..., ge=0.0, le=1.0, description="Score stability measure")
    
    @validator('factors')
    def validate_factors(cls, v):
        for factor, value in v.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"Factor {factor} value must be between 0 and 1")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_score": 0.75,
                "threshold": "high",
                "uncertainty": 0.15,
                "factors": {
                    "data_completeness": 0.85,
                    "evidence_quality": 0.70,
                    "clinical_alignment": 0.80,
                    "protocol_adherence": 0.65
                },
                "trend": "improving",
                "stability": 0.80
            }
        }

class VisualizationResponse(BaseModel):
    """Base response for confidence visualizations"""
    visualization_type: VisualizationType
    chart_data: Union[str, Dict[str, Any]] = Field(..., description="Chart data (JSON or base64)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Visualization metadata")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "visualization_type": "real_time_gauge",
                "chart_data": "{'data': [...], 'layout': {...}}",
                "metadata": {
                    "patient_id": "patient_123",
                    "protocol_id": "protocol_456",
                    "confidence_score": 0.75
                },
                "generated_at": "2024-01-15T10:30:00Z"
            }
        }

class GaugeVisualizationResponse(VisualizationResponse):
    """Response for real-time gauge visualization"""
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    threshold: ConfidenceThreshold
    uncertainty: float = Field(..., ge=0.0, le=1.0)
    factors: Dict[str, float] = Field(..., description="Contributing factors")
    recommendations: List[str] = Field(..., description="Actionable recommendations")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.visualization_type = VisualizationType.REAL_TIME_GAUGE

class TrendVisualizationResponse(VisualizationResponse):
    """Response for historical trend visualization"""
    trend_statistics: Dict[str, Any] = Field(..., description="Statistical analysis of trends")
    data_points: int = Field(..., ge=0, description="Number of data points")
    date_range: Dict[str, str] = Field(..., description="Date range of analysis")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.visualization_type = VisualizationType.HISTORICAL_TREND

class ThresholdAnalysisResponse(VisualizationResponse):
    """Response for threshold analysis visualization"""
    threshold_distribution: Dict[str, int] = Field(..., description="Count by threshold")
    decision_outcomes: Dict[str, int] = Field(..., description="Count by outcome")
    total_decisions: int = Field(..., ge=0, description="Total number of decisions")
    recommendations: List[str] = Field(..., description="Pattern-based recommendations")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.visualization_type = VisualizationType.THRESHOLD_ANALYSIS

class ComparativeAnalysisResponse(VisualizationResponse):
    """Response for comparative analysis visualization"""
    patient_statistics: Dict[str, Dict[str, Any]] = Field(..., description="Per-patient statistics")
    comparison_analysis: Dict[str, Any] = Field(..., description="Cross-patient analysis")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.visualization_type = VisualizationType.COMPARATIVE_CHART

class UncertaintyVisualizationResponse(VisualizationResponse):
    """Response for uncertainty bands visualization"""
    uncertainty_analysis: Dict[str, Any] = Field(..., description="Uncertainty trend analysis")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.visualization_type = VisualizationType.UNCERTAINTY_BANDS

class ConfidenceFactorBreakdown(BaseModel):
    """Detailed breakdown of confidence factors"""
    factor: ConfidenceFactor
    value: float = Field(..., ge=0.0, le=1.0)
    weight: float = Field(..., ge=0.0, le=1.0, description="Factor weight in overall score")
    description: str = Field(..., description="Human-readable factor description")
    impact: str = Field(..., regex="^(positive|negative|neutral)$", description="Impact on confidence")
    recommendations: List[str] = Field(default_factory=list, description="Factor-specific recommendations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "factor": "data_completeness",
                "value": 0.85,
                "weight": 0.25,
                "description": "Percentage of required clinical data available",
                "impact": "positive",
                "recommendations": [
                    "Consider collecting missing lab values",
                    "Update patient medication history"
                ]
            }
        }

class ConfidenceHistory(BaseModel):
    """Historical confidence score data point"""
    timestamp: datetime
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    decision_point: str
    decision_outcome: Optional[str] = None
    factors: Dict[str, float] = Field(default_factory=dict)
    uncertainty: float = Field(0.1, ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-15T10:30:00Z",
                "confidence_score": 0.75,
                "decision_point": "treatment_selection",
                "decision_outcome": "approved",
                "factors": {
                    "data_completeness": 0.85,
                    "evidence_quality": 0.70
                },
                "uncertainty": 0.15
            }
        }

class ConfidenceDashboard(BaseModel):
    """Comprehensive confidence dashboard data"""
    current_metrics: ConfidenceMetrics
    recent_history: List[ConfidenceHistory] = Field(..., max_items=50)
    factor_breakdown: List[ConfidenceFactorBreakdown]
    alerts: List[str] = Field(default_factory=list, description="Current alerts and warnings")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_metrics": {
                    "current_score": 0.75,
                    "threshold": "high",
                    "uncertainty": 0.15,
                    "factors": {},
                    "trend": "improving",
                    "stability": 0.80
                },
                "recent_history": [],
                "factor_breakdown": [],
                "alerts": [
                    "Missing recent lab values",
                    "Protocol deviation detected"
                ],
                "recommendations": [
                    "Update patient assessment",
                    "Review treatment adherence"
                ],
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }

class VisualizationExportRequest(BaseModel):
    """Request for exporting visualizations"""
    visualization_type: VisualizationType
    export_format: str = Field(..., regex="^(png|pdf|svg|json)$", description="Export format")
    patient_id: str
    protocol_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    include_metadata: bool = Field(True, description="Include metadata in export")
    
    class Config:
        json_schema_extra = {
            "example": {
                "visualization_type": "historical_trend",
                "export_format": "pdf",
                "patient_id": "patient_123",
                "protocol_id": "protocol_456",
                "parameters": {"days_back": 30},
                "include_metadata": True
            }
        }

class VisualizationExportResponse(BaseModel):
    """Response for visualization export"""
    export_url: str = Field(..., description="URL to download exported file")
    file_size: int = Field(..., description="File size in bytes")
    expires_at: datetime = Field(..., description="URL expiration time")
    format: str = Field(..., description="File format")
    
    class Config:
        json_schema_extra = {
            "example": {
                "export_url": "https://api.example.com/exports/conf_viz_123.pdf",
                "file_size": 1048576,
                "expires_at": "2024-01-16T10:30:00Z",
                "format": "pdf"
            }
        }
