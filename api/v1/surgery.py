"""
Surgery Analysis API Module for Collaborative Gastric ADCI Platform

This module provides API endpoints for comprehensive surgical analysis
with collaborative capabilities focused on gastric surgery with FLOT protocol
and ADCI decision framework integration.

The endpoints follow RESTful design with proper error handling and
HIPAA/GDPR compliance for healthcare data.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from core.dependencies import get_current_user
from core.models.surgery_models import SurgicalCaseModel, SurgicalAnalysisResult
from features.analysis.surgery_analyzer import IntegratedSurgeryAnalyzer
from core.services.logger import get_logger, audit_log

router = APIRouter(
    prefix="/surgery",
    tags=["surgery"],
    responses={404: {"description": "Not found"}}
)

logger = get_logger(__name__)
surgery_analyzer = IntegratedSurgeryAnalyzer()

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_surgery_case(
    case_data: SurgicalCaseModel,
    collaboration_mode: Optional[bool] = Query(False, description="Enable collaboration mode"),
    current_user: dict = Depends(get_current_user)
):
    """
    Comprehensive surgical case analysis endpoint with collaboration support.
    
    This endpoint performs a complete analysis of a surgical case, integrating:
    - ADCI decision framework analysis
    - FLOT protocol assessment
    - Risk assessment
    - Outcome prediction
    - Collaborative insights (if collaboration_mode is enabled)
    
    The analysis is optimized for gastric surgery cases with FLOT protocol.
    
    Args:
        case_data: Complete surgical case data
        collaboration_mode: Enable collaborative analysis features
        
    Returns:
        Comprehensive analysis with integrated ADCI, FLOT, and surgical assessment
    """
    # Log request with audit trail
    audit_log(
        action="analyze_surgery_case",
        resource_type="surgical_case",
        resource_id=case_data.case_id,
        user_id=current_user.get("id"),
        details=f"Surgical case analysis requested by {current_user.get('username')}"
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
                "tags": []
            }
        
        # Perform integrated analysis
        result = await surgery_analyzer.analyze_case(
            case_data.dict(),
            collaboration_context
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in surgery analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in surgery analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Surgery analysis failed: {str(e)}"
        )


@router.post("/collaborate/{case_id}", response_model=Dict[str, Any])
async def collaborate_on_case(
    case_id: str,
    collaboration_input: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Contribute to collaborative analysis of a surgical case.
    
    This endpoint allows team members to contribute insights, opinions,
    and evidence to an ongoing collaborative case analysis.
    
    Args:
        case_id: ID of the surgical case
        collaboration_input: Collaboration data including opinions, evidence, etc.
        
    Returns:
        Updated collaboration status and insights
    """
    # Log collaboration with audit trail
    audit_log(
        action="collaborate_on_case",
        resource_type="surgical_case",
        resource_id=case_id,
        user_id=current_user.get("id"),
        details=f"Collaboration contribution by {current_user.get('username')}"
    )
    
    try:
        # Validate collaboration input
        if "opinion" not in collaboration_input and "evidence" not in collaboration_input:
            raise ValueError("Collaboration must include either opinion or evidence")
        
        # TODO: In a full implementation, this would interact with a collaboration service
        # For MVP, we'll return a simulated response
        
        # Add the current user to contributors if not already present
        contributors = collaboration_input.get("existing_contributors", [])
        if current_user.get("username") not in contributors:
            contributors.append(current_user.get("username"))
        
        # Update consensus level based on input
        consensus_level = "reached" if collaboration_input.get("agrees_with_recommendation", True) else "divergent"
        
        # Track divergent opinions
        divergent_opinions = collaboration_input.get("existing_divergent_opinions", [])
        if not collaboration_input.get("agrees_with_recommendation", True):
            divergent_opinions.append({
                "contributor": current_user.get("username"),
                "opinion": collaboration_input.get("opinion", ""),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Compile collaboration result
        result = {
            "case_id": case_id,
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
            "next_steps": _generate_next_steps(
                consensus_level, 
                len(divergent_opinions)
            )
        }
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in collaboration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in collaboration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Collaboration failed: {str(e)}"
        )
        
def _generate_next_steps(consensus_level: str, divergent_count: int) -> List[str]:
    """Generate next steps based on collaboration status"""
    steps = []
    
    if consensus_level == "reached":
        steps.append("Proceed with agreed-upon treatment plan")
        steps.append("Document consensus in patient record")
        
    elif consensus_level == "divergent":
        steps.append("Schedule team discussion to address divergent opinions")
        
        if divergent_count > 2:
            steps.append("Consider additional expert consultation")
            
    else:  # pending
        steps.append("Await additional team input")
        
    return steps


@router.get("/cases/collaborative", response_model=List[Dict[str, Any]])
async def get_collaborative_cases(
    status: Optional[str] = Query(None, description="Filter by collaboration status"),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve a list of cases available for collaboration.
    
    This endpoint returns cases that are open for collaborative analysis,
    optionally filtered by collaboration status.
    
    Args:
        status: Optional filter for collaboration status
        
    Returns:
        List of collaborative cases with summary information
    """
    # TODO: In a full implementation, this would query a database
    # For MVP, we'll return a simulated response
    
    # Log request with audit trail
    audit_log(
        action="get_collaborative_cases",
        resource_type="collaborative_cases",
        user_id=current_user.get("id"),
        details=f"Collaborative cases requested by {current_user.get('username')}"
    )
    
    # Sample data for MVP
    cases = [
        {
            "case_id": "CS001",
            "patient_id": "PT10045",
            "diagnosis": "Gastric adenocarcinoma",
            "collaboration_status": "active",
            "contributor_count": 3,
            "last_updated": datetime.utcnow().isoformat(),
            "consensus_level": "pending"
        },
        {
            "case_id": "CS002",
            "patient_id": "PT10062",
            "diagnosis": "Gastric GIST",
            "collaboration_status": "completed",
            "contributor_count": 5,
            "last_updated": datetime.utcnow().isoformat(),
            "consensus_level": "reached"
        }
    ]
    
    # Apply status filter if provided
    if status:
        cases = [case for case in cases if case["collaboration_status"] == status]
    
    return cases


@router.get("/research/flot-impact", response_model=Dict[str, Any])
async def get_flot_impact_metrics(
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve aggregated research metrics on FLOT protocol impact.
    
    This endpoint provides aggregated research insights on the impact of
    FLOT protocol on surgical outcomes based on collaborative case analyses.
    
    Returns:
        Research metrics on FLOT protocol impact
    """
    # TODO: In a full implementation, this would analyze real data
    # For MVP, we'll return a simulated response
    
    # Log request with audit trail
    audit_log(
        action="get_flot_impact_metrics",
        resource_type="research_metrics",
        user_id=current_user.get("id"),
        details=f"FLOT impact metrics requested by {current_user.get('username')}"
    )
    
    return {
        "metrics_timestamp": datetime.utcnow().isoformat(),
        "data_points": 42,  # Placeholder
        "r0_resection_rate": {
            "with_flot": 0.85,
            "without_flot": 0.65,
            "improvement_percentage": 30.8,
            "confidence_interval": [20.5, 41.1]
        },
        "overall_survival": {
            "with_flot": {
                "median_months": 38.5,
                "three_year_rate": 0.57
            },
            "without_flot": {
                "median_months": 26.2,
                "three_year_rate": 0.42
            },
            "hazard_ratio": 0.72,
            "confidence_interval": [0.58, 0.89]
        },
        "surgical_outcomes": {
            "complication_rate": {
                "with_flot": 0.28,
                "without_flot": 0.32,
                "difference": -0.04
            },
            "reoperation_rate": {
                "with_flot": 0.12,
                "without_flot": 0.14,
                "difference": -0.02
            }
        },
        "protocol_adherence": {
            "completion_rate": 0.76,
            "dose_reduction_rate": 0.32,
            "early_termination_rate": 0.18
        },
        "research_insights": [
            "FLOT shows significant survival benefit in gastric cancer",
            "Preoperative FLOT may improve R0 resection rates",
            "Elderly patients (>75) show higher toxicity but maintained benefit",
            "Protocol adherence correlates with improved outcomes"
        ]
    }
        surgery_type: Type of surgery (defaults to case_data.surgery_type if not provided)
        current_user: Current authenticated user
        
    Returns:
        Dictionary containing comprehensive analysis results
    """
    try:
        # Use surgery_type from URL param or from case_data
        surgery_type = surgery_type or str(case_data.surgery_type)
        
        # Log the analysis request
        logger.info(f"Surgery analysis requested for case {case_data.case_id} "
                   f"by user {current_user.get('username')}")
        
        # Initialize integrated analyzer
        analyzer = IntegratedSurgeryAnalyzer()
        
        # Perform comprehensive analysis
        analysis_results = await analyzer.analyze_surgical_case(
            case_data.dict(), 
            surgery_type
        )
        
        # Generate actionable recommendations
        recommendations = await analyzer.generate_surgical_recommendations(
            analysis_results
        )
        
        # Calculate impact metrics
        impact_metrics = await analyzer.calculate_surgical_impact(
            case_data.dict(),
            analysis_results
        )
        
        # Return comprehensive response
        return {
            "status": "success",
            "case_id": case_data.case_id,
            "surgery_type": surgery_type,
            "analysis": analysis_results,
            "recommendations": recommendations,
            "impact_metrics": impact_metrics,
            "analyzed_by": current_user.get("username"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Surgery analysis failed for case {case_data.case_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Surgery analysis failed: {str(e)}"
        )


@router.post("/gastric-flot", response_model=Dict[str, Any])
async def analyze_gastric_flot_case(
    case_data: SurgicalCaseModel,
    current_user: dict = Depends(get_current_user)
):
    """
    Specialized gastric cancer FLOT protocol analysis.
    
    This endpoint provides focused analysis for gastric cancer cases
    following the FLOT protocol with specialized surgical planning.
    
    Args:
        case_data: Surgical case data for gastric cancer
        current_user: Current authenticated user
        
    Returns:
        Dictionary containing specialized gastric FLOT analysis
    """
    if case_data.surgery_type != "gastric_flot":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint is only for gastric FLOT cases"
        )
    
    return await analyze_surgery_case(case_data, "gastric_flot", current_user)


@router.post("/colorectal-eras", response_model=Dict[str, Any])
async def analyze_colorectal_eras_case(
    case_data: SurgicalCaseModel,
    current_user: dict = Depends(get_current_user)
):
    """
    Specialized colorectal surgery ERAS protocol analysis.
    
    This endpoint provides focused analysis for colorectal cancer cases
    following the Enhanced Recovery After Surgery (ERAS) protocol.
    
    Args:
        case_data: Surgical case data for colorectal cancer
        current_user: Current authenticated user
        
    Returns:
        Dictionary containing specialized colorectal ERAS analysis
    """
    if case_data.surgery_type != "colorectal_eras":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint is only for colorectal ERAS cases"
        )
    
    return await analyze_surgery_case(case_data, "colorectal_eras", current_user)


@router.post("/emergency", response_model=Dict[str, Any])
async def analyze_emergency_surgery_case(
    case_data: SurgicalCaseModel,
    current_user: dict = Depends(get_current_user)
):
    """
    Emergency surgery analysis.
    
    This endpoint provides rapid analysis for emergency surgical cases
    with optimized critical pathways.
    
    Args:
        case_data: Emergency surgical case data
        current_user: Current authenticated user
        
    Returns:
        Dictionary containing emergency surgery analysis
    """
    if case_data.surgery_type != "emergency":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint is only for emergency surgery cases"
        )
    
    return await analyze_surgery_case(case_data, "emergency", current_user)


@router.get("/protocols/{surgery_type}", response_model=Dict[str, Any])
async def get_surgery_protocol(
    surgery_type: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get standard protocol information for a surgery type.
    
    This endpoint provides the standard protocol elements, best practices,
    and evidence-based guidelines for a specific surgery type.
    
    Args:
        surgery_type: Type of surgery (gastric_flot, colorectal_eras, etc.)
        current_user: Current authenticated user
        
    Returns:
        Dictionary containing protocol information
    """
    try:
        # Initialize integrated analyzer
        analyzer = IntegratedSurgeryAnalyzer()
        
        # Get protocol manager
        protocol_manager = analyzer.protocol_manager
        
        # Create minimal case data to get standard protocol
        minimal_case = {
            "case_id": "protocol-info",
            "patient_id": "none",
            "age": 65,
            "gender": "male"
        }
        
        # Get protocol information
        protocol_info = protocol_manager.select_optimal_protocol(minimal_case, surgery_type)
        
        return {
            "status": "success",
            "surgery_type": surgery_type,
            "protocol_information": protocol_info,
            "requested_by": current_user.get("username"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get protocol information for {surgery_type}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Protocol information retrieval failed: {str(e)}"
        )
