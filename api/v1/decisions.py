"""
API v1 - Decision Routes
Clean, standardized decision engine endpoints
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks

from core.models.base import ApiResponse, DecisionStatus
from core.config.platform_config import config
from features.auth.service import User, get_current_user, require_permission, Domain, Scope
from features.decisions.service import (
    DecisionService, DecisionRequest, DecisionResponse
)
from features.analysis.job_manager import (
    submit_adci_prediction_job, submit_flot_analysis_job, 
    get_job_status, wait_for_job_result
)

router = APIRouter(prefix="/decisions", tags=["Decisions"])
decision_service = DecisionService()


@router.post("/analyze", response_model=ApiResponse[DecisionResponse])
async def create_decision_analysis(
    request: DecisionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_permission(Domain.HEALTHCARE, Scope.WRITE))
):
    """Create a new decision analysis"""
    
    try:
        # Start job processing in the background
        job_id = await submit_adci_prediction_job(
            patient_data=request.patient_data,
            collaboration_context=request.dict().get("collaboration_context")
        )
        
        # In development, we might want to wait for the result
        if config.environment == "development":
            try:
                # Wait up to 10 seconds for result
                result = await wait_for_job_result(job_id, timeout=10)
                if result:
                    # Create decision record
                    decision = await decision_service.create_decision_from_result(
                        result=result,
                        request=request,
                        user_id=str(current_user.id)
                    )
                    
                    return ApiResponse.success_response(
                        data=decision,
                        message="Decision analysis completed"
                    )
            except ValueError as e:
                # Continue with async flow if timeout
                pass
        
        # Register the job and return the job ID
        decision = await decision_service.register_decision_job(
            job_id=job_id,
            request=request,
            user_id=str(current_user.id)
        )
        
        # Add background task to update the decision when job completes
        background_tasks.add_task(
            decision_service.update_decision_from_job,
            decision_id=decision.id,
            job_id=job_id
        )
        
        return ApiResponse.success_response(
            data=decision,
            message="Decision analysis submitted and processing"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decision analysis failed: {str(e)}"
        )


@router.get("/{decision_id}", response_model=ApiResponse[DecisionResponse])
async def get_decision_by_id(
    decision_id: str,
    current_user: User = Depends(require_permission(Domain.HEALTHCARE, Scope.READ))
):
    """Get decision analysis by ID"""
    
    decision = await decision_service.get_decision(decision_id)
    
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    
    return ApiResponse.success_response(
        data=decision,
        message="Decision retrieved"
    )


@router.get("/", response_model=ApiResponse[List[DecisionResponse]])
async def list_decisions(
    engine_type: Optional[str] = Query(None, description="Filter by engine type"),
    status_filter: Optional[DecisionStatus] = Query(None, alias="status", description="Filter by status"),
    current_user: User = Depends(require_permission(Domain.HEALTHCARE, Scope.READ))
):
    """List decision analyses with optional filters"""
    
    # Regular users can only see their own decisions
    user_id = str(current_user.id) if current_user.role not in ["admin", "researcher"] else None
    
    decisions = await decision_service.list_decisions(
        user_id=user_id,
        engine_type=engine_type,
        status=status_filter
    )
    
    return ApiResponse.success_response(
        data=decisions,
        message=f"Retrieved {len(decisions)} decisions",
        meta={
            "count": len(decisions),
            "filters": {
                "engine_type": engine_type,
                "status": status_filter
            }
        }
    )


@router.get("/engines/available", response_model=ApiResponse[List[dict]])
async def list_available_engines(
    current_user: User = Depends(require_permission(Domain.HEALTHCARE, Scope.READ))
):
    """List available decision engines and their capabilities"""
    
    engines = [
        {
            "type": "adci",
            "name": "Adaptive Decision Confidence Index",
            "description": "AI-powered decision support for gastric cancer treatment",
            "input_requirements": [
                "patient_data.age",
                "patient_data.performance_status", 
                "tumor_data.stage",
                "tumor_data.location"
            ],
            "output_format": {
                "primary_treatment": "string",
                "urgency": "string",
                "sequence": "string (optional)"
            }
        },
        {
            "type": "gastrectomy",
            "name": "Gastrectomy Surgical Planner", 
            "description": "Surgical approach planning for gastrectomy procedures",
            "input_requirements": [
                "patient_data.age",
                "patient_data.bmi",
                "tumor_data.location",
                "tumor_data.size_cm"
            ],
            "output_format": {
                "procedure": "string",
                "approach": "string",
                "lymphadenectomy": "string"
            }
        }
    ]
    
    return ApiResponse.success_response(
        data=engines,
        message="Available decision engines"
    )


@router.post("/validate-input", response_model=ApiResponse[dict])
async def validate_decision_input(
    request: DecisionRequest,
    current_user: User = Depends(require_permission(Domain.HEALTHCARE, Scope.READ))
):
    """Validate decision input without running analysis"""
    
    try:
        # Get engine
        engine = decision_service.engines.get(request.engine_type)
        if not engine:
            raise ValueError(f"Unknown engine type: {request.engine_type}")
        
        # Validate input
        errors = engine.validate_input(request.patient_data, request.tumor_data)
        
        validation_result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "engine_type": request.engine_type
        }
        
        if errors:
            return ApiResponse.error_response(
                message="Input validation failed",
                errors=errors,
                data=validation_result
            )
        else:
            return ApiResponse.success_response(
                data=validation_result,
                message="Input validation passed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/stats/summary", response_model=ApiResponse[dict])
async def get_decision_statistics(
    current_user: User = Depends(require_permission(Domain.HEALTHCARE, Scope.READ))
):
    """Get decision analysis statistics"""
    
    # Calculate statistics from stored decisions
    all_decisions = list(decision_service.decisions.values())
    
    # Filter by user if not admin/researcher
    if current_user.role not in ["admin", "researcher"]:
        all_decisions = [d for d in all_decisions if d.user_id == str(current_user.id)]
    
    stats = {
        "total_decisions": len(all_decisions),
        "by_status": {},
        "by_engine": {},
        "avg_confidence": 0.0,
        "avg_processing_time_ms": 0.0
    }
    
    if all_decisions:
        # Group by status
        for decision in all_decisions:
            status_key = decision.status.value
            stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1
        
        # Group by engine
        for decision in all_decisions:
            engine_key = decision.engine_type
            stats["by_engine"][engine_key] = stats["by_engine"].get(engine_key, 0) + 1
        
        # Calculate averages
        completed_decisions = [d for d in all_decisions if d.status == DecisionStatus.COMPLETED]
        if completed_decisions:
            stats["avg_confidence"] = sum(d.confidence_score or 0 for d in completed_decisions) / len(completed_decisions)
            stats["avg_processing_time_ms"] = sum(d.processing_time_ms or 0 for d in completed_decisions) / len(completed_decisions)
    
    return ApiResponse.success_response(
        data=stats,
        message="Decision statistics retrieved"
    )
