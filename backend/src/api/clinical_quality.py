"""
Clinical Quality API - Decision explainability and human-AI concordance endpoints.
"""

import logging
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import get_current_user, get_db
from ..db.models import User
from ..schemas.clinical_quality import (
    DecisionExplanation,
    ConcordanceAnalysis,
    GuidelineCompliance,
    QualityAssessment,
    ExplainabilityReport,
    QualityDashboard,
    ClinicalInsight,
    ExplanationTemplate,
    PeerReviewRequest,
    PeerReviewResponse,
    UncertaintySource,
    ClinicalConsistencyCheck,
)
from ..services.clinical_quality_service import ClinicalQualityService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/clinical-quality", tags=["Clinical Quality"])
quality_service = ClinicalQualityService()


@router.get("/explain/{decision_id}", response_model=DecisionExplanation)
async def explain_decision(
    decision_id: UUID,
    level: str = Query("detailed", description="Explanation level: brief, summary, detailed"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate comprehensive explanation for a clinical decision."""
    try:
        if level not in ["brief", "summary", "detailed"]:
            raise HTTPException(
                status_code=400, detail="Level must be brief, summary, or detailed"
            )
        
        explanation = await quality_service.generate_decision_explanation(
            db, decision_id, level
        )
        return explanation
    except Exception as e:
        logger.error(f"Failed to explain decision: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to explain decision")


@router.get("/concordance", response_model=ConcordanceAnalysis)
async def analyze_concordance(
    timeframe_days: int = Query(30, ge=1, le=365, description="Analysis timeframe in days"),
    user_id: Optional[UUID] = Query(None, description="Specific user analysis"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze human-AI decision concordance."""
    try:
        # Check if user has permission for system-wide analysis
        if user_id is None and not current_user.is_admin:
            user_id = current_user.id  # Restrict to current user if not admin
        
        analysis = await quality_service.analyze_human_ai_concordance(
            db, timeframe_days, user_id
        )
        return analysis
    except Exception as e:
        logger.error(f"Failed to analyze concordance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze concordance")


@router.get("/compliance/{decision_id}", response_model=GuidelineCompliance)
async def check_guideline_compliance(
    decision_id: UUID,
    guideline_set: Optional[str] = Query(None, description="Specific guideline set"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check decision compliance with clinical guidelines."""
    try:
        compliance = await quality_service.check_guideline_compliance(
            db, decision_id, guideline_set
        )
        return compliance
    except Exception as e:
        logger.error(f"Failed to check guideline compliance: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to check guideline compliance"
        )


@router.get("/assess/{decision_id}", response_model=QualityAssessment)
async def assess_decision_quality(
    decision_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Perform comprehensive quality assessment of a clinical decision."""
    try:
        assessment = await quality_service.assess_decision_quality(db, decision_id)
        return assessment
    except Exception as e:
        logger.error(f"Failed to assess decision quality: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to assess decision quality"
        )


@router.get("/report/explainability", response_model=ExplainabilityReport)
async def generate_explainability_report(
    days: int = Query(30, ge=1, le=365, description="Report period in days"),
    user_id: Optional[UUID] = Query(None, description="Specific user filter"),
    specialty: Optional[str] = Query(None, description="Medical specialty filter"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate comprehensive explainability report."""
    try:
        # Build filters
        filters = {"days": days}
        if user_id:
            filters["user_id"] = user_id
        if specialty:
            filters["specialty"] = specialty
        
        # Check permissions for system-wide reports
        if user_id is None and not current_user.is_admin:
            filters["user_id"] = current_user.id
        
        report = await quality_service.generate_explainability_report(db, filters)
        return report
    except Exception as e:
        logger.error(f"Failed to generate explainability report: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to generate explainability report"
        )


@router.get("/dashboard", response_model=QualityDashboard)
async def get_quality_dashboard(
    days: int = Query(30, ge=1, le=365, description="Dashboard period in days"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get quality dashboard metrics."""
    try:
        # Implementation would generate dashboard metrics
        # For now, return mock data
        
        from datetime import datetime, timedelta
        
        dashboard = QualityDashboard(
            period_start=datetime.utcnow() - timedelta(days=days),
            period_end=datetime.utcnow(),
            total_decisions=0,
            average_quality_score=0.85,
            quality_distribution={"excellent": 0, "good": 0, "acceptable": 0, "poor": 0},
            guideline_compliance_rate=0.92,
            human_ai_concordance_rate=0.87,
            top_quality_issues=[],
            improvement_trends={},
            generated_at=datetime.utcnow(),
        )
        
        return dashboard
    except Exception as e:
        logger.error(f"Failed to get quality dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get quality dashboard")


@router.get("/insights", response_model=List[ClinicalInsight])
async def get_clinical_insights(
    category: Optional[str] = Query(None, description="Insight category filter"),
    relevance: Optional[str] = Query(None, description="Clinical relevance filter"),
    limit: int = Query(10, ge=1, le=50, description="Maximum insights to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get clinical insights derived from decision analysis."""
    try:
        # Implementation would generate insights from decision patterns
        # For now, return mock data
        
        insights = [
            ClinicalInsight(
                insight_type="pattern_recognition",
                description="High concordance observed for early-stage gastric cancer decisions",
                supporting_evidence=[
                    "95% concordance rate for T1-T2 tumors",
                    "Consistent across different clinicians",
                    "Strong guideline alignment"
                ],
                confidence_level=0.92,
                clinical_relevance="high",
                actionable_recommendations=[
                    "Standardize early-stage decision protocols",
                    "Create automated decision support for routine cases"
                ],
            ),
            ClinicalInsight(
                insight_type="risk_factor_identification",
                description="Age and comorbidity burden are primary discordance factors",
                supporting_evidence=[
                    "Lower concordance for patients >75 years",
                    "Multiple comorbidities increase uncertainty",
                    "Subjective assessment variations"
                ],
                confidence_level=0.88,
                clinical_relevance="high",
                actionable_recommendations=[
                    "Develop geriatric-specific decision tools",
                    "Implement structured comorbidity assessment"
                ],
            ),
        ]
        
        # Apply filters
        if category:
            insights = [i for i in insights if i.insight_type == category]
        if relevance:
            insights = [i for i in insights if i.clinical_relevance == relevance]
        
        return insights[:limit]
    except Exception as e:
        logger.error(f"Failed to get clinical insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get clinical insights")


@router.get("/templates", response_model=List[ExplanationTemplate])
async def get_explanation_templates(
    audience: Optional[str] = Query(None, description="Target audience filter"),
    complexity: Optional[str] = Query(None, description="Complexity level filter"),
):
    """Get explanation templates."""
    try:
        templates = [
            ExplanationTemplate(
                template_id="surgical_recommendation_clinician",
                name="Surgical Recommendation for Clinicians",
                description="Detailed surgical recommendation explanation for clinical audience",
                template_text="Based on {patient_factors} and {tumor_characteristics}, surgical resection is recommended. Key factors include {primary_factors}. The recommendation aligns with {guidelines} with {confidence}% confidence.",
                required_variables=["patient_factors", "tumor_characteristics", "primary_factors", "guidelines", "confidence"],
                optional_variables=["contraindications", "alternative_approaches"],
                target_audience="clinician",
                complexity_level="advanced",
            ),
            ExplanationTemplate(
                template_id="treatment_plan_patient",
                name="Treatment Plan for Patients",
                description="Patient-friendly treatment plan explanation",
                template_text="Your treatment plan includes {treatment_type} because {simple_reason}. This approach has been successful in similar cases and follows established medical guidelines.",
                required_variables=["treatment_type", "simple_reason"],
                optional_variables=["success_rate", "timeline", "side_effects"],
                target_audience="patient",
                complexity_level="basic",
            ),
        ]
        
        # Apply filters
        if audience:
            templates = [t for t in templates if t.target_audience == audience]
        if complexity:
            templates = [t for t in templates if t.complexity_level == complexity]
        
        return templates
    except Exception as e:
        logger.error(f"Failed to get explanation templates: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to get explanation templates"
        )


@router.get("/uncertainty/{decision_id}", response_model=List[UncertaintySource])
async def analyze_uncertainty_sources(
    decision_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze sources of uncertainty in a decision."""
    try:
        # Implementation would analyze uncertainty sources
        # For now, return mock data
        
        sources = [
            UncertaintySource(
                source_type="data_quality",
                description="Incomplete staging information",
                impact_level="medium",
                mitigation_strategies=[
                    "Request additional imaging studies",
                    "Consider staging laparoscopy"
                ],
            ),
            UncertaintySource(
                source_type="clinical_variability",
                description="Subjective assessment of performance status",
                impact_level="low",
                mitigation_strategies=[
                    "Use standardized performance status scales",
                    "Obtain multidisciplinary assessment"
                ],
            ),
        ]
        
        return sources
    except Exception as e:
        logger.error(f"Failed to analyze uncertainty sources: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to analyze uncertainty sources"
        )


@router.get("/consistency/{decision_id}", response_model=ClinicalConsistencyCheck)
async def check_clinical_consistency(
    decision_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check clinical consistency of a decision."""
    try:
        # Implementation would check consistency
        # For now, return mock data
        
        consistency = ClinicalConsistencyCheck(
            decision_id=decision_id,
            consistency_score=0.92,
            internal_consistency=True,
            temporal_consistency=True,
            peer_consistency=True,
            inconsistencies=[],
            recommendations=[],
        )
        
        return consistency
    except Exception as e:
        logger.error(f"Failed to check clinical consistency: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to check clinical consistency"
        )


@router.post("/peer-review", response_model=Dict[str, str])
async def request_peer_review(
    review_request: PeerReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Request peer review for a decision."""
    try:
        # Implementation would create peer review request
        # For now, return success message
        
        return {
            "message": "Peer review request submitted",
            "decision_id": str(review_request.decision_id),
            "priority": review_request.review_priority,
        }
    except Exception as e:
        logger.error(f"Failed to request peer review: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to request peer review")


@router.get("/peer-reviews", response_model=List[Dict[str, str]])
async def get_pending_reviews(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get pending peer review requests."""
    try:
        # Implementation would fetch pending reviews
        # For now, return empty list
        
        return []
    except Exception as e:
        logger.error(f"Failed to get pending reviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get pending reviews")


@router.post("/peer-review/{review_id}/respond")
async def submit_peer_review(
    review_id: UUID,
    review_response: PeerReviewResponse,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit peer review response."""
    try:
        # Implementation would store peer review response
        # For now, return success message
        
        return {
            "message": "Peer review submitted successfully",
            "review_id": str(review_id),
            "rating": review_response.quality_rating,
        }
    except Exception as e:
        logger.error(f"Failed to submit peer review: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit peer review")


@router.get("/benchmarks")
async def get_quality_benchmarks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get quality benchmarks and targets."""
    try:
        benchmarks = {
            "explanation_quality": {
                "target": 0.85,
                "current": 0.82,
                "trend": "improving",
            },
            "guideline_compliance": {
                "target": 0.95,
                "current": 0.92,
                "trend": "stable",
            },
            "human_ai_concordance": {
                "target": 0.85,
                "current": 0.87,
                "trend": "improving",
            },
            "peer_review_agreement": {
                "target": 0.80,
                "current": 0.78,
                "trend": "declining",
            },
        }
        
        return benchmarks
    except Exception as e:
        logger.error(f"Failed to get quality benchmarks: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get quality benchmarks")
