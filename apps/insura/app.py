"""
Insura App - Insurance Management Platform
"""

from fastapi import FastAPI, APIRouter
from typing import Dict, Any


def build_app() -> FastAPI:
    """Build and return the insura app FastAPI instance"""
    
    app = FastAPI(
        title="Insura - Insurance Management",
        description="Healthcare insurance and billing management",
        version="1.0.0"
    )
    
    router = APIRouter()
    
    @router.get("/")
    async def insura_root() -> Dict[str, Any]:
        """Root endpoint for insurance management"""
        return {
            "app": "insura",
            "name": "Insura - Insurance Management", 
            "description": "Healthcare insurance and billing management",
            "version": "1.0.0",
            "features": [
                "insurance_claims",
                "billing_management",
                "provider_networks",
                "prior_authorization",
                "eligibility_verification"
            ],
            "status": "active"
        }
    
    @router.get("/health")
    async def insura_health() -> Dict[str, str]:
        """Health check endpoint"""
        return {"status": "healthy", "service": "insura"}
    
    @router.get("/claims")
    async def get_claims() -> Dict[str, Any]:
        """Get insurance claims data"""
        return {
            "claims": [],
            "total": 0,
            "message": "Claims service ready"
        }
    
    @router.get("/billing")
    async def get_billing() -> Dict[str, Any]:
        """Get billing information"""
        return {
            "billing": [],
            "total": 0,
            "message": "Billing service ready"
        }
    
    app.include_router(router, prefix="/api/v1")
    
    return app
