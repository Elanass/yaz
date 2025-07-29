"""
User Models
Healthcare-grade Pydantic models for authentication and authorization
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator, root_validator
from pydantic import ConfigDict, EmailStr


class UserRole(str, Enum):
    """User roles for access control"""
    ADMIN = "admin"
    CLINICIAN = "clinician"
    RESEARCHER = "researcher"
    REVIEWER = "reviewer"
    READONLY = "readonly"


class User(BaseModel):
    """Base user model with common fields"""
    id: UUID = Field(default_factory=uuid4)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str
    role: UserRole = Field(default=UserRole.CLINICIAN)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(str_strip_whitespace=True)


class UserCreate(BaseModel):
    """Model for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str
    role: UserRole = Field(default=UserRole.CLINICIAN)
    
    model_config = ConfigDict(str_strip_whitespace=True)


class UserLogin(BaseModel):
    """Model for user login"""
    username: str
    password: str
    
    model_config = ConfigDict(str_strip_whitespace=True)


class UserResponse(BaseModel):
    """Model for user response (no sensitive data)"""
    id: UUID
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(str_strip_whitespace=True)


class TokenResponse(BaseModel):
    """Model for token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    
    model_config = ConfigDict(str_strip_whitespace=True)


class UserPermission(str, Enum):
    """Permission types for user actions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class ResourceType(str, Enum):
    """Resource types for permission control"""
    PATIENT = "patient"
    CASE = "case"
    DECISION = "decision"
    PROTOCOL = "protocol"
    REPORT = "report"
    USER = "user"
    SYSTEM = "system"


class Permission(BaseModel):
    """Model for permission records"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    resource_type: ResourceType
    resource_id: Optional[UUID] = None  # None means all resources of this type
    permission: UserPermission
    created_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(str_strip_whitespace=True)
