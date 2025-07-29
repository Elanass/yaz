"""
Models for auto-generation requests in journal service.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class AutoGenerateRequest(BaseModel):
    """
    Request for auto-generating journal content from clinical data
    """
    patient_id: str = Field(..., description="The patient ID to generate content for")
    template_id: str = Field(..., description="The template ID to use for generation")
    data_sources: List[str] = Field(default_factory=list, description="Data sources to use")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for generation")
    mode: str = Field("complete", description="Generation mode: complete, partial, or suggested")
