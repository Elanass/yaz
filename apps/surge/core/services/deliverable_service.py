"""Deliverable Service for Surge Platform
Handles document generation, reporting, and deliverable management.
"""

import io
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, BinaryIO
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.surge.core.database import get_db
from surge.core.cache import invalidate_cache

from .base import BaseService


logger = logging.getLogger(__name__)


class DeliverableType(str, Enum):
    """Deliverable type enumeration."""

    CASE_REPORT = "case_report"
    SURGICAL_PLAN = "surgical_plan"
    RISK_ASSESSMENT = "risk_assessment"
    POST_OP_SUMMARY = "post_op_summary"
    ANALYTICS_REPORT = "analytics_report"
    COMPLIANCE_DOCUMENT = "compliance_document"
    RESEARCH_DATA = "research_data"


class DeliverableStatus(str, Enum):
    """Deliverable status enumeration."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DeliverableFormat(str, Enum):
    """Deliverable format enumeration."""

    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"
    XML = "xml"


class DeliverableRequest(BaseModel):
    """Request model for creating deliverables."""

    type: DeliverableType
    title: str
    description: str | None = None
    case_id: int | None = None
    format: DeliverableFormat = DeliverableFormat.PDF
    template_id: str | None = None
    parameters: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    auto_generate: bool = True


class DeliverableUpdateRequest(BaseModel):
    """Request model for updating deliverables."""

    title: str | None = None
    description: str | None = None
    status: DeliverableStatus | None = None
    content: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class DeliverableResponse(BaseModel):
    """Response model for deliverable data."""

    id: str
    type: DeliverableType
    title: str
    description: str | None
    case_id: int | None
    format: DeliverableFormat
    status: DeliverableStatus
    file_path: str | None
    file_size: int | None
    download_url: str | None
    created_at: datetime
    updated_at: datetime
    created_by: str | None
    reviewed_by: str | None
    approved_at: datetime | None
    published_at: datetime | None
    expires_at: datetime | None
    metadata: dict[str, Any] | None = None


class TemplateResponse(BaseModel):
    """Response model for deliverable templates."""

    id: str
    name: str
    type: DeliverableType
    format: DeliverableFormat
    description: str | None
    parameters: list[str]
    created_at: datetime
    is_active: bool


class DeliverableService(BaseService):
    """Service for handling deliverable generation and management."""

    def __init__(self, db: Session = None) -> None:
        super().__init__()
        self.db = db
        self._deliverables = {}  # In-memory store for deliverables
        self._templates = {}  # In-memory store for templates
        self._next_id = 1

        # Initialize default templates
        self._initialize_default_templates()

    def _get_db(self) -> Session:
        """Get database session."""
        if self.db:
            return self.db
        return next(get_db())

    def _initialize_default_templates(self) -> None:
        """Initialize default deliverable templates."""
        templates = [
            {
                "id": "case_report_standard",
                "name": "Standard Case Report",
                "type": DeliverableType.CASE_REPORT,
                "format": DeliverableFormat.PDF,
                "description": "Standard surgical case report template",
                "parameters": ["case_id", "include_images", "include_notes"],
                "created_at": datetime.utcnow(),
                "is_active": True,
            },
            {
                "id": "surgical_plan_basic",
                "name": "Basic Surgical Plan",
                "type": DeliverableType.SURGICAL_PLAN,
                "format": DeliverableFormat.PDF,
                "description": "Basic surgical planning document",
                "parameters": ["case_id", "procedure_steps", "risk_factors"],
                "created_at": datetime.utcnow(),
                "is_active": True,
            },
            {
                "id": "risk_assessment_comprehensive",
                "name": "Comprehensive Risk Assessment",
                "type": DeliverableType.RISK_ASSESSMENT,
                "format": DeliverableFormat.PDF,
                "description": "Detailed patient risk assessment",
                "parameters": ["case_id", "assessment_date", "risk_categories"],
                "created_at": datetime.utcnow(),
                "is_active": True,
            },
        ]

        for template_data in templates:
            self._templates[template_data["id"]] = TemplateResponse(**template_data)

    async def create_deliverable(
        self, request: DeliverableRequest, user_id: str | None = None
    ) -> DeliverableResponse:
        """Create a new deliverable."""
        try:
            deliverable_id = str(uuid4())

            # Generate download URL
            download_url = f"/api/v1/deliverables/{deliverable_id}/download"

            deliverable = DeliverableResponse(
                id=deliverable_id,
                type=request.type,
                title=request.title,
                description=request.description,
                case_id=request.case_id,
                format=request.format,
                status=DeliverableStatus.DRAFT,
                file_path=None,
                file_size=None,
                download_url=download_url,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                created_by=user_id,
                metadata=request.metadata or {},
            )

            self._deliverables[deliverable_id] = deliverable

            # Auto-generate if requested
            if request.auto_generate:
                await self._generate_deliverable_content(
                    deliverable_id, request.parameters or {}
                )

            # Invalidate cache
            await invalidate_cache("deliverables")

            logger.info(f"Created deliverable {deliverable_id} of type {request.type}")
            return deliverable

        except Exception as e:
            logger.exception(f"Error creating deliverable: {e}")
            raise

    async def list_deliverables(
        self,
        type: DeliverableType | None = None,
        status: DeliverableStatus | None = None,
        case_id: int | None = None,
        created_by: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> list[DeliverableResponse]:
        """List deliverables with filtering and pagination."""
        try:
            deliverables = list(self._deliverables.values())

            # Apply filters
            if type:
                deliverables = [d for d in deliverables if d.type == type]
            if status:
                deliverables = [d for d in deliverables if d.status == status]
            if case_id:
                deliverables = [d for d in deliverables if d.case_id == case_id]
            if created_by:
                deliverables = [d for d in deliverables if d.created_by == created_by]

            # Filter out expired deliverables
            now = datetime.utcnow()
            deliverables = [
                d for d in deliverables if not d.expires_at or d.expires_at > now
            ]

            # Sort by created_at descending
            deliverables.sort(key=lambda x: x.created_at, reverse=True)

            # Apply pagination
            start = (page - 1) * limit
            end = start + limit

            return deliverables[start:end]

        except Exception as e:
            logger.exception(f"Error listing deliverables: {e}")
            raise

    async def get_deliverable(self, deliverable_id: str) -> DeliverableResponse | None:
        """Get a specific deliverable."""
        try:
            deliverable = self._deliverables.get(deliverable_id)
            if (
                deliverable
                and deliverable.expires_at
                and deliverable.expires_at <= datetime.utcnow()
            ):
                return None  # Deliverable expired
            return deliverable
        except Exception as e:
            logger.exception(f"Error getting deliverable {deliverable_id}: {e}")
            raise

    async def update_deliverable(
        self,
        deliverable_id: str,
        request: DeliverableUpdateRequest,
        user_id: str | None = None,
    ) -> DeliverableResponse | None:
        """Update a deliverable."""
        try:
            deliverable = self._deliverables.get(deliverable_id)
            if not deliverable:
                return None

            # Update fields
            update_data = request.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(deliverable, field, value)

            deliverable.updated_at = datetime.utcnow()

            # If status changed to approved, set approval timestamp
            if request.status == DeliverableStatus.APPROVED:
                deliverable.approved_at = datetime.utcnow()
                deliverable.reviewed_by = user_id
            elif request.status == DeliverableStatus.PUBLISHED:
                deliverable.published_at = datetime.utcnow()

            # Invalidate cache
            await invalidate_cache("deliverables")
            await invalidate_cache("deliverables", id=deliverable_id)

            logger.info(f"Updated deliverable {deliverable_id}")
            return deliverable

        except Exception as e:
            logger.exception(f"Error updating deliverable {deliverable_id}: {e}")
            raise

    async def delete_deliverable(self, deliverable_id: str) -> bool:
        """Delete a deliverable."""
        try:
            if deliverable_id in self._deliverables:
                del self._deliverables[deliverable_id]

                # Invalidate cache
                await invalidate_cache("deliverables")
                await invalidate_cache("deliverables", id=deliverable_id)

                logger.info(f"Deleted deliverable {deliverable_id}")
                return True

            return False

        except Exception as e:
            logger.exception(f"Error deleting deliverable {deliverable_id}: {e}")
            raise

    async def download_deliverable(self, deliverable_id: str) -> BinaryIO | None:
        """Download deliverable content."""
        try:
            deliverable = await self.get_deliverable(deliverable_id)
            if not deliverable:
                return None

            # Generate content based on deliverable type and format
            content = await self._generate_deliverable_file(deliverable)

            # Create file-like object
            file_obj = io.BytesIO(
                content.encode("utf-8") if isinstance(content, str) else content
            )
            file_obj.seek(0)

            return file_obj

        except Exception as e:
            logger.exception(f"Error downloading deliverable {deliverable_id}: {e}")
            raise

    async def list_templates(self) -> list[TemplateResponse]:
        """List available deliverable templates."""
        try:
            return [
                template for template in self._templates.values() if template.is_active
            ]
        except Exception as e:
            logger.exception(f"Error listing templates: {e}")
            raise

    async def get_template(self, template_id: str) -> TemplateResponse | None:
        """Get a specific template."""
        try:
            return self._templates.get(template_id)
        except Exception as e:
            logger.exception(f"Error getting template {template_id}: {e}")
            raise

    async def generate_from_template(
        self,
        template_id: str,
        parameters: dict[str, Any],
        user_id: str | None = None,
    ) -> DeliverableResponse | None:
        """Generate deliverable from template."""
        try:
            template = await self.get_template(template_id)
            if not template:
                return None

            # Create deliverable request from template
            request = DeliverableRequest(
                type=template.type,
                title=f"{template.name} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                description=f"Generated from template: {template.name}",
                format=template.format,
                template_id=template_id,
                parameters=parameters,
                auto_generate=True,
            )

            return await self.create_deliverable(request, user_id)

        except Exception as e:
            logger.exception(f"Error generating from template {template_id}: {e}")
            raise

    async def _generate_deliverable_content(
        self, deliverable_id: str, parameters: dict[str, Any]
    ) -> None:
        """Generate content for a deliverable."""
        try:
            deliverable = self._deliverables.get(deliverable_id)
            if not deliverable:
                return

            # Simulate content generation (placeholder implementation)
            content = await self._create_content_based_on_type(
                deliverable.type, parameters
            )

            # Update deliverable with generated content
            deliverable.file_size = len(str(content))
            deliverable.status = DeliverableStatus.PENDING_REVIEW
            deliverable.updated_at = datetime.utcnow()

            logger.info(f"Generated content for deliverable {deliverable_id}")

        except Exception as e:
            logger.exception(
                f"Error generating content for deliverable {deliverable_id}: {e}"
            )

    async def _create_content_based_on_type(
        self, deliverable_type: DeliverableType, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Create content based on deliverable type."""
        base_content = {
            "generated_at": datetime.utcnow().isoformat(),
            "parameters": parameters,
            "type": deliverable_type,
        }

        if deliverable_type == DeliverableType.CASE_REPORT:
            base_content.update(
                {
                    "title": "Surgical Case Report",
                    "sections": [
                        "Patient Information",
                        "Procedure Details",
                        "Operative Notes",
                        "Post-operative Care",
                        "Outcomes",
                    ],
                    "case_id": parameters.get("case_id"),
                    "procedure_summary": "Surgical procedure completed successfully",
                }
            )
        elif deliverable_type == DeliverableType.RISK_ASSESSMENT:
            base_content.update(
                {
                    "title": "Patient Risk Assessment",
                    "risk_score": 0.3,
                    "risk_factors": [
                        "Age: Moderate risk",
                        "Procedure complexity: Low risk",
                        "Medical history: Low risk",
                    ],
                    "recommendations": [
                        "Standard pre-operative assessment",
                        "Monitor vital signs during procedure",
                    ],
                }
            )
        elif deliverable_type == DeliverableType.SURGICAL_PLAN:
            base_content.update(
                {
                    "title": "Surgical Plan",
                    "procedure_steps": [
                        "Pre-operative preparation",
                        "Anesthesia administration",
                        "Surgical approach",
                        "Procedure execution",
                        "Closure and recovery",
                    ],
                    "estimated_duration": "2-3 hours",
                    "team_requirements": [
                        "Surgeon",
                        "Anesthesiologist",
                        "Surgical nurse",
                    ],
                }
            )

        return base_content

    async def _generate_deliverable_file(
        self, deliverable: DeliverableResponse
    ) -> str | bytes:
        """Generate file content for deliverable."""
        # This would integrate with actual document generation libraries
        content = await self._create_content_based_on_type(
            deliverable.type, deliverable.metadata or {}
        )

        if deliverable.format == DeliverableFormat.JSON:
            return json.dumps(content, indent=2)
        if deliverable.format == DeliverableFormat.HTML:
            return f"""
            <html>
            <head><title>{deliverable.title}</title></head>
            <body>
                <h1>{deliverable.title}</h1>
                <pre>{json.dumps(content, indent=2)}</pre>
            </body>
            </html>
            """
        if deliverable.format == DeliverableFormat.CSV:
            # Simplified CSV generation
            return "key,value\n" + "\n".join([f"{k},{v}" for k, v in content.items()])
        # Default to plain text representation
        return f"{deliverable.title}\n\n{json.dumps(content, indent=2)}"

    async def cleanup_expired_deliverables(self) -> None:
        """Clean up expired deliverables."""
        try:
            now = datetime.utcnow()
            expired_ids = [
                d_id
                for d_id, d in self._deliverables.items()
                if d.expires_at and d.expires_at <= now
            ]

            for d_id in expired_ids:
                del self._deliverables[d_id]

            if expired_ids:
                await invalidate_cache("deliverables")
                logger.info(f"Cleaned up {len(expired_ids)} expired deliverables")

        except Exception as e:
            logger.exception(f"Error cleaning up expired deliverables: {e}")

    async def health_check(self) -> dict[str, Any]:
        """Check deliverable service health."""
        try:
            total_deliverables = len(self._deliverables)
            pending_review = len(
                [
                    d
                    for d in self._deliverables.values()
                    if d.status == DeliverableStatus.PENDING_REVIEW
                ]
            )
            published = len(
                [
                    d
                    for d in self._deliverables.values()
                    if d.status == DeliverableStatus.PUBLISHED
                ]
            )

            return {
                "service": "DeliverableService",
                "status": "healthy",
                "total_deliverables": total_deliverables,
                "pending_review": pending_review,
                "published": published,
                "available_templates": len(self._templates),
            }

        except Exception as e:
            return {"service": "DeliverableService", "status": "error", "error": str(e)}
