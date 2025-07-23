"""
Decision Engine API endpoints for clinical decision support
Handles ADCI, Gastrectomy, and FLOT protocol engines
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, validator
from datetime import datetime

from ...core.security import get_current_user, rbac_manager
from ...core.logging import clinical_logger, performance_logger
from ...db.database import get_async_session
from ...services.decision_engine_service import DecisionEngineService
from ...engines.adci_engine import ADCIEngine
from ...engines.gastrectomy_engine import GastrectomyEngine
from ...engines.flot_engine import FLOTEngine

router = APIRouter()


class DecisionRequest(BaseModel):
    """Decision engine request model"""
    engine_name: str
    patient_id: str
    clinical_parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    include_alternatives: bool = True
    confidence_threshold: float = 0.75
    
    @validator('engine_name')
    def validate_engine_name(cls, v):
        allowed_engines = ['adci', 'gastrectomy', 'flot']
        if v.lower() not in allowed_engines:
            raise ValueError(f'Engine must be one of: {allowed_engines}')
        return v.lower()
    
    @validator('confidence_threshold')
    def validate_confidence_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence threshold must be between 0.0 and 1.0')
        return v


class DecisionResponse(BaseModel):
    """Decision engine response model"""
    engine_name: str
    engine_version: str
    patient_id: str
    recommendation: Dict[str, Any]
    confidence_score: float
    confidence_level: str
    evidence_summary: List[Dict[str, Any]]
    reasoning_chain: List[Dict[str, Any]]
    alternative_options: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    monitoring_recommendations: Dict[str, Any]
    warnings: List[str]
    data_completeness: float
    processing_time_ms: float


class BatchDecisionRequest(BaseModel):
    """Batch decision request for multiple patients"""
    engine_name: str
    requests: List[Dict[str, Any]]
    max_concurrent: int = 5


@router.post("/process", response_model=DecisionResponse)
async def process_decision(
    request: DecisionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Process a clinical decision request"""
    
    # Check permissions
    if not rbac_manager.has_permission(current_user.get("role"), "access_decision_engines"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access decision engines"
        )
    
    start_time = datetime.now()
    
    try:
        decision_service = DecisionEngineService(db)
        
        # Validate patient access
        if not await decision_service.can_access_patient(current_user["sub"], request.patient_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to patient data"
            )
        
        # Get the appropriate engine
        engine = await _get_decision_engine(request.engine_name)
        
        # Process the decision
        result = await engine.process_decision(
            patient_id=request.patient_id,
            parameters=request.clinical_parameters,
            context=request.context,
            include_alternatives=request.include_alternatives,
            confidence_threshold=request.confidence_threshold
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Save result to database
        background_tasks.add_task(
            decision_service.save_decision_result,
            user_id=current_user["sub"],
            patient_id=request.patient_id,
            engine_name=request.engine_name,
            result=result
        )
        
        # Log decision engine usage
        clinical_logger.log_decision_engine_use(
            user_id=current_user["sub"],
            engine=request.engine_name,
            patient_id=request.patient_id,
            result={
                "confidence_score": result["confidence_score"],
                "recommendation_type": result["recommendation"].get("type"),
                "processing_time_ms": processing_time
            }
        )
        
        # Log performance
        performance_logger.log_decision_engine_performance(
            engine=request.engine_name,
            duration=processing_time / 1000,
            complexity=_assess_complexity(request.clinical_parameters)
        )
        
        # Format response
        return DecisionResponse(
            engine_name=request.engine_name,
            engine_version=result["engine_version"],
            patient_id=request.patient_id,
            recommendation=result["recommendation"],
            confidence_score=result["confidence_score"],
            confidence_level=result["confidence_level"],
            evidence_summary=result.get("evidence_summary", []),
            reasoning_chain=result.get("reasoning_chain", []),
            alternative_options=result.get("alternative_options", []),
            risk_assessment=result.get("risk_assessment", {}),
            monitoring_recommendations=result.get("monitoring_recommendations", {}),
            warnings=result.get("warnings", []),
            data_completeness=result.get("data_completeness", 1.0),
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        clinical_logger.log_decision_engine_use(
            user_id=current_user["sub"],
            engine=request.engine_name,
            patient_id=request.patient_id,
            result={"error": str(e)}
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decision processing failed: {str(e)}"
        )


@router.post("/batch-process")
async def batch_process_decisions(
    request: BatchDecisionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Process multiple decision requests in batch"""
    
    # Check permissions
    if not rbac_manager.has_permission(current_user.get("role"), "access_decision_engines"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access decision engines"
        )
    
    if current_user.get("role") not in ["researcher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Batch processing requires researcher or admin role"
        )
    
    try:
        decision_service = DecisionEngineService(db)
        
        # Process batch in background
        background_tasks.add_task(
            decision_service.process_batch_decisions,
            user_id=current_user["sub"],
            engine_name=request.engine_name,
            requests=request.requests,
            max_concurrent=request.max_concurrent
        )
        
        return {
            "message": f"Batch processing started for {len(request.requests)} requests",
            "engine": request.engine_name,
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing failed: {str(e)}"
        )


@router.get("/engines")
async def get_available_engines(
    current_user: dict = Depends(get_current_user)
):
    """Get list of available decision engines"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "access_decision_engines"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access decision engines"
        )
    
    return {
        "engines": [
            {
                "name": "adci",
                "display_name": "ADCI (Adaptive Decision Confidence Index)",
                "description": "Adaptive decision support with confidence scoring",
                "version": "2.1.0",
                "indication": "Gastric cancer treatment decisions",
                "parameters": [
                    "tumor_stage", "histology", "biomarkers", "performance_status",
                    "comorbidities", "patient_preferences"
                ]
            },
            {
                "name": "gastrectomy",
                "display_name": "Gastrectomy Planning Engine",
                "description": "Surgical approach and technique recommendations",
                "version": "1.5.2",
                "indication": "Gastric resection procedures",
                "parameters": [
                    "tumor_location", "tumor_size", "depth_invasion", "nodal_status",
                    "surgical_risk", "surgeon_experience"
                ]
            },
            {
                "name": "flot",
                "display_name": "FLOT Protocol Engine",
                "description": "Perioperative chemotherapy optimization",
                "version": "1.3.1",
                "indication": "Perioperative chemotherapy for gastric cancer",
                "parameters": [
                    "staging", "operability", "molecular_markers", "performance_status",
                    "renal_function", "cardiac_function"
                ]
            }
        ]
    }


@router.get("/engines/{engine_name}/parameters")
async def get_engine_parameters(
    engine_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed parameters for a specific engine"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "access_decision_engines"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access decision engines"
        )
    
    try:
        engine = await _get_decision_engine(engine_name)
        parameters = await engine.get_parameter_schema()
        
        return {
            "engine_name": engine_name,
            "parameters": parameters,
            "required_fields": engine.get_required_fields(),
            "optional_fields": engine.get_optional_fields(),
            "validation_rules": engine.get_validation_rules()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get engine parameters: {str(e)}"
        )


@router.get("/results/{patient_id}")
async def get_patient_decision_history(
    patient_id: str,
    engine_name: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get decision history for a patient"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "view_patient_data"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view patient data"
        )
    
    try:
        decision_service = DecisionEngineService(db)
        
        # Validate patient access
        if not await decision_service.can_access_patient(current_user["sub"], patient_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to patient data"
            )
        
        results = await decision_service.get_patient_decision_history(
            patient_id=patient_id,
            engine_name=engine_name,
            limit=limit
        )
        
        return {
            "patient_id": patient_id,
            "engine_filter": engine_name,
            "results": results,
            "total_count": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get decision history: {str(e)}"
        )


@router.get("/analytics/engine-usage")
async def get_engine_usage_analytics(
    days: int = 30,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get analytics on decision engine usage"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "access_analytics"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access analytics"
        )
    
    try:
        decision_service = DecisionEngineService(db)
        analytics = await decision_service.get_engine_usage_analytics(days=days)
        
        return {
            "period_days": days,
            "analytics": analytics,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )


async def _get_decision_engine(engine_name: str):
    """Get decision engine instance"""
    engines = {
        "adci": ADCIEngine,
        "gastrectomy": GastrectomyEngine,
        "flot": FLOTEngine
    }
    
    if engine_name not in engines:
        raise ValueError(f"Unknown engine: {engine_name}")
    
    return engines[engine_name]()


def _assess_complexity(parameters: Dict[str, Any]) -> str:
    """Assess complexity of decision request"""
    param_count = len(parameters)
    
    if param_count < 5:
        return "low"
    elif param_count < 10:
        return "medium"
    elif param_count < 20:
        return "high"
    else:
        return "very_high"
