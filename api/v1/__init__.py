"""
API v1 endpoints
"""

from fastapi import APIRouter

# Core routers
from .auth import router as auth_router
from .decisions import router as decisions_router
from .analysis import router as analysis_router
from .cases import router as cases_router

# Create main router
router = APIRouter()

# Include routers
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(decisions_router, prefix="/decisions", tags=["Decisions"]) 
router.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
router.include_router(cases_router, prefix="/cases", tags=["Cases"])

@router.get("/")
async def api_root():
    """API v1 root endpoint"""
    return {
        "message": "Decision Precision in Surgery API v1",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "decisions": "/api/v1/decisions", 
            "analysis": "/api/v1/analysis",
            "cases": "/api/v1/cases"
        }
    }