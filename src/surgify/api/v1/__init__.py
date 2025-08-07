"""
Surgify API v1 - Enhanced Surgery Analytics Platform API
Complete CSV-to-Insights Pipeline with Professional Deliverable Generation
"""

from fastapi import APIRouter

from .ai import router as ai_router
from .ai_enhanced import enhanced_router as ai_enhanced_router  # Enhanced AI with local models
from .auth import router as auth_router
from .cases import router as cases_router
from .chat import router as chat_router
# Import core API routers
from .dashboard import router as dashboard_router
from .deliverables import router as deliverables_router
from .downloads import router as downloads_router
from .feedback import router as feedback_router
from .ingestion import router as ingestion_router
from .mobile import router as mobile_router
from .pipeline import router as pipeline_router  # New pipeline router
from .proposals import router as proposals_router
from .recommendations import router as recommendations_router
from .search import router as search_router
from .sync import router as sync_router

# Create main router
router = APIRouter()

# Include core routers with enhanced modular endpoints
router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(cases_router, prefix="/cases", tags=["Cases"])
router.include_router(sync_router, prefix="/sync", tags=["Sync"])
router.include_router(
    deliverables_router, prefix="/deliverables", tags=["Deliverables"]
)
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(proposals_router, prefix="/collaboration", tags=["Collaboration"])
router.include_router(search_router, tags=["Search"])
router.include_router(mobile_router, tags=["Mobile"])
router.include_router(feedback_router, tags=["Feedback"])
router.include_router(
    recommendations_router, prefix="/recommendations", tags=["Recommendations"]
)
router.include_router(downloads_router, prefix="/downloads", tags=["Downloads"])
router.include_router(ai_router, prefix="/ai", tags=["AI Services"])
router.include_router(ai_enhanced_router, prefix="/ai-enhanced", tags=["Enhanced AI Services"])  # Free/low-cost AI
router.include_router(chat_router, prefix="/chat", tags=["Chat Integration"])

# New enhanced endpoints
router.include_router(ingestion_router, prefix="/ingestion", tags=["Data Ingestion"])
router.include_router(
    pipeline_router, tags=["CSV-to-Insights Pipeline"]
)  # Main pipeline endpoint


@router.get("/")
async def api_root():
    """API v1 root endpoint with enhanced features"""
    return {
        "service": "Surgify - Decision Precision Engine",
        "version": "2.1.0",
        "description": "Surgery Analytics Platform with AI-Powered Decision Support",
        "features": [
            "Clinical Decision Support",
            "Case Management with Enhanced Services",
            "Real-time Data Synchronization",
            "Document Generation & Deliverables",
            "Analytics Dashboard",
            "Redis Caching for High Performance",
            "Modular API Architecture",
        ],
        "endpoints": {
            "dashboard": "/api/v1/dashboard",
            "cases": "/api/v1/cases",
            "sync": "/api/v1/sync",
            "deliverables": "/api/v1/deliverables",
            "auth": "/api/v1/auth",
            "collaboration": "/api/v1/collaboration",
            "search": "/api/v1/search",
            "recommendations": "/api/v1/recommendations",
        },
        "cache": {"enabled": True, "backend": "Redis", "default_ttl": 300},
        "architecture": {
            "stateless": True,
            "idempotent": True,
            "modular": True,
            "reproducible": True,
        },
    }
