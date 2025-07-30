"""
Core Models - Streamlined base models for the platform
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class BaseEntity(BaseModel):
    """Base entity with common fields"""
    
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ApiResponse(BaseModel):
    """Standard API response wrapper"""
    
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None
    errors: Optional[List[str]] = None


class HealthStatus(BaseModel):
    """Application health status"""
    
    status: str = "healthy"
    version: str = "1.0.0"
    environment: str = "development"
    database_connected: bool = True
    api_available: bool = True


# Clinical Enums
class DecisionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ConfidenceLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class UserRole(str, Enum):
    PATIENT = "patient"
    CLINICIAN = "clinician"
    RESEARCHER = "researcher"
    ADMIN = "admin"


class TumorStage(str, Enum):
    T1A = "T1a"
    T1B = "T1b"
    T2 = "T2"
    T3 = "T3"
    T4A = "T4a"
    T4B = "T4b"
