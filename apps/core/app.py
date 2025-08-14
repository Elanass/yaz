"""
Core App - Core YAZ Platform Services
"""

import logging
from fastapi import FastAPI, APIRouter
from typing import Dict, Any

logger = logging.getLogger("core")


def build_app() -> FastAPI:
    """Build and return the core app FastAPI instance"""
    
    app = FastAPI(
        title="YAZ Core Platform",
        description="Core YAZ platform services and management",
        version="2.0.0"
    )
    
    router = APIRouter()
    
    @router.get("/")
    async def core_root() -> Dict[str, Any]:
        """Root endpoint for core platform"""
        return {
            "app": "core",
            "name": "YAZ Core Platform", 
            "description": "Core YAZ platform services and management",
            "version": "2.0.0",
            "features": [
                "platform_management",
                "user_authentication",
                "system_monitoring",
                "configuration_management"
            ],
            "endpoints": {
                "health": "/core/health",
                "status": "/core/status",
                "config": "/core/config"
            }
        }
    
    @router.get("/health")
    async def core_health() -> Dict[str, Any]:
        """Health check for core platform"""
        return {
            "status": "healthy",
            "app": "core",
            "timestamp": "2025-08-11T00:00:00Z"
        }
    
    @router.get("/status") 
    async def core_status() -> Dict[str, Any]:
        """Status information for core platform"""
        return {
            "app": "core",
            "status": "running",
            "uptime": "1h 30m",
            "memory_usage": "45MB",
            "active_connections": 12
        }
    
    @router.get("/config")
    async def core_config() -> Dict[str, Any]:
        """Configuration information for core platform"""
        return {
            "app": "core",
            "environment": "development",
            "debug": True,
            "features_enabled": [
                "authentication",
                "monitoring", 
                "logging"
            ]
        }
    
    app.include_router(router)
    
    # Include API routers
    try:
        from apps.core.routers import fhir_proxy, forms, imaging, smart
        app.include_router(fhir_proxy.router, prefix="/api/fhir", tags=["FHIR"])
        app.include_router(forms.router, prefix="/api/forms", tags=["Forms"])
        app.include_router(imaging.router, prefix="/api/imaging", tags=["Imaging"])
        app.include_router(smart.router, prefix="/api/smart", tags=["SMART"])
    except ImportError as e:
        logger.info(f"API routers not available: {e}")
    
    return app
