"""Surgify API v1 - Enhanced Surgery Analytics Platform API
Complete CSV-to-Insights Pipeline with Professional Deliverable Generation.
"""

from fastapi import APIRouter

from .ai import router as ai_router
from .ai_enhanced import router as ai_enhanced_router
from .auth import router as auth_router
from .cases import router as cases_router
from .chat import router as chat_router

# Import core API routers
from .dashboard import router as dashboard_router
from .datasets import router as datasets_router
from .deliverables import router as deliverables_router
from .downloads import router as downloads_router
from .feedback import router as feedback_router
from .health import router as health_router  # Health & monitoring endpoints
from .ingestion import router as ingestion_router
from .islands import router as islands_router  # New islands architecture
from .mobile import router as mobile_router
from .notifications import router as notifications_router  # New notifications system
from .pipeline import router as pipeline_router  # New pipeline router
from .proposals import router as proposals_router
from .recommendations import router as recommendations_router
from .search import router as search_router
from .studies import router as studies_router
from .subjects import router as subjects_router
from .sync import router as sync_router


# Create main router
router = APIRouter()

# Register all API routes
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(ingestion_router, prefix="/ingest", tags=["Data Ingestion"])
router.include_router(cases_router, prefix="/cases", tags=["Case Management"])
router.include_router(
    deliverables_router, prefix="/deliverables", tags=["Deliverables"]
)
router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(sync_router, prefix="/sync", tags=["Real-time Sync"])
router.include_router(search_router, prefix="/search", tags=["Search"])
router.include_router(
    recommendations_router, prefix="/recommendations", tags=["AI Recommendations"]
)
router.include_router(chat_router, prefix="/chat", tags=["Chat"])
router.include_router(proposals_router, prefix="/proposals", tags=["Proposals"])
router.include_router(feedback_router, prefix="/feedback", tags=["Feedback"])
router.include_router(downloads_router, prefix="/downloads", tags=["Downloads"])
router.include_router(mobile_router, prefix="/mobile", tags=["Mobile API"])
router.include_router(ai_router, prefix="/ai", tags=["AI Features"])
router.include_router(ai_enhanced_router, prefix="/ai-enhanced", tags=["Enhanced AI"])
router.include_router(islands_router, prefix="/islands", tags=["Islands Architecture"])
router.include_router(
    notifications_router, prefix="/notifications", tags=["Notifications"]
)
router.include_router(pipeline_router, prefix="/pipeline", tags=["Data Pipeline"])
router.include_router(studies_router, prefix="/studies", tags=["Studies"])
router.include_router(subjects_router, prefix="/subjects", tags=["Subjects"])
router.include_router(datasets_router, prefix="/datasets", tags=["Datasets"])
router.include_router(
    health_router, tags=["Health & Monitoring"]
)  # No prefix for health


@router.get("/")
async def api_root():
    """API v1 root endpoint with enhanced features."""
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
            "Islands Architecture (Landing, Indexing, Interacting)",
            "Real-time Notifications via SSE",
            "JWT Authentication with WebAuthn Support",
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
            "islands": "/api/v1/islands",
            "notifications": "/api/v1/notifications",
            "studies": "/api/v1/studies",
            "subjects": "/api/v1/subjects",
            "datasets": "/api/v1/datasets",
            "health": "/api/v1/health",
        },
        "cache": {"enabled": True, "backend": "Redis", "default_ttl": 300},
        "architecture": {
            "stateless": True,
            "idempotent": True,
            "modular": True,
            "reproducible": True,
            "islands": {
                "landing": "Main entry point and dashboard",
                "indexing": "Search and discovery interface",
                "interacting": "Active case workstation environment",
            },
        },
    }


# Stable router exports
__all__ = [
    "ai_enhanced_router",
    "ai_router",
    "auth_router",
    "cases_router",
    "chat_router",
    "dashboard_router",
    "datasets_router",
    "deliverables_router",
    "health_router",
    "router_v1",
    "studies_router",
    "subjects_router",
]
