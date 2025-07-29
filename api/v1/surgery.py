"""
Surgery Analysis API Module

This module provides API endpoints for comprehensive surgical analysis
including various surgery types like gastric surgery with FLOT protocol,
colorectal surgery with ERAS protocol, and others.

The endpoints follow RESTful design with proper error handling and
HIPAA/GDPR compliance for healthcare data.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from core.dependencies import get_current_user
from core.models.surgery_models import SurgicalCaseModel, SurgicalAnalysisResult
from features.analysis.surgery_analyzer import IntegratedSurgeryAnalyzer

router = APIRouter(
    prefix="/surgery",
    tags=["surgery"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_surgery_case(
    case_data: SurgicalCaseModel,
    surgery_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Comprehensive surgical case analysis endpoint.
    
    This endpoint performs a complete analysis of a surgical case, including:
    - Risk assessment
    - Protocol selection and customization
    - Outcome prediction
    - Quality metrics calculation
    - Decision support recommendations
    
    The analysis is tailored to the specific surgery type (e.g., gastric_flot,
    colorectal_eras, hepatobiliary, emergency, general).
    
    Args:
        case_data: Complete surgical case data
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
