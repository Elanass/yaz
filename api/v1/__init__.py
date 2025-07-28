"""
API v1 endpoints for the Gastric ADCI Platform.

This module provides the FastAPI router that includes all v1 API endpoints.
"""

from fastapi import APIRouter

# Import all API modules
from .auth import router as auth_router
from .decisions import router as decisions_router
from .journal import router as journal_router
from .services.event_logger import router as event_logger_router
from .services.event_correlation import router as event_correlation_router
from .analysis_retrospective import router as retrospective_analysis_router
from .analysis_prospective import router as prospective_analysis_router

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(decisions_router)
api_router.include_router(journal_router)
api_router.include_router(event_logger_router)
api_router.include_router(event_correlation_router)
api_router.include_router(retrospective_analysis_router)
api_router.include_router(prospective_analysis_router)