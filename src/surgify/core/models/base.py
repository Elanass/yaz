"""
Core Models - Streamlined base models for the platform
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseEntity(BaseModel):
    """Base entity with common fields"""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""

    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    errors: Optional[List[str]] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginationMeta(BaseModel):
    """Pagination metadata"""

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class HealthStatus(BaseModel):
    """Application health status"""

    status: str = "healthy"
    version: str = "1.0.0"
    environment: str = "development"
    database_connected: bool = True
    api_available: bool = True


# Generic Application Enums
class ProcessingStatus(str, Enum):
    """Generic processing status for any operation"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConfidenceLevel(str, Enum):
    """Generic confidence level for any analysis"""

    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class UserRole(str, Enum):
    """Generic user roles for any application"""

    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
    VIEWER = "viewer"


class Domain(str, Enum):
    """Application domains/modules"""

    AUTH = "auth"
    ANALYSIS = "analysis"
    DECISIONS = "decisions"
    PROTOCOLS = "protocols"
    EDUCATION = "education"
    HOSPITALITY = "hospitality"


class Scope(str, Enum):
    """Permission scopes"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
