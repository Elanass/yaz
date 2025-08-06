"""
Enhanced Deliverables API - Advanced CSV-to-Insights Pipeline
Handles document generation, reporting, and deliverable management with professional templates
"""

import asyncio
import io
import uuid
from datetime import datetime
from typing import BinaryIO, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...core.analytics.insight_generator import InsightGenerator
from ...core.cache import cache_detail_endpoint, cache_list_endpoint, invalidate_cache
from ...core.database import get_db
from ...core.deliverable_factory import DeliverableFactory
from ...core.models.processing_models import (
    AudienceType,
    Deliverable,
    DeliverableFormat,
    DeliverableMetadata,
    DeliverableRequest,
)
from ...core.models.user import User
from ...core.services.auth_service import get_current_user

# Legacy imports for backward compatibility
from ...core.services.deliverable_service import (
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

# In-memory storage for processing results (replace with database in production)
processing_results_store = {}
deliverables_store = {}


class AdvancedDeliverableRequest(BaseModel):
    """Enhanced request for advanced deliverable generation"""

    processing_result_id: str
    audience: AudienceType
    format: DeliverableFormat
    title: Optional[str] = None
    customization: dict = {}
    include_raw_data: bool = False
    enable_interactivity: bool = False

    class Config:
        use_enum_values = True


class DeliverableGenerationResponse(BaseModel):
    """Response for deliverable generation"""

    success: bool
    deliverable_id: str
    message: str
    download_url: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    status: str = "generating"


@router.post("/generate-advanced", response_model=DeliverableGenerationResponse)
async def generate_advanced_deliverable(
    request: AdvancedDeliverableRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate advanced deliverable from processed CSV data with professional templates

    This endpoint creates publication-ready reports with:
    - Audience-specific content and formatting
    - Professional templates and styling
    - Interactive visualizations (for web formats)
    - Domain-specific insights and recommendations
    """
    try:
        # Check if processing result exists
        if request.processing_result_id not in processing_results_store:
            raise HTTPException(
                status_code=404,
                detail=f"Processing result {request.processing_result_id} not found",
            )

        processing_result = processing_results_store[request.processing_result_id]

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
            logger.warning(f"Failed to generate insights: {str(e)}")

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
            status_code=500, detail=f"Failed to generate deliverable: {str(e)}"
        )


@router.get("/download/{deliverable_id}")
async def download_deliverable(deliverable_id: str, db: Session = Depends(get_db)):
    """
    Download a generated deliverable
    """
    try:
        if deliverable_id not in deliverables_store:
            raise HTTPException(
                status_code=404, detail="Deliverable not found or not ready"
            )

        deliverable = deliverables_store[deliverable_id]

        if deliverable.format == DeliverableFormat.PDF and deliverable.content:
            return StreamingResponse(
                io.BytesIO(deliverable.content),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={deliverable.metadata.title}.pdf"
                },
            )

        elif (
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

        elif deliverable.format == DeliverableFormat.API and deliverable.api_response:
            return JSONResponse(deliverable.api_response)

        elif (
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

        else:
            raise HTTPException(
                status_code=404, detail="Deliverable content not available"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to download deliverable: {str(e)}"
        )


@router.get("/status/{deliverable_id}")
async def get_deliverable_status(deliverable_id: str, db: Session = Depends(get_db)):
    """
    Get the status of a deliverable generation
    """
    try:
        if deliverable_id in deliverables_store:
            deliverable = deliverables_store[deliverable_id]
            return {
                "deliverable_id": deliverable_id,
                "status": "completed",
                "title": deliverable.metadata.title,
                "format": deliverable.metadata.format.value,
                "audience": deliverable.metadata.audience.value,
                "generated_at": deliverable.metadata.generated_at.isoformat(),
                "file_size_bytes": deliverable.metadata.file_size_bytes,
                "download_url": f"/api/v1/deliverables/download/{deliverable_id}",
            }
        else:
            return {
                "deliverable_id": deliverable_id,
                "status": "generating",
                "message": "Deliverable is being generated",
            }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get deliverable status: {str(e)}"
        )


@router.get("/list-advanced")
async def list_advanced_deliverables(
    audience: Optional[AudienceType] = None,
    format: Optional[DeliverableFormat] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List generated advanced deliverables with filtering
    """
    try:
        deliverables = list(deliverables_store.values())

        # Apply filters
        if audience:
            deliverables = [d for d in deliverables if d.metadata.audience == audience]
        if format:
            deliverables = [d for d in deliverables if d.metadata.format == format]

        # Sort by generation date (newest first)
        deliverables.sort(key=lambda x: x.metadata.generated_at, reverse=True)

        # Apply limit
        deliverables = deliverables[:limit]

        return [
            {
                "deliverable_id": did,
                "title": d.metadata.title,
                "audience": d.metadata.audience.value,
                "format": d.metadata.format.value,
                "generated_at": d.metadata.generated_at.isoformat(),
                "file_size_bytes": d.metadata.file_size_bytes,
                "download_url": f"/api/v1/deliverables/download/{did}",
            }
            for did, d in deliverables_store.items()
            if (not audience or d.metadata.audience == audience)
            and (not format or d.metadata.format == format)
        ][:limit]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list deliverables: {str(e)}"
        )


@router.delete("/{deliverable_id}")
async def delete_deliverable(deliverable_id: str, db: Session = Depends(get_db)):
    """
    Delete a generated deliverable
    """
    try:
        if deliverable_id not in deliverables_store:
            raise HTTPException(status_code=404, detail="Deliverable not found")

        del deliverables_store[deliverable_id]

        return {"success": True, "message": "Deliverable deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete deliverable: {str(e)}"
        )


# Background task
async def generate_deliverable_async(
    deliverable_id: str,
    processing_result,
    insights,
    deliverable_request: DeliverableRequest,
    user_id: str,
):
    """
    Background task to generate deliverable
    """
    try:
        # Generate the deliverable
        deliverable = await deliverable_factory.generate_deliverable(
            processing_result, insights, deliverable_request
        )

        # Store the deliverable
        deliverables_store[deliverable_id] = deliverable

        logger.info(
            f"Deliverable {deliverable_id} generated successfully for user {user_id}"
        )

    except Exception as e:
        logger.error(f"Failed to generate deliverable {deliverable_id}: {str(e)}")
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
            html_content=f"<html><body><h1>Error</h1><p>Failed to generate deliverable: {str(e)}</p></body></html>",
            api_response={"error": str(e), "deliverable_id": deliverable_id},
        )
        deliverables_store[deliverable_id] = error_deliverable


# Legacy endpoints for backward compatibility
def get_deliverable_service(db: Session = Depends(get_db)) -> DeliverableService:
    """Dependency to get deliverable service instance"""
    return DeliverableService(db)


@router.post(
    "/", response_model=DeliverableResponse, status_code=status.HTTP_201_CREATED
)
async def create_deliverable(
    request: DeliverableRequest,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new deliverable document or report (legacy endpoint).
    """
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
            detail=f"Error creating deliverable: {str(e)}",
        )


@router.get("/", response_model=List[DeliverableResponse])
@cache_list_endpoint("deliverables", ttl=120)  # Cache for 2 minutes
async def list_deliverables(
    type: Optional[DeliverableType] = Query(
        None, description="Filter by deliverable type"
    ),
    status: Optional[DeliverableStatus] = Query(None, description="Filter by status"),
    case_id: Optional[int] = Query(None, description="Filter by case ID"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
):
    """
    List deliverables with filtering and pagination.

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
        deliverables = await deliverable_service.list_deliverables(
            type=type,
            status=status,
            case_id=case_id,
            created_by=created_by,
            page=page,
            limit=limit,
        )

        return deliverables

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving deliverables: {str(e)}",
        )


@router.get("/{deliverable_id}", response_model=DeliverableResponse)
@cache_detail_endpoint("deliverables", ttl=300)  # Cache for 5 minutes
async def get_deliverable(
    deliverable_id: str,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
):
    """
    Get details of a specific deliverable.

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
            detail=f"Error retrieving deliverable: {str(e)}",
        )


@router.put("/{deliverable_id}", response_model=DeliverableResponse)
async def update_deliverable(
    deliverable_id: str,
    request: DeliverableUpdateRequest,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing deliverable.

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
            detail=f"Error updating deliverable: {str(e)}",
        )


@router.delete("/{deliverable_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deliverable(
    deliverable_id: str,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a deliverable.

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
            detail=f"Error deleting deliverable: {str(e)}",
        )


@router.get("/{deliverable_id}/download")
async def download_deliverable(
    deliverable_id: str,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
):
    """
    Download a deliverable file.

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
            detail=f"Error downloading deliverable: {str(e)}",
        )


# Template Endpoints


@router.get("/templates", response_model=List[TemplateResponse])
@cache_list_endpoint("deliverable_templates", ttl=600)  # Cache for 10 minutes
async def list_templates(
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
):
    """
    List available deliverable templates.

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
        templates = await deliverable_service.list_templates()
        return templates

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving templates: {str(e)}",
        )


@router.get("/templates/{template_id}", response_model=TemplateResponse)
@cache_detail_endpoint("deliverable_templates", ttl=600)  # Cache for 10 minutes
async def get_template(
    template_id: str,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
):
    """
    Get details of a specific deliverable template.

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
            detail=f"Error retrieving template: {str(e)}",
        )


@router.post("/templates/{template_id}/generate", response_model=DeliverableResponse)
async def generate_from_template(
    template_id: str,
    parameters: dict,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a deliverable from a template.

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
            detail=f"Error generating from template: {str(e)}",
        )


# Health Endpoint


@router.get("/health", response_model=dict)
async def get_deliverable_health(
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
):
    """
    Get deliverable service health status.

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
        health_info = await deliverable_service.health_check()
        return health_info

    except Exception as e:
        return {"service": "DeliverableService", "status": "error", "error": str(e)}
