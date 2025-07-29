"""
Shared Data Models for Gastric ADCI Platform
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Union

# Enumerations
class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    DOCTOR = "doctor"
    RESEARCHER = "researcher"
    NURSE = "nurse"
    GUEST = "guest"

class GenderType(str, Enum):
    """Gender type enumeration"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class TumorStage(str, Enum):
    """Tumor stage enumeration"""
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"
    NA = "NA"

class TumorLocation(str, Enum):
    """Tumor location enumeration"""
    CARDIA = "cardia"
    FUNDUS = "fundus"
    BODY = "body"
    ANTRUM = "antrum"
    PYLORUS = "pylorus"
    DIFFUSE = "diffuse"
    UNKNOWN = "unknown"

# User Models
class User(BaseModel):
    """User data model"""
    id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="User email")
    full_name: str = Field(..., description="Full name")
    role: UserRole = Field(default=UserRole.GUEST, description="User role")
    is_active: bool = Field(default=True, description="Is user active")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")

class UserCreate(BaseModel):
    """User creation model"""
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")
    full_name: str = Field(..., description="Full name")
    role: UserRole = Field(default=UserRole.GUEST, description="User role")

class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = Field(None, description="User email")
    full_name: Optional[str] = Field(None, description="Full name")
    role: Optional[UserRole] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="Is user active")

class Token(BaseModel):
    """Token model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    user: User = Field(..., description="User data")

# Patient Models
class Patient(BaseModel):
    """Patient data model"""
    id: str = Field(..., description="Unique patient identifier")
    age: int = Field(..., description="Patient age")
    gender: GenderType = Field(..., description="Patient gender")
    comorbidities: List[str] = Field(default=[], description="List of comorbidities")
    tumor_stage: TumorStage = Field(..., description="Tumor stage")
    tumor_location: TumorLocation = Field(..., description="Tumor location")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

class Transition(BaseModel):
    """Markov transition model"""
    from_state: str = Field(..., description="Starting state")
    to_state: str = Field(..., description="Ending state")
    probability: float = Field(..., description="Transition probability")
    confidence_interval: Optional[List[float]] = Field(None, description="Confidence interval [lower, upper]")

class Insight(BaseModel):
    """Insight data model"""
    id: str = Field(..., description="Unique insight identifier")
    domain: str = Field(..., description="Insight domain")
    data: Dict[str, Any] = Field(..., description="Insight data")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    source: Optional[str] = Field(None, description="Data source")
    confidence: Optional[float] = Field(None, description="Confidence score (0-1)")

class ReportParams(BaseModel):
    """Report generation parameters"""
    patient_id: str = Field(..., description="Patient ID")
    report_type: str = Field(..., description="Report type")
    include_charts: bool = Field(default=True, description="Include charts")
    date_range: Optional[List[datetime]] = Field(None, description="Date range [start, end]")
    sections: Optional[List[str]] = Field(None, description="Sections to include")

# Case Models
class Case(BaseModel):
    """Case data model"""
    id: str = Field(..., description="Unique case identifier")
    title: str = Field(..., description="Case title")
    patient_id: Optional[str] = Field(None, description="Patient ID")
    created_by: str = Field(..., description="Creator user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    specialty: str = Field(..., description="Surgical specialty")
    procedure: str = Field(..., description="Procedure details")
    location: str = Field(..., description="Location")
    adci_score: Optional[float] = Field(None, description="ADCI score (0-100)")
    status: str = Field(default="active", description="Case status")

class CaseCreate(BaseModel):
    """Case creation model"""
    title: str = Field(..., description="Case title")
    patient_id: Optional[str] = Field(None, description="Patient ID")
    specialty: str = Field(..., description="Surgical specialty")
    procedure: str = Field(..., description="Procedure details")
    location: str = Field(..., description="Location")
    date: datetime = Field(..., description="Case date")
    format: str = Field(..., description="Report format (CSV, JSON, PDF)")
    filters: Optional[dict] = Field(None, description="Filters for report generation")

class Feedback(BaseModel):
    """Feedback model"""
    user_id: str = Field(..., description="User providing feedback")
    comments: str = Field(..., description="Feedback comments")
    rating: Optional[int] = Field(None, description="Feedback rating")
