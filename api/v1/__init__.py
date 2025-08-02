"""
API v1 endpoints - Complete Gastric ADCI Platform API
"""

from fastapi import APIRouter

# Import all API routers
from .auth import router as auth_router
from .surgery import router as surgery_router
from .insurance import router as insurance_router
from .logistics import router as logistics_router
from .reporter import router as reporter_router

# Create main router
router = APIRouter()

# Include all routers
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(surgery_router, prefix="/surgery", tags=["Surgery Management"])
router.include_router(insurance_router, prefix="/insurance", tags=["Insurance Management"])
router.include_router(logistics_router, prefix="/logistics", tags=["Logistics Management"])
router.include_router(reporter_router, prefix="/reporter", tags=["Reporting & Analytics"])

@router.get("/")
async def api_root():
    """API v1 root endpoint"""
    return {
        "message": "Gastric ADCI Platform API v1",
        "version": "1.0.0",
        "description": "Complete API for gastric surgery case management, insurance processing, and logistics coordination",
        "endpoints": {
            "auth": "/api/v1/auth",
            "surgery": "/api/v1/surgery", 
            "insurance": "/api/v1/insurance",
            "logistics": "/api/v1/logistics",
            "reporter": "/api/v1/reporter"
        },
        "features": [
            "WebAuthn Authentication",
            "Surgery Procedure Management",
            "Insurance Claims Processing", 
            "Patient Transport Logistics",
            "Resource Management",
            "Staff Scheduling",
            "Reporting & Analytics"
        ]
    }