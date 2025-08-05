"""
Deliverables API - Surgify Platform
Handles document generation, reporting, and deliverable management
"""

import io
from typing import BinaryIO, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from surgify.core.cache import (
    cache_detail_endpoint,
    cache_list_endpoint,
    invalidate_cache,
)
from surgify.core.database import get_db
from surgify.core.models.user import User
from surgify.core.services.auth_service import get_current_user
from surgify.core.services.deliverable_service import (
    DeliverableFormat,
    DeliverableRequest,
    DeliverableResponse,
    DeliverableService,
    DeliverableStatus,
    DeliverableType,
    DeliverableUpdateRequest,
    TemplateResponse,
)

router = APIRouter(tags=["Deliverables"])


def get_deliverable_service(db: Session = Depends(get_db)) -> DeliverableService:
    """Dependency to get deliverable service instance"""
    return DeliverableService(db)


# Deliverable Endpoints


@router.post(
    "/", response_model=DeliverableResponse, status_code=status.HTTP_201_CREATED
)
async def create_deliverable(
    request: DeliverableRequest,
    deliverable_service: DeliverableService = Depends(get_deliverable_service),
    current_user: User = Depends(get_current_user),
):
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
