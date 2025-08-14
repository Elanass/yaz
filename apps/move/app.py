"""
Move App - Logistics Management Platform
"""

import logging
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("move")


def build_app() -> FastAPI:
    """Build and return the move app FastAPI instance"""
    
    app = FastAPI(
        title="Move - Logistics Management Platform",
        description="Medical logistics and supply chain management",
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
    async def move_root():
        """Root endpoint for logistics management platform"""
        return {
            "app": "move",
            "description": "Medical logistics and supply chain management",
            "version": "1.0.0",
            "features": [
                "inventory_management",
                "supply_tracking", 
                "delivery_coordination",
                "vendor_management"
            ],
            "status": "active",
            "endpoints": {
                "inventory": "/inventory",
                "tracking": "/tracking"
            }
        }
    
    @router.get("/health")
    async def health_check():
        return {"status": "healthy", "app": "move"}
    
    @router.get("/inventory")
    async def inventory_overview():
        """Inventory management overview"""
        return {
            "feature": "inventory_management",
            "description": "Medical supply inventory tracking and management",
            "status": "available",
            "items": []
        }
    
    @router.get("/tracking")
    async def supply_tracking():
        """Supply tracking overview"""
        return {
            "feature": "supply_tracking",
            "description": "Real-time tracking of medical supplies and deliveries",
            "status": "available",
            "shipments": []
        }
    
    app.include_router(router)
    return app
