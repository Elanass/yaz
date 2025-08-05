"""
Enhanced Cases API - Surgify Platform
Modular, high-performance endpoints with caching and proper service separation
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session

from surgify.core.database import get_db
from surgify.core.services.case_service import (
    CaseService as EnhancedCaseService, 
    CaseCreateRequest, 
    CaseUpdateRequest, 
    CaseResponse,
    CaseListFilters
)
from surgify.core.services.auth_service import get_current_user
from surgify.core.models.user import User
from surgify.core.cache import cache_list_endpoint, cache_detail_endpoint, invalidate_cache

router = APIRouter(tags=["Cases"])

def get_case_service(db: Session = Depends(get_db)) -> EnhancedCaseService:
    """Dependency to get case service instance"""
    return EnhancedCaseService(db)

@router.get("/", response_model=List[CaseResponse])
@cache_list_endpoint("cases", ttl=60)  # Cache for 1 minute
async def list_cases(
    status: Optional[str] = Query(None, description="Filter by case status"),
    procedure_type: Optional[str] = Query(None, description="Filter by procedure type"),
    surgeon_id: Optional[str] = Query(None, description="Filter by surgeon ID"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    search: Optional[str] = Query(None, description="Search cases"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    case_service: EnhancedCaseService = Depends(get_case_service)
):
    """
    List all surgical cases with filtering, pagination, and sorting.
    
    This endpoint is **stateless** and **idempotent** - multiple calls with the same
    parameters will return the same results. Results are cached for performance.
    
    **Filtering Options:**
    - status: Filter by case status (planned, in_progress, completed, cancelled)
    - procedure_type: Filter by procedure type
    - surgeon_id: Filter by assigned surgeon
    - priority: Filter by priority level (low, medium, high, urgent)
    - patient_id: Filter by patient identifier
    - search: Search across case number, patient ID, diagnosis, and procedure type
    
    **Pagination:**
    - page: Page number (starting from 1)
    - limit: Number of items per page (1-100)
    
    **Sorting:**
    - sort_by: Field to sort by (default: created_at)
    - sort_order: Sort direction (asc/desc)
    """
    try:
        filters = CaseListFilters(
            status=status,
            procedure_type=procedure_type,
            surgeon_id=surgeon_id,
            priority=priority,
            patient_id=patient_id,
            search=search
        )
        
        cases = await case_service.list_cases(
            filters=filters,
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return cases
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cases: {str(e)}"
        )

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    request: CaseCreateRequest,
    case_service: EnhancedCaseService = Depends(get_case_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new surgical case.
    
    This endpoint is **stateless** - it doesn't maintain any in-process state.
    Each request creates a new case with a unique case number.
    
    **Required Fields:**
    - patient_id: Unique identifier for the patient
    - procedure_type: Type of surgical procedure
    
    **Optional Fields:**
    - diagnosis: Patient diagnosis
    - status: Case status (default: "planned")
    - priority: Case priority (default: "medium")
    - surgeon_id: Assigned surgeon identifier
    - scheduled_date: Scheduled date/time for procedure
    - notes: Additional notes
    
    **Response:**
    Returns the created case with generated case number, timestamps, and
    calculated risk score and recommendations.
    """
    try:
        case = await case_service.create_case(request, current_user.username)
        
        # Invalidate related caches
        await invalidate_cache("cases")
        
        return case
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating case: {str(e)}"
        )

@router.get("/{case_id}", response_model=CaseResponse)
@cache_detail_endpoint("cases", ttl=300)  # Cache for 5 minutes
async def get_case(
    case_id: int,
    case_service: EnhancedCaseService = Depends(get_case_service)
):
    """
    Get a specific surgical case by ID.
    
    This endpoint is **stateless** and **idempotent** - multiple calls with the same
    case_id will return the same result. Results are cached for performance.
    
    **Response:**
    Returns complete case details including:
    - Basic case information
    - Patient and surgeon details
    - Scheduling information
    - Risk assessment and recommendations
    - Audit trail (created/updated timestamps)
    """
    try:
        case = await case_service.get_case(case_id)
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case with ID {case_id} not found"
            )
        
        return case
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving case: {str(e)}"
        )

@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: int,
    request: CaseUpdateRequest,
    case_service: EnhancedCaseService = Depends(get_case_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing surgical case.
    
    This endpoint is **idempotent** - multiple calls with the same data will
    result in the same final state.
    
    **Partial Updates:**
    Only provided fields will be updated. Omitted fields remain unchanged.
    
    **Updatable Fields:**
    - patient_id: Patient identifier
    - procedure_type: Procedure type
    - diagnosis: Patient diagnosis
    - status: Case status
    - priority: Case priority
    - surgeon_id: Assigned surgeon
    - scheduled_date: Scheduled procedure date/time
    - notes: Additional notes
    
    **Response:**
    Returns the updated case with refreshed timestamps and recalculated
    risk score and recommendations.
    """
    try:
        case = await case_service.update_case(case_id, request, current_user.username)
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case with ID {case_id} not found"
            )
        
        # Invalidate related caches
        await invalidate_cache("cases")
        await invalidate_cache("cases", id=case_id)
        
        return case
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating case: {str(e)}"
        )

@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: int,
    case_service: EnhancedCaseService = Depends(get_case_service),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a surgical case.
    
    This endpoint is **idempotent** - multiple delete requests for the same
    case will have the same effect (the case will be deleted or already gone).
    
    **Warning:**
    This operation permanently removes the case and cannot be undone.
    Consider updating the case status to "cancelled" instead of deletion
    for audit trail purposes.
    
    **Response:**
    Returns 204 No Content on successful deletion.
    Returns 404 Not Found if the case doesn't exist.
    """
    try:
        deleted = await case_service.delete_case(case_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case with ID {case_id} not found"
            )
        
        # Invalidate related caches
        await invalidate_cache("cases")
        await invalidate_cache("cases", id=case_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting case: {str(e)}"
        )

@router.get("/", response_model=dict)
async def get_case_statistics(
    status: Optional[str] = Query(None, description="Filter by status"),
    procedure_type: Optional[str] = Query(None, description="Filter by procedure type"),
    case_service: EnhancedCaseService = Depends(get_case_service)
):
    """
    Get case statistics and summary information.
    
    This endpoint is **stateless** and **idempotent**.
    Provides aggregate statistics about cases in the system.
    
    **Filters:**
    - status: Filter statistics by case status
    - procedure_type: Filter statistics by procedure type
    
    **Response:**
    Returns statistical summary including:
    - Total case count
    - Cases by status
    - Cases by priority
    - Average risk scores
    - Recent activity metrics
    """
    try:
        # This would implement actual statistics calculation
        # For now, return a placeholder response
        stats = {
            "total_cases": 0,
            "by_status": {
                "planned": 0,
                "in_progress": 0,
                "completed": 0,
                "cancelled": 0
            },
            "by_priority": {
                "low": 0,
                "medium": 0,
                "high": 0,
                "urgent": 0
            },
            "average_risk_score": 0.0,
            "last_updated": "2024-01-01T00:00:00Z"
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/cases", response_model=CaseResponse)
async def create_case(request: CaseCreateRequest):
    """Create a new case"""
    try:
        case = case_service.create_case(request)
        return CaseResponse(**case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/cases/{case_id}", response_model=CaseResponse)
async def update_case(case_id: int, request: CaseCreateRequest):
    """Update an existing case"""
    try:
        case = case_service.update_case(case_id, request)
        return CaseResponse(**case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/cases/{case_id}")
async def delete_case(case_id: int):
    """Delete a case"""
    try:
        case_service.delete_case(case_id)
        return {"detail": f"Case {case_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cases/{case_id}/decision-support")
async def get_decision_support(case_id: int):
    """Get decision support for a case"""
    try:
        # Get case details first
        case_data = case_service.get_case(case_id)
        
        # Generate decision support based on case
        recommendations = generate_recommendations(case_data["procedure_type"], case_data["diagnosis"])
        
        return {
            "case_id": case_id,
            "recommendations": recommendations,
            "risk_assessment": {
                "overall_risk": case_data["risk_score"],
                "risk_factors": get_risk_factors(case_data["diagnosis"]),
                "mitigation_strategies": get_mitigation_strategies(case_data["procedure_type"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating decision support: {str(e)}")

def generate_recommendations(procedure_type: str, diagnosis: str) -> List[str]:
    """Generate recommendations based on procedure and diagnosis"""
    recommendations = []
    
    if "cancer" in diagnosis.lower():
        recommendations.extend([
            "Consider multidisciplinary team consultation",
            "Evaluate for neoadjuvant therapy",
            "Assess nutritional status pre-operatively"
        ])
    
    if procedure_type == "laparoscopic":
        recommendations.extend([
            "Ensure CO2 insufflation equipment is ready",
            "Prepare for potential conversion to open",
            "Monitor for trocar site complications"
        ])
    elif procedure_type == "gastric_resection":
        recommendations.extend([
            "Plan for intraoperative frozen section",
            "Ensure adequate margins",
            "Prepare for gastric reconstruction"
        ])
    
    return recommendations

def get_risk_factors(diagnosis: str) -> List[str]:
    """Get risk factors based on diagnosis"""
    risk_factors = ["Patient age", "Comorbidities", "Previous surgeries"]
    
    if "cancer" in diagnosis.lower():
        risk_factors.extend(["Tumor stage", "Metastatic potential", "Nutritional status"])
    
    return risk_factors

def get_mitigation_strategies(procedure_type: str) -> List[str]:
    """Get mitigation strategies based on procedure type"""
    strategies = ["Standard monitoring", "Prophylactic antibiotics", "DVT prevention"]
    
    if procedure_type == "laparoscopic":
        strategies.extend(["Monitor for CO2 embolism", "Careful trocar placement"])
    elif procedure_type == "gastric_resection":
        strategies.extend(["Anastomotic leak prevention", "Nutritional support planning"])
    
    return strategies

# Note: These endpoints use the case service for demonstration
# The main endpoints (/, /{case_id}) above use direct database queries
# and are enhanced with optional research capabilities
