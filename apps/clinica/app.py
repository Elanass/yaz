"""
Clinica App - Integrated Clinical Care
"""

import logging
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("clinica")


def build_app() -> FastAPI:
    """Build and return the clinica app FastAPI instance"""
    
    app = FastAPI(
        title="Clinica - Integrated Clinical Care",
        description="Comprehensive clinical care experience",
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
    async def clinica_root():
        """Root endpoint for integrated clinical care"""
        return {
            "app": "clinica", 
            "description": "Comprehensive clinical care experience",
            "version": "1.0.0",
            "features": [
                "patient_management",
                "clinical_workflows",
                "care_coordination",
                "medical_records"
            ],
            "status": "active"
        }
    
    @router.get("/health")
    async def health_check():
        return {"status": "healthy", "app": "clinica"}
    
    app.include_router(router)
    return app
