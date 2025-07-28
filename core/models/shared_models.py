"""
Shared Data Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class Patient(BaseModel):
    """Patient data model"""
    id: str = Field(..., description="Unique patient identifier")
    age: int = Field(..., description="Patient age")
    gender: str = Field(..., description="Patient gender")
    comorbidities: List[str] = Field(default=[], description="List of comorbidities")
    tumor_stage: str = Field(..., description="Tumor stage")
    tumor_location: str = Field(..., description="Tumor location")

class Transition(BaseModel):
    """Markov transition model"""
    from_state: str = Field(..., description="Starting state")
    to_state: str = Field(..., description="Ending state")
    probability: float = Field(..., description="Transition probability")

class Insight(BaseModel):
    """Insight data model"""
    id: str = Field(..., description="Unique insight identifier")
    domain: str = Field(..., description="Insight domain")
    data: dict = Field(..., description="Insight data")

class ReportParams(BaseModel):
    """Report generation parameters"""
    format: str = Field(..., description="Report format (CSV, JSON, PDF)")
    filters: Optional[dict] = Field(None, description="Filters for report generation")

class Feedback(BaseModel):
    """Feedback model"""
    user_id: str = Field(..., description="User providing feedback")
    comments: str = Field(..., description="Feedback comments")
    rating: Optional[int] = Field(None, description="Feedback rating")
