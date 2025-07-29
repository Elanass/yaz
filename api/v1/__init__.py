"""
API v1 endpoints for the Decision Precision in Surgery Platform.

This module provides the FastAPI router that includes all v1 API endpoints.
"""

from fastapi import APIRouter

# Import all API modules
from .auth import router as auth_router
from .decisions import router as decisions_router
from .journal import router as journal_router
from .dashboard import router as dashboard_router

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(decisions_router)
api_router.include_router(journal_router)
api_router.include_router(dashboard_router)