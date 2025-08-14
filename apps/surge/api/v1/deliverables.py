"""Enhanced Deliverables API - Advanced CSV-to-Insights Pipeline
Handles document generation, reporting, and deliverable management with professional templates.
"""

import io
import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from apps.surge.core.analytics.insight_generator import InsightGenerator


# from ...core.cache import cache_detail_endpoint, cache_list_endpoint, invalidate_cache


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


from apps.surge.api.dependencies import get_async_session
from apps.surge.core.database import get_db
from apps.surge.core.deliverable_factory import DeliverableFactory
from apps.surge.core.models.processing_models import (
    AudienceType,
    Deliverable,
    DeliverableFormat,
    DeliverableMetadata,
    DeliverableRequest,
)
from apps.surge.core.models.user import User
from apps.surge.core.services.auth_service import get_current_user
from apps.surge.core.services.logger import get_logger
from apps.surge.core.state.store import store
from apps.surge.models.orm import DeliverableORM


logger = get_logger(__name__)

# Legacy imports for backward compatibility
from apps.surge.core.services.deliverable_service import (
    DeliverableResponse,
    DeliverableService,
    DeliverableStatus,
    DeliverableType,
    DeliverableUpdateRequest,
    TemplateResponse,
)


router = APIRouter(tags=["Deliverables"])

# Initialize our advanced components
deliverable_factory = DeliverableFactory()
insight_generator = InsightGenerator()

# Remove module-level dicts in favor of centralized store
# processing_results_store = {}
# deliverables_store = {}


class AdvancedDeliverableRequest(BaseModel):
    """Enhanced request for advanced deliverable generation."""

    processing_result_id: str
    audience: AudienceType
    format: DeliverableFormat
    title: str | None = None
    customization: dict = {}
    include_raw_data: bool = False
    enable_interactivity: bool = False

    class Config:
        use_enum_values = True


class DeliverableGenerationResponse(BaseModel):
    """Response for deliverable generation."""

    success: bool
    deliverable_id: str
    message: str
    download_url: str | None = None
    estimated_completion: datetime | None = None
    status: str = "generating"


@router.post("/generate-advanced", response_model=DeliverableGenerationResponse)
async def generate_advanced_deliverable(
    request: AdvancedDeliverableRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate advanced deliverable from processed CSV data with professional templates.

    This endpoint creates publication-ready reports with:
    - Audience-specific content and formatting
    - Professional templates and styling
    - Interactive visualizations (for web formats)
    - Domain-specific insights and recommendations
    """
    try:
        # Check if processing result exists
        if not store.has_processing_result(request.processing_result_id):
            raise HTTPException(
                status_code=404,
                detail=f"Processing result {request.processing_result_id} not found",
            )

        processing_result = store.get_processing_result(request.processing_result_id)

        # Generate deliverable ID
        deliverable_id = str(uuid.uuid4())

        # Create deliverable request
        deliverable_request = DeliverableRequest(
            processing_result_id=request.processing_result_id,
            audience=request.audience,
            format=request.format,
            customization=request.customization,
            include_raw_data=request.include_raw_data,
        )

        # Generate insights if not already available
        insights = None
        try:
            insights = await insight_generator.generate_comprehensive_insights(
                processing_result
            )
        except Exception as e:
            logger.warning(f"Failed to generate insights: {e!s}")

        # Generate deliverable in background
        background_tasks.add_task(
            generate_deliverable_async,
            deliverable_id,
            processing_result,
            insights,
            deliverable_request,
            current_user.username if hasattr(current_user, "username") else "anonymous",
        )

        # Create download URL
        download_url = f"/api/v1/deliverables/download/{deliverable_id}"

        return DeliverableGenerationResponse(
            success=True,
            deliverable_id=deliverable_id,
            message=f"Generating {request.format.value} report for {request.audience.value} audience",
            download_url=download_url,
            estimated_completion=datetime.utcnow(),
            status="generating",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate deliverable: {e!s}"
        )


@router.get("/download/{deliverable_id}")
async def download_deliverable(deliverable_id: str, db: Session = Depends(get_db)):
    """Download a generated deliverable."""
    try:
        deliverable = store.get_deliverable(deliverable_id)
        if not deliverable:
            raise HTTPException(
                status_code=404, detail="Deliverable not found or not ready"
            )

        if deliverable.format == DeliverableFormat.PDF and deliverable.content:
            return StreamingResponse(
                io.BytesIO(deliverable.content),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={deliverable.metadata.title}.pdf"
                },
            )

        if (
            deliverable.format == DeliverableFormat.INTERACTIVE
            and deliverable.html_content
        ):
            return StreamingResponse(
                io.BytesIO(deliverable.html_content.encode()),
                media_type="text/html",
                headers={
                    "Content-Disposition": f"inline; filename={deliverable.metadata.title}.html"
                },
            )

        if deliverable.format == DeliverableFormat.API and deliverable.api_response:
            return JSONResponse(deliverable.api_response)

        if (
            deliverable.format == DeliverableFormat.PRESENTATION
            and deliverable.html_content
        ):
            return StreamingResponse(
                io.BytesIO(deliverable.html_content.encode()),
                media_type="text/html",
                headers={
                    "Content-Disposition": f"inline; filename={deliverable.metadata.title}_presentation.html"
                },
            )

        raise HTTPException(status_code=404, detail="Deliverable content not available")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to download deliverable: {e!s}"
        )


@router.get("/status/{deliverable_id}")
async def get_deliverable_status(deliverable_id: str, db: Session = Depends(get_db)):
    """Get the status of a deliverable generation."""
    try:
        if store.get_deliverable(deliverable_id):
            d = store.get_deliverable(deliverable_id)
            return {
                "deliverable_id": deliverable_id,
                "status": "completed",
                "title": d.metadata.title,
                "format": d.metadata.format.value,
                "audience": d.metadata.audience.value,
                "generated_at": d.metadata.generated_at.isoformat(),
                "file_size_bytes": d.metadata.file_size_bytes,
                "download_url": f"/api/v1/deliverables/download/{deliverable_id}",
            }
        return {
            "deliverable_id": deliverable_id,
            "status": "generating",
            "message": "Deliverable is being generated",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get deliverable status: {e!s}"
        )


@router.get("/list-advanced")
async def list_advanced_deliverables(
    audience: AudienceType | None = None,
    format: DeliverableFormat | None = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List generated advanced deliverables with filtering."""
    try:
        all_items = store.list_deliverables()
        deliverables = list(all_items.values())

        # Apply filters
        if audience:
            deliverables = [d for d in deliverables if d.metadata.audience == audience]
        if format:
            deliverables = [d for d in deliverables if d.metadata.format == format]

        # Sort by generation date (newest first)
        deliverables.sort(key=lambda x: x.metadata.generated_at, reverse=True)

        # Apply limit
        deliverables = deliverables[:limit]

        result = []
        for did, d in all_items.items():
            if (not audience or d.metadata.audience == audience) and (
                not format or d.metadata.format == format
            ):
                result.append(
                    {
                        "deliverable_id": did,
                        "title": d.metadata.title,
                        "audience": d.metadata.audience.value,
                        "format": d.metadata.format.value,
                        "generated_at": d.metadata.generated_at.isoformat(),
                        "file_size_bytes": d.metadata.file_size_bytes,
                        "download_url": f"/api/v1/deliverables/download/{did}",
                    }
                )
        return result[:limit]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list deliverables: {e!s}"
        )


@router.delete("/{deliverable_id}")
async def delete_deliverable(deliverable_id: str, db: Session = Depends(get_db)):
    """Delete a generated deliverable."""
    try:
        if not store.get_deliverable(deliverable_id):
            raise HTTPException(status_code=404, detail="Deliverable not found")

        store.delete_deliverable(deliverable_id)
        return {"success": True, "message": "Deliverable deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete deliverable: {e!s}"
        )


@router.post("/share/{deliverable_id}")
async def create_share_link(
    deliverable_id: str,
    ttl_minutes: int = 60,
    current_user: User = Depends(get_current_user),
):
    """Create a shareable token for a deliverable with TTL (simple sharing)."""
    if not store.get_deliverable(deliverable_id):
        raise HTTPException(status_code=404, detail="Deliverable not found")
    token = store.create_share_token(deliverable_id, ttl_minutes=ttl_minutes)
    return {
        "share_url": f"/api/v1/deliverables/share/access/{token}",
        "expires_in_minutes": ttl_minutes,
    }


@router.get("/share/access/{token}")
async def access_shared_deliverable(token: str):
    """Access a deliverable via share token without authentication until expiry."""
    deliverable_id = store.resolve_share_token(token)
    if not deliverable_id:
        raise HTTPException(status_code=404, detail="Invalid or expired token")
    # Delegate to download endpoint (could forward or duplicate logic)
    return await download_deliverable(deliverable_id)


# Background task
async def generate_deliverable_async(
    deliverable_id: str,
    processing_result,
    insights,
    deliverable_request: DeliverableRequest,
    user_id: str,
) -> None:
    """Background task to generate deliverable."""
    try:
        # Generate the deliverable
        deliverable = await deliverable_factory.generate_deliverable(
            processing_result, insights, deliverable_request
        )

        # Store the deliverable
        store.save_deliverable(deliverable_id, deliverable)

        logger.info(
            f"Deliverable {deliverable_id} generated successfully for user {user_id}"
        )

    except Exception as e:
        logger.exception(f"Failed to generate deliverable {deliverable_id}: {e!s}")
        # Store error information
        error_deliverable = Deliverable(
            metadata=DeliverableMetadata(
                id=deliverable_id,
                title="Generation Failed",
                audience=deliverable_request.audience,
                format=deliverable_request.format,
                generated_at=datetime.utcnow(),
            ),
            content=None,
            html_content=f"<html><body><h1>Error</h1><p>Failed to generate deliverable: {e!s}</p></body></html>",
            api_response={"error": str(e), "deliverable_id": deliverable_id},
        )
        store.save_deliverable(deliverable_id, error_deliverable)


# Legacy endpoints for backward compatibility
def get_deliverable_service(db: Session = Depends(get_db)) -> DeliverableService:
    """Dependency to get deliverable service instance."""
    return DeliverableService(db)


@router.post(
    "/", response_model=DeliverableResponse, status_code=status.HTTP_201_CREATED
)
async def create_deliverable(
    request: DeliverableRequest,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
    current_user: User = Depends(get_current_user),
):
    """Create a new deliverable document or report (legacy endpoint)."""
    """
    Create a new deliverable document or report.

    This endpoint is **stateless** - it doesn't maintain any in-process state.
    Each request creates a new deliverable that can be generated independently.

    **Deliverable Types:**
    - case_report: Surgical case reports
    - surgical_plan: Pre-operative planning documents
    - risk_assessment: Patient risk assessment reports
    - post_op_summary: Post-operative summaries
    - analytics_report: Data analytics and insights
    - compliance_document: Regulatory compliance documents
    - research_data: Research data exports

    **Output Formats:**
    - pdf: Portable Document Format (default)
    - html: Web-friendly HTML format
    - json: Structured JSON data
    - csv: Comma-separated values
    - xlsx: Excel spreadsheet
    - xml: XML format

    **Auto-Generation:**
    When auto_generate is true, the deliverable content will be generated
    immediately using the provided parameters and template.

    **Response:**
    Returns the created deliverable with unique ID, download URL, and metadata.
    """
    try:
        deliverable = await deliverable_service.create_deliverable(
            request, current_user.username
        )

        # Invalidate related caches
        await invalidate_cache("deliverables")

        return deliverable

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating deliverable: {e!s}",
        )


@router.get("/", response_model=list[DeliverableResponse])
@cache_list_endpoint("deliverables", ttl=120)  # Cache for 2 minutes
async def list_deliverables(
    type: DeliverableType
    | None = Query(None, description="Filter by deliverable type"),
    status: DeliverableStatus | None = Query(None, description="Filter by status"),
    case_id: int | None = Query(None, description="Filter by case ID"),
    created_by: str | None = Query(None, description="Filter by creator"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
):
    """List deliverables with filtering and pagination.

    This endpoint is **stateless** and **idempotent** - multiple calls with the same
    parameters will return the same results. Results are cached for performance.

    **Filtering Options:**
    - type: Filter by deliverable type
    - status: Filter by deliverable status (draft, pending_review, approved, published, archived)
    - case_id: Filter deliverables related to specific case
    - created_by: Filter by creator user ID

    **Deliverable Status:**
    - draft: Initial creation state
    - pending_review: Awaiting review and approval
    - approved: Reviewed and approved for publication
    - published: Available for download and distribution
    - archived: No longer active but preserved

    **Automatic Cleanup:**
    Expired deliverables are automatically filtered out from results.

    **Response:**
    Returns paginated list of deliverables sorted by creation time (newest first).
    """
    try:
        return await deliverable_service.list_deliverables(
            type=type,
            status=status,
            case_id=case_id,
            created_by=created_by,
            page=page,
            limit=limit,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving deliverables: {e!s}",
        )


@router.get("/{deliverable_id}", response_model=DeliverableResponse)
@cache_detail_endpoint("deliverables", ttl=300)  # Cache for 5 minutes
async def get_deliverable(
    deliverable_id: str,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
):
    """Get details of a specific deliverable.

    This endpoint is **stateless** and **idempotent** - multiple calls will
    return the same deliverable information.

    **Expiration Handling:**
    Returns 404 if the deliverable has expired based on its expires_at timestamp.

    **Response:**
    Returns complete deliverable details including:
    - Basic information (title, description, type)
    - Status and approval information
    - File details (size, format, download URL)
    - Audit trail (created/updated timestamps)
    - Metadata and parameters used for generation
    """
    try:
        deliverable = await deliverable_service.get_deliverable(deliverable_id)

        if not deliverable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deliverable with ID {deliverable_id} not found or expired",
            )

        return deliverable

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving deliverable: {e!s}",
        )


@router.put("/{deliverable_id}", response_model=DeliverableResponse)
async def update_deliverable(
    deliverable_id: str,
    request: DeliverableUpdateRequest,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
    current_user: User = Depends(get_current_user),
):
    """Update an existing deliverable.

    This endpoint is **idempotent** - multiple calls with the same data will
    result in the same final state.

    **Partial Updates:**
    Only provided fields will be updated. Omitted fields remain unchanged.

    **Updatable Fields:**
    - title: Deliverable title
    - description: Description text
    - status: Current status (draft, pending_review, approved, published, archived)
    - content: Custom content data
    - metadata: Additional metadata

    **Status Transitions:**
    - draft → pending_review: Submit for review
    - pending_review → approved: Approve for publication
    - approved → published: Make available for download
    - Any status → archived: Archive the deliverable

    **Automatic Timestamps:**
    - approved_at: Set when status changes to approved
    - published_at: Set when status changes to published
    - updated_at: Always updated on any change

    **Response:**
    Returns the updated deliverable with refreshed timestamps and metadata.
    """
    try:
        deliverable = await deliverable_service.update_deliverable(
            deliverable_id, request, current_user.username
        )

        if not deliverable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deliverable with ID {deliverable_id} not found",
            )

        # Invalidate related caches
        await invalidate_cache("deliverables")
        await invalidate_cache("deliverables", id=deliverable_id)

        return deliverable

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating deliverable: {e!s}",
        )


@router.delete("/{deliverable_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deliverable(
    deliverable_id: str,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a deliverable.

    This endpoint is **idempotent** - multiple delete requests for the same
    deliverable will have the same effect.

    **Warning:**
    This operation permanently removes the deliverable and its associated
    files. This cannot be undone. Consider archiving instead of deletion
    for audit trail purposes.

    **Response:**
    Returns 204 No Content on successful deletion.
    Returns 404 Not Found if the deliverable doesn't exist.
    """
    try:
        deleted = await deliverable_service.delete_deliverable(deliverable_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deliverable with ID {deliverable_id} not found",
            )

        # Invalidate related caches
        await invalidate_cache("deliverables")
        await invalidate_cache("deliverables", id=deliverable_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting deliverable: {e!s}",
        )


@router.get("/{deliverable_id}/download")
async def download_deliverable(
    deliverable_id: str,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
):
    """Download a deliverable file.

    This endpoint is **stateless** and **idempotent** - multiple download
    requests will return the same file content.

    **Content Generation:**
    If the deliverable doesn't have a pre-generated file, the content
    will be generated on-demand based on the deliverable's configuration.

    **Response:**
    Returns the file as a streaming download with appropriate content-type
    headers based on the deliverable format.

    **File Formats:**
    - PDF: application/pdf
    - HTML: text/html
    - JSON: application/json
    - CSV: text/csv
    - XLSX: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    - XML: application/xml
    """
    try:
        # Get deliverable info first
        deliverable = await deliverable_service.get_deliverable(deliverable_id)

        if not deliverable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deliverable with ID {deliverable_id} not found or expired",
            )

        # Get file content
        file_content = await deliverable_service.download_deliverable(deliverable_id)

        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File content not available for deliverable {deliverable_id}",
            )

        # Determine content type and filename
        content_type_map = {
            "pdf": "application/pdf",
            "html": "text/html",
            "json": "application/json",
            "csv": "text/csv",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xml": "application/xml",
        }

        content_type = content_type_map.get(
            deliverable.format.lower(), "application/octet-stream"
        )
        filename = f"{deliverable.title}.{deliverable.format.lower()}"

        return StreamingResponse(
            io.BytesIO(file_content.read()),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading deliverable: {e!s}",
        )


# Template Endpoints


@router.get("/templates", response_model=list[TemplateResponse])
@cache_list_endpoint("deliverable_templates", ttl=600)  # Cache for 10 minutes
async def list_templates(
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
):
    """List available deliverable templates.

    This endpoint is **stateless** and **idempotent** - it returns the current
    list of available templates for deliverable generation.

    **Templates:**
    Templates define the structure and content generation rules for different
    types of deliverables. They include:
    - Content structure and layout
    - Required parameters
    - Output format options
    - Generation rules and logic

    **Response:**
    Returns list of available templates with their metadata and parameter requirements.
    """
    try:
        return await deliverable_service.list_templates()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving templates: {e!s}",
        )


@router.get("/templates/{template_id}", response_model=TemplateResponse)
@cache_detail_endpoint("deliverable_templates", ttl=600)  # Cache for 10 minutes
async def get_template(
    template_id: str,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
):
    """Get details of a specific deliverable template.

    This endpoint is **stateless** and **idempotent** - multiple calls will
    return the same template information.

    **Response:**
    Returns complete template details including:
    - Template metadata (name, description, type)
    - Required parameters list
    - Supported output formats
    - Usage instructions
    """
    try:
        template = await deliverable_service.get_template(template_id)

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with ID {template_id} not found",
            )

        return template

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving template: {e!s}",
        )


@router.post("/templates/{template_id}/generate", response_model=DeliverableResponse)
async def generate_from_template(
    template_id: str,
    parameters: dict,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
    current_user: User = Depends(get_current_user),
):
    """Generate a deliverable from a template.

    This endpoint is **stateless** - it creates a new deliverable using the
    specified template and parameters without maintaining any in-process state.

    **Template Generation:**
    Uses the specified template to generate a new deliverable with the provided
    parameters. The template defines:
    - Content structure and layout
    - Data sources and processing rules
    - Output format and styling

    **Parameters:**
    Parameters should match the requirements defined in the template.
    Common parameters include:
    - case_id: Case identifier for case-related deliverables
    - date_range: Date range for reports
    - include_images: Whether to include images
    - format_options: Output format specific options

    **Response:**
    Returns the generated deliverable ready for download or further processing.
    """
    try:
        deliverable = await deliverable_service.generate_from_template(
            template_id, parameters, current_user.username
        )

        if not deliverable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with ID {template_id} not found",
            )

        # Invalidate related caches
        await invalidate_cache("deliverables")

        return deliverable

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating from template: {e!s}",
        )


# Health Endpoint


@router.get("/health", response_model=dict)
async def get_deliverable_health(
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
):
    """Get deliverable service health status.

    This endpoint is **stateless** and **idempotent** - it provides current
    service health information for monitoring and diagnostics.

    **Response:**
    Returns service health metrics including:
    - Service status
    - Total deliverable count
    - Status distribution
    - Available templates count
    - Performance metrics
    """
    try:
        return await deliverable_service.health_check()

    except Exception as e:
        return {"service": "DeliverableService", "status": "error", "error": str(e)}


@router.post("/create", response_model=dict)
async def create_deliverable_api(
    deliverable: dict, session: AsyncSession = Depends(get_async_session)
):
    """Create a new deliverable and persist to database."""
    db_obj = DeliverableORM(**deliverable)
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return {"id": str(db_obj.id), "message": "Deliverable created"}
