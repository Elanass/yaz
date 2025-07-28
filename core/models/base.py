"""
Core Models
Shared data models used across the platform
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseEntity(BaseModel):
    """Base entity with common fields"""
    
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            UUID: lambda uuid: str(uuid)
        }


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    errors: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_response(cls, data: T = None, message: str = "Success", meta: Dict[str, Any] = None):
        return cls(success=True, message=message, data=data, meta=meta)
    
    @classmethod
    def error_response(cls, message: str, errors: List[str] = None, data: T = None):
        return cls(success=False, message=message, errors=errors or [], data=data)


class PaginationParams(BaseModel):
    """Pagination parameters"""
    
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    
    page: int
    size: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(cls, page: int, size: int, total: int):
        pages = (total + size - 1) // size
        return cls(
            page=page,
            size=size,
            total=total,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )


class Domain(str, Enum):
    """System domains for RBAC"""
    
    HEALTHCARE = "healthcare"
    LOGISTICS = "logistics"
    RESEARCH = "research"
    ADMIN = "admin"


class Scope(str, Enum):
    """Permission scopes for RBAC"""
    
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class UserRole(str, Enum):
    """User roles in the system"""
    
    PATIENT = "patient"
    CLINICIAN = "clinician"
    RESEARCHER = "researcher"
    ADMIN = "admin"


class DecisionStatus(str, Enum):
    """Status of decision processing"""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConfidenceLevel(str, Enum):
    """Confidence levels for decisions"""
    
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    
    @classmethod
    def from_score(cls, score: float) -> "ConfidenceLevel":
        """Convert numeric score to confidence level"""
        if score < 0.3:
            return cls.VERY_LOW
        elif score < 0.5:
            return cls.LOW
        elif score < 0.7:
            return cls.MODERATE
        elif score < 0.9:
            return cls.HIGH
        else:
            return cls.VERY_HIGH


class HealthStatus(BaseModel):
    """Application health status"""
    
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    environment: str = "development"
    components: Dict[str, str] = Field(default_factory=dict)
    
    def add_component(self, name: str, status: str):
        """Add component health status"""
        self.components[name] = status
        if status != "healthy":
            self.status = "degraded"


# Clinical domain models
class TumorStage(str, Enum):
    """TNM tumor staging"""
    
    T1A = "T1a"
    T1B = "T1b"
    T2 = "T2"
    T3 = "T3"
    T4A = "T4a"
    T4B = "T4b"
    TX = "Tx"


class NodalStatus(str, Enum):
    """Nodal involvement status"""
    
    N0 = "N0"
    N1 = "N1"
    N2 = "N2"
    N3A = "N3a"
    N3B = "N3b"
    NX = "Nx"


class MetastasisStatus(str, Enum):
    """Metastasis status"""
    
    M0 = "M0"
    M1 = "M1"
    MX = "Mx"


class PatientPerformanceStatus(int, Enum):
    """ECOG Performance Status"""
    
    PS0 = 0  # Fully active
    PS1 = 1  # Restricted in physically strenuous activity
    PS2 = 2  # Ambulatory and capable of self-care
    PS3 = 3  # Capable of limited self-care
    PS4 = 4  # Completely disabled
