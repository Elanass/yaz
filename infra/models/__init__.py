"""Shared Models for Yaz Platform
Common data models that can be used across all apps.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, validator


class BaseYazModel(BaseModel):
    """Base model for all Yaz platform models."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )

    id: str | None = Field(None, description="Unique identifier")
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default_factory=datetime.utcnow)

    def dict(self, **kwargs) -> dict[str, Any]:
        """Enhanced dict method with better serialization."""
        data = super().dict(**kwargs)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


class StatusEnum(str, Enum):
    """Common status values across the platform."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PriorityEnum(str, Enum):
    """Common priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class UserRole(str, Enum):
    """User roles across the platform."""

    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    TECHNICIAN = "technician"
    PATIENT = "patient"
    VIEWER = "viewer"


class Address(BaseYazModel):
    """Common address model."""

    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State/Province")
    zip_code: str = Field(..., description="ZIP/Postal code")
    country: str = Field(default="US", description="Country code")


class Contact(BaseYazModel):
    """Common contact information model."""

    email: str | None = Field(None, description="Email address")
    phone: str | None = Field(None, description="Phone number")
    address: Address | None = Field(None, description="Physical address")


class User(BaseYazModel):
    """Common user model."""

    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(default=True, description="Whether user is active")
    contact: Contact | None = Field(None, description="Contact information")


class AuditLog(BaseYazModel):
    """Common audit log model."""

    action: str = Field(..., description="Action performed")
    user_id: str = Field(..., description="User who performed the action")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: str = Field(..., description="ID of the resource affected")
    changes: dict[str, Any] | None = Field(None, description="Changes made")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class APIResponse(BaseYazModel):
    """Standard API response format."""

    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Any | None = Field(None, description="Response data")
    errors: list[str] | None = Field(None, description="List of errors if any")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class PaginatedResponse(BaseYazModel):
    """Standard paginated response format."""

    items: list[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there's a next page")
    has_prev: bool = Field(..., description="Whether there's a previous page")
