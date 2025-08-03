"""
Surgify API v1 - Clean Surgery Analytics Platform API
"""

from fastapi import APIRouter

# Import core API routers
from .dashboard import router as dashboard_router
from .cases import router as cases_router
from .auth import router as auth_router

# Create main router
router = APIRouter()

# Include core routers
router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(cases_router, prefix="/cases", tags=["Cases"])
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@router.get("/")
async def api_root():
    """API v1 root endpoint"""
    return {
        "service": "Surgify - Decision Precision Engine",
        "version": "2.0.0",
        "description": "Surgery Analytics Platform with AI-Powered Decision Support",
        "endpoints": {
            "dashboard": "/api/v1/dashboard",
            "cases": "/api/v1/cases",
            "auth": "/api/v1/auth"
        },
        "features": [
            "Clinical Decision Support",
            "Case Management",
            "Analytics Dashboard",
            "Real-time Monitoring"
        ]
    }
