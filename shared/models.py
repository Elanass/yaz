"""
Shared Models
Common data models for all applications
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from pydantic import BaseModel

from .database import Base


# SQLAlchemy Models
class BaseEntity(Base):
    """Base database entity"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


# Pydantic Models
class BaseResponse(BaseModel):
    """Base API response"""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[dict] = None


class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = datetime.utcnow()
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
