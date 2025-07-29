"""
User Identity Model
"""

from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class UserIdentity(BaseModel):
    """User identity model for authentication"""
    id: UUID
    username: str
    email: str
    role: str
    permissions: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
