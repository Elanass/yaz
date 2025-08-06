"""
Enhanced Feedback API - Comprehensive Feedback and Continuous Improvement System
Handles deliverable feedback, outcome validation, and algorithm improvement
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from statistics import mean
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.models.processing_models import (
    AggregatedFeedback,
    FeedbackData,
    FeedbackType,
)
from ...core.services.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/feedback", tags=["Feedback"])


# Enhanced Pydantic Models
class DeliverableFeedbackRequest(BaseModel):
    """Feedback specifically for deliverables"""

    deliverable_id: str
    feedback_type: FeedbackType
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)
    specific_field: Optional[str] = None
    suggested_value: Optional[str] = None
    accuracy_assessment: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


class OutcomeValidationRequest(BaseModel):
    """Validation of predicted outcomes against actual results"""

    deliverable_id: str
    predicted_values: Dict[str, Any]
    actual_values: Dict[str, Any]
    validation_date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Response for feedback submission"""

    success: bool
    feedback_id: str
    message: str
    improvement_triggered: bool = False


class FeedbackAnalytics(BaseModel):
    """Analytics on collected feedback"""

    total_feedback_count: int
    average_rating: float
    feedback_by_type: Dict[str, int]
    recent_trends: Dict[str, Any]
    improvement_actions: List[str]


# In-memory storage (replace with database in production)
feedback_store = {}
outcome_validations = {}
improvement_metrics = {
    "algorithm_accuracy": [],
    "user_satisfaction": [],
    "feedback_trends": {},
}


@router.post("/deliverable", response_model=FeedbackResponse)
async def submit_deliverable_feedback(
    feedback_request: DeliverableFeedbackRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Submit feedback for a specific deliverable
    """
    try:
        feedback_id = str(uuid.uuid4())

        # Create feedback data
        feedback_data = FeedbackData(
            deliverable_id=feedback_request.deliverable_id,
            feedback_type=feedback_request.feedback_type,
            rating=feedback_request.rating,
            comment=feedback_request.comment,
            specific_field=feedback_request.specific_field,
            suggested_value=feedback_request.suggested_value,
            user_id=None,  # Would be extracted from auth in production
        )

        # Store feedback
        feedback_store[feedback_id] = feedback_data

        # Trigger improvement analysis in background
        background_tasks.add_task(
            analyze_feedback_for_improvements, feedback_data, feedback_id
        )

        logger.info(
            f"Feedback submitted for deliverable {feedback_request.deliverable_id}"
        )

        return FeedbackResponse(
            success=True,
            feedback_id=feedback_id,
            message="Feedback submitted successfully",
            improvement_triggered=True,
        )

    except Exception as e:
        logger.error(f"Error submitting deliverable feedback: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to submit feedback: {str(e)}"
        )


@router.post("/outcome-validation", response_model=FeedbackResponse)
async def submit_outcome_validation(
    validation_request: OutcomeValidationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Submit validation of predicted outcomes against actual results
    """
    try:
        validation_id = str(uuid.uuid4())

        # Store outcome validation
        outcome_validations[validation_id] = validation_request

        # Calculate accuracy metrics
        accuracy_metrics = calculate_prediction_accuracy(
            validation_request.predicted_values, validation_request.actual_values
        )

        # Update algorithm performance tracking
        background_tasks.add_task(
            update_algorithm_performance,
            validation_request.deliverable_id,
            accuracy_metrics,
        )

        logger.info(
            f"Outcome validation submitted for deliverable {validation_request.deliverable_id}"
        )

        return FeedbackResponse(
            success=True,
            feedback_id=validation_id,
            message="Outcome validation submitted successfully",
            improvement_triggered=True,
        )

    except Exception as e:
        logger.error(f"Error submitting outcome validation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to submit validation: {str(e)}"
        )


@router.get("/analytics", response_model=FeedbackAnalytics)
async def get_feedback_analytics(
    deliverable_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """
    Get analytics on collected feedback
    """
    try:
        # Filter feedback based on criteria
        filtered_feedback = feedback_store.values()

        if not filtered_feedback:
            return FeedbackAnalytics(
                total_feedback_count=0,
                average_rating=0.0,
                feedback_by_type={},
                recent_trends={},
                improvement_actions=[],
            )

        # Calculate analytics
        total_count = len(filtered_feedback)

        # Average rating
        ratings = [f.rating for f in filtered_feedback if f.rating is not None]
        avg_rating = mean(ratings) if ratings else 0.0

        # Feedback by type
        feedback_by_type = {}
        for feedback in filtered_feedback:
            fb_type = feedback.feedback_type.value
            feedback_by_type[fb_type] = feedback_by_type.get(fb_type, 0) + 1

        # Recent trends (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_feedback = [
            f for f in filtered_feedback if f.timestamp >= thirty_days_ago
        ]

        recent_trends = {
            "recent_count": len(recent_feedback),
            "rating_trend": "stable",  # Would calculate actual trend
            "common_issues": extract_common_issues(recent_feedback),
        }

        # Generate improvement actions
        improvement_actions = generate_improvement_actions(filtered_feedback)

        return FeedbackAnalytics(
            total_feedback_count=total_count,
            average_rating=avg_rating,
            feedback_by_type=feedback_by_type,
            recent_trends=recent_trends,
            improvement_actions=improvement_actions,
        )

    except Exception as e:
        logger.error(f"Error getting feedback analytics: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get analytics: {str(e)}"
        )


@router.get("/deliverable/{deliverable_id}")
async def get_deliverable_feedback(deliverable_id: str, db: Session = Depends(get_db)):
    """
    Get all feedback for a specific deliverable
    """
    try:
        deliverable_feedback = [
            {
                "feedback_id": fid,
                "feedback_type": feedback.feedback_type.value,
                "rating": feedback.rating,
                "comment": feedback.comment,
                "timestamp": feedback.timestamp.isoformat(),
                "specific_field": feedback.specific_field,
            }
            for fid, feedback in feedback_store.items()
            if feedback.deliverable_id == deliverable_id
        ]

        # Calculate summary statistics
        ratings = [f["rating"] for f in deliverable_feedback if f["rating"] is not None]
        summary = {
            "total_feedback": len(deliverable_feedback),
            "average_rating": mean(ratings) if ratings else None,
            "rating_distribution": {i: ratings.count(i) for i in range(1, 6)}
            if ratings
            else {},
            "feedback_by_type": {},
        }

        # Count by type
        for feedback in deliverable_feedback:
            fb_type = feedback["feedback_type"]
            summary["feedback_by_type"][fb_type] = (
                summary["feedback_by_type"].get(fb_type, 0) + 1
            )

        return {
            "deliverable_id": deliverable_id,
            "summary": summary,
            "feedback": deliverable_feedback,
        }

    except Exception as e:
        logger.error(f"Error getting deliverable feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get feedback: {str(e)}")


@router.get("/performance-metrics")
async def get_performance_metrics(db: Session = Depends(get_db)):
    """
    Get algorithm performance metrics based on feedback and validations
    """
    try:
        # Calculate accuracy metrics from outcome validations
        accuracy_scores = []
        for validation in outcome_validations.values():
            accuracy = calculate_prediction_accuracy(
                validation.predicted_values, validation.actual_values
            )
            accuracy_scores.append(accuracy["overall_accuracy"])

        # User satisfaction from ratings
        ratings = [f.rating for f in feedback_store.values() if f.rating is not None]
        satisfaction_score = mean(ratings) / 5.0 if ratings else 0.0  # Normalize to 0-1

        # Model performance trends
        performance_trends = {
            "accuracy_trend": calculate_trend(
                improvement_metrics["algorithm_accuracy"]
            ),
            "satisfaction_trend": calculate_trend(
                improvement_metrics["user_satisfaction"]
            ),
            "improvement_velocity": calculate_improvement_velocity(),
        }

        return {
            "current_metrics": {
                "prediction_accuracy": mean(accuracy_scores)
                if accuracy_scores
                else 0.0,
                "user_satisfaction": satisfaction_score,
                "total_validations": len(outcome_validations),
                "total_feedback": len(feedback_store),
            },
            "trends": performance_trends,
            "improvement_opportunities": identify_improvement_opportunities(),
        }

    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


# Legacy feedback endpoint (backward compatibility)
@router.post("/")
async def submit_feedback(feedback_request: dict):
    """Submit general feedback (legacy endpoint)"""
    try:
        feedback_id = str(uuid.uuid4())
        feedback_data = {
            **feedback_request,
            "id": feedback_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store in legacy format for backward compatibility
        if "legacy_feedback" not in globals():
            globals()["legacy_feedback"] = []

        globals()["legacy_feedback"].append(feedback_data)

        return {
            "message": "Feedback submitted successfully",
            "status": "success",
            "id": feedback_id,
        }

    except Exception as e:
        logger.error(f"Error submitting legacy feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


# Background task functions
async def analyze_feedback_for_improvements(
    feedback_data: FeedbackData, feedback_id: str
):
    """
    Analyze feedback to trigger algorithm improvements
    """
    try:
        # Check for patterns in feedback
        if feedback_data.rating is not None and feedback_data.rating < 3:
            logger.warning(f"Low rating feedback received: {feedback_id}")

            # Trigger specific improvement actions based on feedback type
            if feedback_data.feedback_type == FeedbackType.CORRECTION:
                await trigger_algorithm_correction(feedback_data)
            elif feedback_data.feedback_type == FeedbackType.SUGGESTION:
                await process_improvement_suggestion(feedback_data)

        # Update improvement metrics
        if feedback_data.rating:
            improvement_metrics["user_satisfaction"].append(feedback_data.rating)

        logger.info(f"Feedback analysis completed for: {feedback_id}")

    except Exception as e:
        logger.error(f"Error analyzing feedback: {str(e)}")


async def update_algorithm_performance(
    deliverable_id: str, accuracy_metrics: Dict[str, float]
):
    """
    Update algorithm performance metrics based on outcome validation
    """
    try:
        # Store accuracy metrics
        improvement_metrics["algorithm_accuracy"].append(
            accuracy_metrics["overall_accuracy"]
        )

        # Check if performance is declining
        recent_accuracies = improvement_metrics["algorithm_accuracy"][
            -10:
        ]  # Last 10 measurements
        if len(recent_accuracies) >= 5:
            recent_avg = mean(recent_accuracies[-5:])
            older_avg = mean(recent_accuracies[:-5])

            if recent_avg < older_avg * 0.95:  # 5% decline
                logger.warning("Algorithm performance decline detected")
                await trigger_model_retraining()

        logger.info(f"Algorithm performance updated for deliverable: {deliverable_id}")

    except Exception as e:
        logger.error(f"Error updating algorithm performance: {str(e)}")


# Helper functions
def calculate_prediction_accuracy(
    predicted: Dict[str, Any], actual: Dict[str, Any]
) -> Dict[str, float]:
    """Calculate accuracy metrics between predicted and actual values"""
    if not predicted or not actual:
        return {"overall_accuracy": 0.0}

    # Simple accuracy calculation for common keys
    common_keys = set(predicted.keys()) & set(actual.keys())
    if not common_keys:
        return {"overall_accuracy": 0.0}

    correct_predictions = 0
    total_predictions = len(common_keys)

    for key in common_keys:
        pred_val = predicted[key]
        actual_val = actual[key]

        # Handle different types of comparisons
        if isinstance(pred_val, (int, float)) and isinstance(actual_val, (int, float)):
            # Numeric comparison with tolerance
            if (
                abs(pred_val - actual_val) / max(abs(actual_val), 1) < 0.1
            ):  # 10% tolerance
                correct_predictions += 1
        else:
            # Exact match for categorical
            if str(pred_val).lower() == str(actual_val).lower():
                correct_predictions += 1

    overall_accuracy = (
        correct_predictions / total_predictions if total_predictions > 0 else 0.0
    )

    return {
        "overall_accuracy": overall_accuracy,
        "correct_predictions": correct_predictions,
        "total_predictions": total_predictions,
    }


def extract_common_issues(feedback_list: List[FeedbackData]) -> List[str]:
    """Extract common issues from feedback comments"""
    issues = []
    for feedback in feedback_list:
        if feedback.comment and feedback.rating and feedback.rating < 3:
            # Simple keyword extraction (would use NLP in production)
            if "accuracy" in feedback.comment.lower():
                issues.append("accuracy_concerns")
            if "slow" in feedback.comment.lower():
                issues.append("performance_issues")
            if "confusing" in feedback.comment.lower():
                issues.append("usability_issues")

    # Return most common issues
    from collections import Counter

    issue_counts = Counter(issues)
    return [issue for issue, count in issue_counts.most_common(5)]


def generate_improvement_actions(feedback_list: List[FeedbackData]) -> List[str]:
    """Generate actionable improvement recommendations based on feedback"""
    actions = []

    # Analyze ratings
    ratings = [f.rating for f in feedback_list if f.rating is not None]
    if ratings:
        avg_rating = mean(ratings)
        if avg_rating < 3.5:
            actions.append("Review and improve algorithm accuracy")
        if len([r for r in ratings if r <= 2]) > len(ratings) * 0.2:
            actions.append("Investigate major issues causing low ratings")

    # Analyze feedback types
    correction_count = len(
        [f for f in feedback_list if f.feedback_type == FeedbackType.CORRECTION]
    )
    if correction_count > 5:
        actions.append("Implement systematic correction learning")

    suggestion_count = len(
        [f for f in feedback_list if f.feedback_type == FeedbackType.SUGGESTION]
    )
    if suggestion_count > 3:
        actions.append("Review user suggestions for feature improvements")

    return actions


def calculate_trend(values: List[float]) -> str:
    """Calculate trend direction from a list of values"""
    if len(values) < 2:
        return "insufficient_data"

    recent = values[-min(5, len(values)) :]  # Last 5 values
    older = values[: -len(recent)] if len(values) > len(recent) else []

    if not older:
        return "insufficient_data"

    recent_avg = mean(recent)
    older_avg = mean(older)

    if recent_avg > older_avg * 1.05:
        return "improving"
    elif recent_avg < older_avg * 0.95:
        return "declining"
    else:
        return "stable"


def calculate_improvement_velocity() -> float:
    """Calculate how quickly the system is improving based on feedback"""
    # Simple velocity calculation based on satisfaction trends
    satisfaction_scores = improvement_metrics["user_satisfaction"]
    if len(satisfaction_scores) < 10:
        return 0.0

    # Compare recent month vs previous month
    recent_month = (
        satisfaction_scores[-30:]
        if len(satisfaction_scores) >= 30
        else satisfaction_scores[-len(satisfaction_scores) // 2 :]
    )
    previous_month = (
        satisfaction_scores[-60:-30]
        if len(satisfaction_scores) >= 60
        else satisfaction_scores[: -len(recent_month)]
    )

    if not previous_month:
        return 0.0

    recent_avg = mean(recent_month)
    previous_avg = mean(previous_month)

    return (recent_avg - previous_avg) / previous_avg if previous_avg > 0 else 0.0


def identify_improvement_opportunities() -> List[str]:
    """Identify specific opportunities for improvement"""
    opportunities = []

    # Check accuracy trends
    accuracy_scores = improvement_metrics["algorithm_accuracy"]
    if accuracy_scores and mean(accuracy_scores[-5:]) < 0.85:
        opportunities.append("Improve prediction accuracy through model refinement")

    # Check satisfaction trends
    satisfaction_scores = improvement_metrics["user_satisfaction"]
    if satisfaction_scores and mean(satisfaction_scores[-10:]) < 3.5:
        opportunities.append("Enhance user experience and interface design")

    # Check feedback patterns
    if len(feedback_store) > 10:
        low_rating_count = len(
            [f for f in feedback_store.values() if f.rating and f.rating <= 2]
        )
        if low_rating_count / len(feedback_store) > 0.2:
            opportunities.append("Address critical issues causing user dissatisfaction")

    return opportunities


async def trigger_algorithm_correction(feedback_data: FeedbackData):
    """Trigger algorithm correction based on user feedback"""
    logger.info(
        f"Triggering algorithm correction for field: {feedback_data.specific_field}"
    )
    # Implementation would involve retraining or adjusting algorithms


async def process_improvement_suggestion(feedback_data: FeedbackData):
    """Process improvement suggestions from users"""
    logger.info(f"Processing improvement suggestion: {feedback_data.comment}")
    # Implementation would log suggestions for development team review


async def trigger_model_retraining():
    """Trigger model retraining when performance declines"""
    logger.warning("Triggering model retraining due to performance decline")
    # Implementation would start retraining pipeline
