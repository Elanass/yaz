"""
ADCI Decision Framework API Module for Decision Precision in Surgery

This module provides API endpoints for the Adaptive Decision Confidence Index (ADCI)
framework, focused on gastric surgery with FLOT protocol impact assessment and
precision decision-making capabilities.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Dict, Any, List, Optional
from datetime import datetime

from features.decisions.adci_engine import ADCIEngine
from core.dependencies import get_current_user
from core.services.logger import get_logger, audit_log
from core.utils.validation import validate_patient_data, validate_collaboration_input

router = APIRouter(
    prefix="/adci",
    tags=["adci"],
    responses={404: {"description": "Not found"}}
)

logger = get_logger(__name__)
adci_engine = ADCIEngine()

@router.post("/predict", response_model=Dict[str, Any])
async def predict_adci(
    patient_data: dict,
    collaboration_mode: Optional[bool] = Query(False, description="Enable collaboration mode"),
    current_user: dict = Depends(get_current_user)
):
    """
    API endpoint to predict outcomes using the ADCI engine with collaboration support.
    
    This endpoint provides comprehensive ADCI analysis for gastric surgery cases,
    with optional collaboration features.
    
    Args:
        patient_data: Complete patient clinical data
        collaboration_mode: Enable collaborative analysis features
        
    Returns:
        ADCI prediction with confidence metrics and FLOT integration
    """
    # Log request with audit trail
    patient_id = patient_data.get("patient_id", "unknown")
    audit_log(
        action="adci_predict",
        resource_type="patient_data",
        resource_id=patient_id,
        user_id=current_user.get("id"),
        details=f"ADCI prediction requested by {current_user.get('username')}"
    )
    
    # Validate input
    is_valid, missing_fields = validate_patient_data(patient_data, "adci")
    if not is_valid:
        logger.error(f"Invalid input data for ADCI prediction: {patient_id}, missing: {missing_fields}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input data for ADCI engine: missing {', '.join(missing_fields)}"
        )

    try:
        # Create collaboration context if collaboration mode is enabled
        collaboration_context = None
        if collaboration_mode:
            collaboration_context = {
                "contributors": [current_user.get("username")],
                "consensus_level": "pending",
                "stage": "initial",
                "divergent_opinions": [],
                "flags": []
            }
            
        # Get ADCI prediction
        prediction = await adci_engine.predict(patient_data, collaboration_context)
        return prediction
        
    except Exception as e:
        logger.error(f"Error in ADCI prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ADCI prediction failed: {str(e)}"
        )

@router.post("/collaborate/{patient_id}", response_model=Dict[str, Any])
async def collaborate_on_adci(
    patient_id: str,
    collaboration_input: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Contribute to collaborative ADCI analysis.
    
    This endpoint allows team members to contribute insights, opinions,
    and evidence to an ongoing collaborative ADCI analysis.
    
    Args:
        patient_id: ID of the patient
        collaboration_input: Collaboration data including opinions, evidence, etc.
        
    Returns:
        Updated ADCI collaboration status and insights
    """
    # Log collaboration with audit trail
    audit_log(
        action="collaborate_on_adci",
        resource_type="patient_data",
        resource_id=patient_id,
        user_id=current_user.get("id"),
        details=f"ADCI collaboration contribution by {current_user.get('username')}"
    )
    
    try:
        # Validate collaboration input
        is_valid, error_message = validate_collaboration_input(collaboration_input)
        if not is_valid:
            raise ValueError(error_message)
        
        # TODO: In a full implementation, this would interact with a collaboration service
        # For MVP, we'll return a simulated response
        
        # Add the current user to contributors if not already present
        contributors = collaboration_input.get("existing_contributors", [])
        if current_user.get("username") not in contributors:
            contributors.append(current_user.get("username"))
        
        # Update consensus level based on input
        consensus_level = "reached" if collaboration_input.get("agrees_with_adci", True) else "divergent"
        
        # Track divergent opinions
        divergent_opinions = collaboration_input.get("existing_divergent_opinions", [])
        if not collaboration_input.get("agrees_with_adci", True):
            divergent_opinions.append({
                "contributor": current_user.get("username"),
                "opinion": collaboration_input.get("opinion", ""),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Compile collaboration result
        result = {
            "patient_id": patient_id,
            "collaboration_status": {
                "contributors": contributors,
                "contributor_count": len(contributors),
                "consensus_level": consensus_level,
                "divergent_opinions": divergent_opinions,
                "latest_contribution": {
                    "contributor": current_user.get("username"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "opinion" if "opinion" in collaboration_input else "evidence"
                }
            },
            "adci_impact": {
                "confidence_adjustment": _calculate_confidence_adjustment(contributors, divergent_opinions),
                "key_insights": _extract_key_insights(collaboration_input)
            },
            "next_steps": _generate_adci_next_steps(consensus_level, len(divergent_opinions))
        }
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in ADCI collaboration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in ADCI collaboration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ADCI collaboration failed: {str(e)}"
        )

@router.get("/research/confidence-metrics", response_model=Dict[str, Any])
async def get_adci_confidence_metrics(
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve aggregated research metrics on ADCI confidence performance.
    
    This endpoint provides aggregated research insights on ADCI confidence
    metrics and their correlation with actual outcomes.
    
    Returns:
        Research metrics on ADCI confidence performance
    """
    # TODO: In a full implementation, this would analyze real data
    # For MVP, we'll return a simulated response
    
    # Log request with audit trail
    audit_log(
        action="get_adci_confidence_metrics",
        resource_type="research_metrics",
        user_id=current_user.get("id"),
        details=f"ADCI confidence metrics requested by {current_user.get('username')}"
    )
    
    return {
        "metrics_timestamp": datetime.utcnow().isoformat(),
        "data_points": 78,  # Placeholder
        "confidence_calibration": {
            "high_confidence_cases": {
                "count": 45,
                "accuracy": 0.91,
                "confidence_interval": [0.85, 0.96]
            },
            "medium_confidence_cases": {
                "count": 22,
                "accuracy": 0.77,
                "confidence_interval": [0.68, 0.86]
            },
            "low_confidence_cases": {
                "count": 11,
                "accuracy": 0.55,
                "confidence_interval": [0.42, 0.68]
            }
        },
        "collaboration_impact": {
            "solo_assessment": {
                "average_confidence": 0.78,
                "accuracy": 0.81
            },
            "collaborative_assessment": {
                "average_confidence": 0.82,
                "accuracy": 0.89
            },
            "improvement_percentage": 9.9
        },
        "decision_changes": {
            "percentage_changed_after_collaboration": 0.23,
            "improved_outcome_rate": 0.18
        },
        "research_insights": [
            "Collaborative ADCI shows improved decision accuracy",
            "High confidence cases reliably predict surgical outcomes",
            "Cases with confidence <0.7 benefit most from multidisciplinary input",
            "Integration with FLOT protocol analysis enhances prediction specificity"
        ]
    }

def _calculate_confidence_adjustment(contributors: List[str], 
                                   divergent_opinions: List[Dict[str, Any]]) -> float:
    """
    Calculate confidence adjustment based on collaboration
    
    Args:
        contributors: List of contributors
        divergent_opinions: List of divergent opinions
        
    Returns:
        Confidence adjustment factor (-1.0 to 1.0)
    """
    # Implementation would calculate appropriate adjustment
    # Simplified implementation for MVP
    
    # More contributors with consensus increases confidence
    contributor_factor = min(len(contributors) * 0.05, 0.2)
    
    # Divergent opinions decrease confidence
    divergent_factor = -min(len(divergent_opinions) * 0.1, 0.3)
    
    return contributor_factor + divergent_factor

def _extract_key_insights(collaboration_input: Dict[str, Any]) -> List[str]:
    """Extract key insights from collaboration input"""
    # Implementation would extract meaningful insights
    # Simplified implementation for MVP
    
    insights = []
    
    if "evidence" in collaboration_input:
        insights.append(f"New evidence: {collaboration_input['evidence'][:50]}...")
        
    if "opinion" in collaboration_input:
        insights.append(f"Clinical assessment: {collaboration_input['opinion'][:50]}...")
        
    if "critical_factors" in collaboration_input:
        for factor in collaboration_input.get("critical_factors", []):
            insights.append(f"Critical factor identified: {factor}")
            
    return insights

def _generate_adci_next_steps(consensus_level: str, divergent_count: int) -> List[str]:
    """Generate next steps based on ADCI collaboration status"""
    steps = []
    
    if consensus_level == "reached":
        steps.append("Proceed with ADCI-recommended approach")
        steps.append("Document consensus in decision support record")
        
    elif consensus_level == "divergent":
        steps.append("Review divergent opinions in multidisciplinary setting")
        
        if divergent_count > 2:
            steps.append("Consider additional diagnostic workup")
            steps.append("Re-evaluate ADCI inputs")
            
    else:  # pending
        steps.append("Collect additional team input")
        
    return steps
