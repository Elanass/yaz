"""
Educa App - Medical Education Platform
"""

import logging
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("educa")


def build_app() -> FastAPI:
    """Build and return the educa app FastAPI instance"""
    
    app = FastAPI(
        title="Educa - Medical Education Platform",
        description="Medical education and training platform",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    router = APIRouter()
    
    @router.get("/")
    async def educa_root():
        """Root endpoint for medical education platform"""
        return {
            "app": "educa",
            "description": "Medical education and training platform",
            "version": "1.0.0",
            "features": [
                "course_management",
                "assessment_tools",
                "certification_tracking",
                "learning_analytics"
            ],
            "status": "active",
            "endpoints": {
                "courses": "/courses",
                "assessments": "/assessments"
            }
        }
    
    @router.get("/health")
    async def health_check():
        return {"status": "healthy", "app": "educa"}
    
    @router.get("/courses")
    async def get_courses():
        """Get available courses"""
        return {
            "courses": [],
            "total": 0,
            "categories": ["surgery", "medicine", "nursing", "pharmacy"]
        }
    
    @router.get("/assessments")
    async def get_assessments():
        """Get available assessments"""
        return {
            "assessments": [],
            "total": 0,
            "types": ["quiz", "exam", "practical", "simulation"]
        }
    
    app.include_router(router)
    return app
