"""
Clinical Quality Schemas - Pydantic models for decision explainability and quality assurance.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class FeatureImportance(BaseModel):
    """Feature importance for decision explanation."""
    
    feature_name: str = Field(..., description="Name of the feature")
    importance_score: float = Field(..., ge=0, le=1, description="Importance score (0-1)")
    direction: str = Field(..., description="Impact direction (positive, negative, neutral)")
    value: str = Field(..., description="Actual feature value")
    interpretation: str = Field(..., description="Clinical interpretation")
    confidence: float = Field(1.0, ge=0, le=1, description="Confidence in importance")
    
    @validator("direction")
    def validate_direction(cls, v):
        allowed_directions = ["positive", "negative", "neutral"]
        if v not in allowed_directions:
            raise ValueError(f"Direction must be one of: {', '.join(allowed_directions)}")
        return v


class ClinicalReasoning(BaseModel):
    """Clinical reasoning explanation."""
    
    primary_factors: List[str] = Field(..., description="Primary factors influencing decision")
    supporting_evidence: List[str] = Field(..., description="Supporting clinical evidence")
    alternative_considerations: List[str] = Field(..., description="Alternative approaches considered")
    contraindications: List[str] = Field([], description="Identified contraindications")
    risk_factors: List[str] = Field([], description="Risk factors identified")
    mitigation_strategies: List[str] = Field([], description="Risk mitigation strategies")


class DecisionExplanation(BaseModel):
    """Comprehensive decision explanation."""
    
    decision_id: UUID = Field(..., description="Decision identifier")
    natural_explanation: str = Field(..., description="Natural language explanation")
    feature_importance: List[FeatureImportance] = Field(..., description="Feature importance analysis")
    clinical_reasoning: ClinicalReasoning = Field(..., description="Clinical reasoning")
    confidence_metrics: Dict[str, float] = Field(..., description="Detailed confidence metrics")
    similar_cases: List[Dict[str, Any]] = Field([], description="Similar historical cases")
    evidence_quality: Dict[str, Any] = Field(..., description="Quality of underlying evidence")
    guideline_alignment: Dict[str, Any] = Field(..., description="Alignment with guidelines")
    uncertainty_sources: List[str] = Field([], description="Sources of uncertainty")
    recommendations: List[str] = Field([], description="Additional recommendations")
    generated_at: datetime = Field(..., description="Explanation generation timestamp")


class ConcordancePattern(BaseModel):
    """Human-AI concordance pattern."""
    
    decision_id: str = Field(..., description="Decision identifier")
    ai_recommendation: str = Field(..., description="AI recommendation")
    human_decision: str = Field(..., description="Human final decision")
    confidence_score: float = Field(..., ge=0, le=1, description="AI confidence score")
    case_complexity: str = Field(..., description="Case complexity level")
    discordance_reason: str = Field(..., description="Reason for discordance")
    clinical_context: Dict[str, Any] = Field({}, description="Additional clinical context")


class ConcordanceAnalysis(BaseModel):
    """Human-AI concordance analysis results."""
    
    timeframe_days: int = Field(..., description="Analysis timeframe in days")
    total_decisions: int = Field(..., description="Total decisions analyzed")
    concordance_rate: float = Field(..., ge=0, le=1, description="Overall concordance rate")
    concordance_by_complexity: Dict[str, float] = Field({}, description="Concordance by case complexity")
    concordance_by_confidence: Dict[str, float] = Field({}, description="Concordance by AI confidence")
    discordance_patterns: List[ConcordancePattern] = Field([], description="Discordance patterns")
    user_specific: bool = Field(False, description="Whether analysis is user-specific")
    analysis_date: datetime = Field(..., description="Analysis timestamp")
    recommendations: List[str] = Field([], description="Improvement recommendations")


class GuidelineRule(BaseModel):
    """Clinical guideline rule."""
    
    rule_id: str = Field(..., description="Rule identifier")
    description: str = Field(..., description="Rule description")
    condition: str = Field(..., description="Rule condition")
    recommendation: str = Field(..., description="Rule recommendation")
    strength: str = Field(..., description="Recommendation strength")
    evidence_level: str = Field(..., description="Evidence level")
    
    @validator("strength")
    def validate_strength(cls, v):
        allowed_strengths = ["strong", "weak", "conditional"]
        if v not in allowed_strengths:
            raise ValueError(f"Strength must be one of: {', '.join(allowed_strengths)}")
        return v
    
    @validator("evidence_level")
    def validate_evidence_level(cls, v):
        allowed_levels = ["high", "moderate", "low", "very_low"]
        if v not in allowed_levels:
            raise ValueError(f"Evidence level must be one of: {', '.join(allowed_levels)}")
        return v


class GuidelineCompliance(BaseModel):
    """Guideline compliance assessment."""
    
    decision_id: UUID = Field(..., description="Decision identifier")
    guideline_set: str = Field(..., description="Guideline set used")
    overall_compliance: bool = Field(..., description="Overall compliance status")
    compliance_score: float = Field(..., ge=0, le=1, description="Compliance score (0-1)")
    guideline_results: List[Dict[str, Any]] = Field(..., description="Individual guideline results")
    deviations: List[Dict[str, Any]] = Field([], description="Identified deviations")
    recommendations: List[str] = Field([], description="Compliance recommendations")
    checked_at: datetime = Field(..., description="Compliance check timestamp")


class QualityMetrics(BaseModel):
    """Clinical decision quality metrics."""
    
    overall_score: float = Field(..., ge=0, le=1, description="Overall quality score")
    explanation_quality: float = Field(..., ge=0, le=1, description="Explanation quality score")
    guideline_compliance: float = Field(..., ge=0, le=1, description="Guideline compliance score")
    evidence_strength: float = Field(..., ge=0, le=1, description="Evidence strength score")
    clinical_appropriateness: float = Field(..., ge=0, le=1, description="Clinical appropriateness score")
    risk_assessment_accuracy: float = Field(..., ge=0, le=1, description="Risk assessment accuracy")
    recommendation_clarity: float = Field(..., ge=0, le=1, description="Recommendation clarity score")
    uncertainty_handling: float = Field(..., ge=0, le=1, description="Uncertainty handling quality")


class QualityAssessment(BaseModel):
    """Comprehensive quality assessment."""
    
    decision_id: UUID = Field(..., description="Decision identifier")
    overall_score: float = Field(..., ge=0, le=1, description="Overall quality score")
    explanation_quality: float = Field(..., ge=0, le=1, description="Explanation quality")
    guideline_compliance: float = Field(..., ge=0, le=1, description="Guideline compliance")
    evidence_strength: float = Field(..., ge=0, le=1, description="Evidence strength")
    clinical_appropriateness: float = Field(..., ge=0, le=1, description="Clinical appropriateness")
    risk_assessment_accuracy: float = Field(..., ge=0, le=1, description="Risk assessment accuracy")
    recommendation_clarity: float = Field(..., ge=0, le=1, description="Recommendation clarity")
    uncertainty_handling: float = Field(..., ge=0, le=1, description="Uncertainty handling")
    strengths: List[str] = Field([], description="Identified strengths")
    areas_for_improvement: List[str] = Field([], description="Areas for improvement")
    action_items: List[str] = Field([], description="Recommended actions")
    assessed_at: datetime = Field(..., description="Assessment timestamp")


class ExplainabilityReport(BaseModel):
    """Comprehensive explainability report."""
    
    period_start: datetime = Field(..., description="Report period start")
    period_end: datetime = Field(..., description="Report period end")
    total_decisions: int = Field(..., description="Total decisions analyzed")
    average_explanation_score: float = Field(..., ge=0, le=1, description="Average explanation score")
    average_confidence_score: float = Field(..., ge=0, le=1, description="Average confidence score")
    complexity_distribution: Dict[str, int] = Field(..., description="Case complexity distribution")
    top_uncertainty_sources: List[str] = Field([], description="Top sources of uncertainty")
    improvement_recommendations: List[str] = Field([], description="Improvement recommendations")
    generated_at: datetime = Field(..., description="Report generation timestamp")


class UncertaintySource(BaseModel):
    """Source of uncertainty in decision making."""
    
    source_type: str = Field(..., description="Type of uncertainty source")
    description: str = Field(..., description="Description of uncertainty")
    impact_level: str = Field(..., description="Impact level on decision")
    mitigation_strategies: List[str] = Field([], description="Suggested mitigation strategies")
    
    @validator("source_type")
    def validate_source_type(cls, v):
        allowed_types = [
            "data_quality", "model_limitation", "clinical_variability",
            "guideline_ambiguity", "evidence_gap", "patient_factors"
        ]
        if v not in allowed_types:
            raise ValueError(f"Source type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator("impact_level")
    def validate_impact_level(cls, v):
        allowed_levels = ["low", "medium", "high", "critical"]
        if v not in allowed_levels:
            raise ValueError(f"Impact level must be one of: {', '.join(allowed_levels)}")
        return v


class ClinicalConsistencyCheck(BaseModel):
    """Clinical consistency verification."""
    
    decision_id: UUID = Field(..., description="Decision identifier")
    consistency_score: float = Field(..., ge=0, le=1, description="Consistency score")
    internal_consistency: bool = Field(..., description="Internal logic consistency")
    temporal_consistency: bool = Field(..., description="Consistency with previous decisions")
    peer_consistency: bool = Field(..., description="Consistency with peer decisions")
    inconsistencies: List[str] = Field([], description="Identified inconsistencies")
    recommendations: List[str] = Field([], description="Consistency recommendations")


class ExplanationTemplate(BaseModel):
    """Template for generating explanations."""
    
    template_id: str = Field(..., description="Template identifier")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    template_text: str = Field(..., description="Template text with placeholders")
    required_variables: List[str] = Field(..., description="Required template variables")
    optional_variables: List[str] = Field([], description="Optional template variables")
    target_audience: str = Field(..., description="Target audience")
    complexity_level: str = Field(..., description="Explanation complexity level")
    
    @validator("target_audience")
    def validate_target_audience(cls, v):
        allowed_audiences = ["patient", "clinician", "researcher", "administrator"]
        if v not in allowed_audiences:
            raise ValueError(f"Target audience must be one of: {', '.join(allowed_audiences)}")
        return v
    
    @validator("complexity_level")
    def validate_complexity_level(cls, v):
        allowed_levels = ["basic", "intermediate", "advanced", "expert"]
        if v not in allowed_levels:
            raise ValueError(f"Complexity level must be one of: {', '.join(allowed_levels)}")
        return v


class ClinicalInsight(BaseModel):
    """Clinical insight derived from decision analysis."""
    
    insight_type: str = Field(..., description="Type of clinical insight")
    description: str = Field(..., description="Insight description")
    supporting_evidence: List[str] = Field(..., description="Supporting evidence")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in insight")
    clinical_relevance: str = Field(..., description="Clinical relevance")
    actionable_recommendations: List[str] = Field([], description="Actionable recommendations")
    
    @validator("insight_type")
    def validate_insight_type(cls, v):
        allowed_types = [
            "pattern_recognition", "risk_factor_identification", "outcome_prediction",
            "treatment_optimization", "resource_utilization", "quality_improvement"
        ]
        if v not in allowed_types:
            raise ValueError(f"Insight type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator("clinical_relevance")
    def validate_clinical_relevance(cls, v):
        allowed_relevance = ["high", "medium", "low"]
        if v not in allowed_relevance:
            raise ValueError(f"Clinical relevance must be one of: {', '.join(allowed_relevance)}")
        return v


class QualityDashboard(BaseModel):
    """Quality dashboard metrics."""
    
    period_start: datetime = Field(..., description="Dashboard period start")
    period_end: datetime = Field(..., description="Dashboard period end")
    total_decisions: int = Field(..., description="Total decisions in period")
    average_quality_score: float = Field(..., ge=0, le=1, description="Average quality score")
    quality_distribution: Dict[str, int] = Field(..., description="Quality score distribution")
    guideline_compliance_rate: float = Field(..., ge=0, le=1, description="Guideline compliance rate")
    human_ai_concordance_rate: float = Field(..., ge=0, le=1, description="Human-AI concordance rate")
    top_quality_issues: List[str] = Field([], description="Top quality issues identified")
    improvement_trends: Dict[str, float] = Field({}, description="Quality improvement trends")
    generated_at: datetime = Field(..., description="Dashboard generation timestamp")


class PeerReviewRequest(BaseModel):
    """Peer review request for decision quality."""
    
    decision_id: UUID = Field(..., description="Decision to review")
    reviewer_requirements: List[str] = Field([], description="Reviewer requirements")
    review_priority: str = Field("normal", description="Review priority")
    review_deadline: Optional[datetime] = Field(None, description="Review deadline")
    specific_questions: List[str] = Field([], description="Specific review questions")
    
    @validator("review_priority")
    def validate_review_priority(cls, v):
        allowed_priorities = ["low", "normal", "high", "urgent"]
        if v not in allowed_priorities:
            raise ValueError(f"Review priority must be one of: {', '.join(allowed_priorities)}")
        return v


class PeerReviewResponse(BaseModel):
    """Peer review response."""
    
    review_id: UUID = Field(..., description="Review identifier")
    decision_id: UUID = Field(..., description="Decision reviewed")
    reviewer_id: UUID = Field(..., description="Reviewer identifier")
    overall_assessment: str = Field(..., description="Overall assessment")
    quality_rating: int = Field(..., ge=1, le=5, description="Quality rating (1-5)")
    agreement_with_recommendation: bool = Field(..., description="Agreement with recommendation")
    specific_feedback: List[str] = Field([], description="Specific feedback points")
    suggested_improvements: List[str] = Field([], description="Suggested improvements")
    reviewed_at: datetime = Field(..., description="Review completion timestamp")
    
    @validator("overall_assessment")
    def validate_overall_assessment(cls, v):
        allowed_assessments = ["excellent", "good", "acceptable", "needs_improvement", "inadequate"]
        if v not in allowed_assessments:
            raise ValueError(f"Overall assessment must be one of: {', '.join(allowed_assessments)}")
        return v
