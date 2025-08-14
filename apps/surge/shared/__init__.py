"""
Shared utilities and dependencies for SURGE app
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
import logging

logger = logging.getLogger("surge.shared")

# Shared models
class SurgeResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    status: str = "error"
    error: str
    detail: Optional[str] = None

# Shared dependencies
async def get_current_user():
    """Get current user - mock implementation for now"""
    return {"id": "user-1", "name": "Dr. Smith", "role": "surgeon"}

async def verify_api_key(api_key: Optional[str] = None):
    """Verify API key - mock implementation"""
    if not api_key:
        return {"valid": True, "user": "anonymous"}
    return {"valid": True, "user": "authenticated"}

# Shared utilities
def format_response(data: Any, message: str = None) -> SurgeResponse:
    """Format standard response"""
    return SurgeResponse(
        status="success",
        message=message,
        data=data
    )

def format_error(error: str, detail: str = None) -> ErrorResponse:
    """Format error response"""
    return ErrorResponse(
        status="error",
        error=error,
        detail=detail
    )
