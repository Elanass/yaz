"""Enhanced Cases API - Surgify Platform
Modular, high-performance endpoints with caching and proper service separation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status as http_status
from sqlalchemy.orm import Session


# from ...core.cache import cache_response as cache_detail_endpoint, cache_response as cache_list_endpoint, invalidate_cache


# Simplified cache decorators for now
def cache_list_endpoint(resource, ttl=60):
    def decorator(func):
        return func

    return decorator


def cache_detail_endpoint(resource, ttl=300):
    def decorator(func):
        return func

    return decorator


def invalidate_cache(resource, **params) -> None:
    pass


from src.surge.core.database import get_db
from src.surge.core.models.user import User
from src.surge.core.services.auth_service import get_current_user
from src.surge.domain.models import (
    CaseCreate,
    CaseListFilters,
    CaseResponse,
    CaseUpdate,
)
from src.surge.services.case_service import CaseService as EnhancedCaseService


router = APIRouter(tags=["Cases"])


def get_case_service(db: Session = Depends(get_db)) -> EnhancedCaseService:
    """Dependency to get case service instance."""
    return EnhancedCaseService(db)


@router.get("/", response_model=list[CaseResponse])
@cache_list_endpoint("cases", ttl=60)  # Cache for 1 minute
async def list_cases(
    case_status: str | None = Query(None, description="Filter by case status"),
    procedure_type: str | None = Query(None, description="Filter by procedure type"),
    surgeon_id: str | None = Query(None, description="Filter by surgeon ID"),
    priority: str | None = Query(None, description="Filter by priority"),
    patient_id: str | None = Query(None, description="Filter by patient ID"),
    search: str | None = Query(None, description="Search cases"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    case_service: EnhancedCaseService = Depends(get_case_service),
):
    """List all surgical cases with filtering, pagination, and sorting.

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
            status=case_status,
            procedure_type=procedure_type,
            surgeon_id=surgeon_id,
            priority=priority,
            patient_id=patient_id,
            search=search,
        )

        return await case_service.list_cases(
            filters=filters,
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cases: {e!s}",
        )


@router.post("/", response_model=CaseResponse, status_code=http_status.HTTP_201_CREATED)
async def create_case(
    request: CaseCreate,
    case_service: EnhancedCaseService = Depends(get_case_service),
    current_user: User = Depends(get_current_user),
):
    """Create a new surgical case.

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
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating case: {e!s}",
        )


@router.get("/{case_id}", response_model=CaseResponse)
@cache_detail_endpoint("cases", ttl=300)  # Cache for 5 minutes
async def get_case(
    case_id: int, case_service: EnhancedCaseService = Depends(get_case_service)
):
    """Get a specific surgical case by ID.

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
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Case with ID {case_id} not found",
            )

        return case

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving case: {e!s}",
        )


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: int,
    request: CaseUpdate,
    case_service: EnhancedCaseService = Depends(get_case_service),
    current_user: User = Depends(get_current_user),
):
    """Update an existing surgical case.

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
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Case with ID {case_id} not found",
            )

        # Invalidate related caches
        await invalidate_cache("cases")
        await invalidate_cache("cases", id=case_id)

        return case

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating case: {e!s}",
        )


@router.delete("/{case_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: int,
    case_service: EnhancedCaseService = Depends(get_case_service),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a surgical case.

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
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Case with ID {case_id} not found",
            )

        # Invalidate related caches
        await invalidate_cache("cases")
        await invalidate_cache("cases", id=case_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting case: {e!s}",
        )


@router.get("/", response_model=dict)
async def get_case_statistics(
    status: str | None = Query(None, description="Filter by status"),
    procedure_type: str | None = Query(None, description="Filter by procedure type"),
    case_service: EnhancedCaseService = Depends(get_case_service),
):
    """Get case statistics and summary information.

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
        return {
            "total_cases": 0,
            "by_status": {
                "planned": 0,
                "in_progress": 0,
                "completed": 0,
                "cancelled": 0,
            },
            "by_priority": {"low": 0, "medium": 0, "high": 0, "urgent": 0},
            "average_risk_score": 0.0,
            "last_updated": "2024-01-01T00:00:00Z",
        }

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {e!s}",
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/cases", response_model=CaseResponse)
async def create_case(request: CaseCreate):
    """Create a new case."""
    try:
        case = case_service.create_case(request)
        return CaseResponse(**case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/cases/{case_id}", response_model=CaseResponse)
async def update_case(case_id: int, request: CaseUpdate):
    """Update an existing case."""
    try:
        case = case_service.update_case(case_id, request)
        return CaseResponse(**case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/cases/{case_id}")
async def delete_case(case_id: int):
    """Delete a case."""
    try:
        case_service.delete_case(case_id)
        return {"detail": f"Case {case_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cases/{case_id}/decision-support")
async def get_decision_support(case_id: int):
    """Get decision support for a case."""
    try:
        # Get case details first
        case_data = case_service.get_case(case_id)

        # Generate decision support based on case
        recommendations = generate_recommendations(
            case_data["procedure_type"], case_data["diagnosis"]
        )

        return {
            "case_id": case_id,
            "recommendations": recommendations,
            "risk_assessment": {
                "overall_risk": case_data["risk_score"],
                "risk_factors": get_risk_factors(case_data["diagnosis"]),
                "mitigation_strategies": get_mitigation_strategies(
                    case_data["procedure_type"]
                ),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating decision support: {e!s}"
        )


def generate_recommendations(procedure_type: str, diagnosis: str) -> list[str]:
    """Generate recommendations based on procedure and diagnosis."""
    recommendations = []

    if "cancer" in diagnosis.lower():
        recommendations.extend(
            [
                "Consider multidisciplinary team consultation",
                "Evaluate for neoadjuvant therapy",
                "Assess nutritional status pre-operatively",
            ]
        )

    if procedure_type == "laparoscopic":
        recommendations.extend(
            [
                "Ensure CO2 insufflation equipment is ready",
                "Prepare for potential conversion to open",
                "Monitor for trocar site complications",
            ]
        )
    elif procedure_type == "gastric_resection":
        recommendations.extend(
            [
                "Plan for intraoperative frozen section",
                "Ensure adequate margins",
                "Prepare for gastric reconstruction",
            ]
        )

    return recommendations


def get_risk_factors(diagnosis: str) -> list[str]:
    """Get risk factors based on diagnosis."""
    risk_factors = ["Patient age", "Comorbidities", "Previous surgeries"]

    if "cancer" in diagnosis.lower():
        risk_factors.extend(
            ["Tumor stage", "Metastatic potential", "Nutritional status"]
        )

    return risk_factors


def get_mitigation_strategies(procedure_type: str) -> list[str]:
    """Get mitigation strategies based on procedure type."""
    strategies = ["Standard monitoring", "Prophylactic antibiotics", "DVT prevention"]

    if procedure_type == "laparoscopic":
        strategies.extend(["Monitor for CO2 embolism", "Careful trocar placement"])
    elif procedure_type == "gastric_resection":
        strategies.extend(
            ["Anastomotic leak prevention", "Nutritional support planning"]
        )

    return strategies


# HTMX Surgery Platform Endpoints
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Setup templates for HTMX partials
templates_path = Path(__file__).parent.parent.parent / "ui" / "web" / "templates"
templates = Jinja2Templates(directory=str(templates_path)) if templates_path.exists() else None

# Import from your existing surge structure
try:
    from ...services.case_service import CaseService as EnhancedCaseService
    from ...models.users import User
except ImportError:
    # Fallback if structure is different
    EnhancedCaseService = None
    User = None


@router.get("/cases/list", response_class=HTMLResponse)
async def get_cases_list_partial(
    request: Request,
    search: str = Query("", description="Search term"),
    status: str = Query("", description="Case status filter"),
    procedure: str = Query("", description="Procedure filter"),
    case_service: EnhancedCaseService = Depends(get_case_service),
    current_user: User = Depends(get_current_user),
):
    """HTMX partial for cases list with filters"""
    try:
        # Apply filters
        filters = CaseListFilters(
            search=search if search else None,
            status=status if status else None,
            procedure=procedure if procedure else None,
        )

        cases = await case_service.list_cases(filters=filters, user=current_user)

        if templates:
            return templates.TemplateResponse(
                "partials/cases-list.html",
                {
                    "request": request,
                    "cases": cases.items,
                    "total": cases.total,
                },
            )
        else:
            return HTMLResponse(
                f"""
                <div id="cases-list">
                    <div class="space-y-4">
                        {"".join(
                            [
                                f"""
                        <div class="card p-4">
                            <div class="flex justify-between items-start">
                                <div>
                                    <h3 class="font-semibold">{case.procedure}</h3>
                                    <p class="text-sm text-gray-600">Patient: {case.patient_name}</p>
                                    <p class="text-sm text-gray-600">Surgeon: {case.surgeon}</p>
                                </div>
                                <span class="px-2 py-1 text-xs rounded bg-{case.status == "completed" and "green" or case.status == "scheduled" and "blue" or "yellow"}-100">
                                    {case.status.replace("_", " ").title()}
                                </span>
                            </div>
                        </div>
                        """
                                for case in cases.items
                            ]
                        )}
                    </div>
                </div>
            """
            )
    except Exception as e:
        return HTMLResponse(f'<div class="error">Error loading cases: {str(e)}</div>')


@router.get("/cases/new-form", response_class=HTMLResponse)
async def get_new_case_form(
    request: Request, current_user: User = Depends(get_current_user)
):
    """HTMX partial for new case form"""
    if templates:
        return templates.TemplateResponse(
            "partials/case-form.html",
            {
                "request": request,
                "case": None,
                "title": "New Case",
            },
        )
    else:
        return HTMLResponse(
            """
            <div id="case-form-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white rounded-lg p-6 w-full max-w-2xl">
                    <h3 class="text-lg font-semibold mb-4">New Surgical Case</h3>
                    <form hx-post="/api/v1/cases" hx-target="#cases-list" hx-swap="outerHTML">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium mb-1">Patient Name</label>
                                <input type="text" name="patient_name" class="w-full border rounded px-3 py-2" required>
                            </div>
                            <div>
                                <label class="block text-sm font-medium mb-1">Procedure</label>
                                <select name="procedure" class="w-full border rounded px-3 py-2" required>
                                    <option value="">Select Procedure</option>
                                    <option value="laparoscopic_cholecystectomy">Laparoscopic Cholecystectomy</option>
                                    <option value="appendectomy">Appendectomy</option>
                                    <option value="hernia_repair">Hernia Repair</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium mb-1">Surgeon</label>
                                <input type="text" name="surgeon" class="w-full border rounded px-3 py-2" required>
                            </div>
                            <div>
                                <label class="block text-sm font-medium mb-1">Scheduled Date</label>
                                <input type="datetime-local" name="scheduled_datetime" class="w-full border rounded px-3 py-2" required>
                            </div>
                        </div>
                        <div class="flex justify-end space-x-3 mt-6">
                            <button type="button" onclick="document.getElementById('case-form-modal').remove()" 
                                    class="px-4 py-2 text-gray-600 border rounded hover:bg-gray-50">
                                Cancel
                            </button>
                            <button type="submit" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                                Create Case
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        """
        )


@router.get("/cases/today", response_class=HTMLResponse)
async def get_todays_cases(
    request: Request,
    case_service: EnhancedCaseService = Depends(get_case_service),
    current_user: User = Depends(get_current_user),
):
    """HTMX partial for today's cases"""
    try:
        from datetime import date

        today = date.today()

        # Get cases scheduled for today
        filters = CaseListFilters(date_from=today, date_to=today)

        cases = await case_service.list_cases(filters=filters, user=current_user)

        return HTMLResponse(
            f"""
            <div class="space-y-2">
                {"".join(
                    [
                        f"""
                <div class="flex items-center justify-between p-2 border rounded">
                    <div class="text-sm">
                        <div class="font-medium">{case.procedure}</div>
                        <div class="text-gray-600">{case.patient_name}</div>
                    </div>
                    <span class="text-xs text-gray-500">{case.scheduled_start_time or "TBD"}</span>
                </div>
                """
                        for case in cases.items
                    ]
                ) if cases.items else '<div class="text-sm text-gray-500 text-center py-4">No cases today</div>'}
            </div>
        """
        )
    except Exception as e:
        return HTMLResponse(f'<div class="text-sm text-red-600">Error: {str(e)}</div>')


@router.get("/cases/{case_id}/details", response_class=HTMLResponse)
async def get_case_details_modal(
    case_id: str,
    request: Request,
    case_service: EnhancedCaseService = Depends(get_case_service),
    current_user: User = Depends(get_current_user),
):
    """HTMX partial for case details modal"""
    try:
        case = await case_service.get_case(case_id, user=current_user)

        return HTMLResponse(
            f"""
            <div id="case-details-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white rounded-lg p-6 w-full max-w-4xl">
                    <div class="flex justify-between items-start mb-4">
                        <h3 class="text-lg font-semibold">Case Details: {case.procedure}</h3>
                        <button onclick="document.getElementById('case-details-modal').remove()" 
                                class="text-gray-400 hover:text-gray-600">✕</button>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-6">
                        <div>
                            <h4 class="font-semibold mb-2">Patient Information</h4>
                            <div class="space-y-1 text-sm">
                                <div><span class="text-gray-600">Name:</span> {case.patient_name}</div>
                                <div><span class="text-gray-600">MRN:</span> {case.patient_mrn or "N/A"}</div>
                                <div><span class="text-gray-600">DOB:</span> {case.patient_dob or "N/A"}</div>
                            </div>
                        </div>
                        
                        <div>
                            <h4 class="font-semibold mb-2">Case Information</h4>
                            <div class="space-y-1 text-sm">
                                <div><span class="text-gray-600">Procedure:</span> {case.procedure}</div>
                                <div><span class="text-gray-600">Surgeon:</span> {case.surgeon}</div>
                                <div><span class="text-gray-600">Status:</span> 
                                    <span class="px-2 py-1 text-xs rounded bg-blue-100">{case.status}</span>
                                </div>
                                <div><span class="text-gray-600">Scheduled:</span> {case.scheduled_start_time or "TBD"}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-6 flex justify-end">
                        <button onclick="document.getElementById('case-details-modal').remove()" 
                                class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600">
                            Close
                        </button>
                    </div>
                </div>
            </div>
        """
        )
    except Exception as e:
        return HTMLResponse(f'<div class="error">Error loading case details: {str(e)}</div>')


# Note: These endpoints use the case service for demonstration
# The main endpoints (/, /{case_id}) above use direct database queries
# and are enhanced with optional research capabilities
