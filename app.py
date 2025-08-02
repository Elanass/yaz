#!/usr/bin/env python3
"""
Gastric ADCI Platform - Minimal Surgery Decision Support
Streamlined FastAPI application with core functionality only
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Consolidated config - single source of truth
CONFIG = {
    "app_name": "Gastric ADCI Platform",
    "version": "2.0.0",
    "description": "Surgery decision support platform with ADCI framework",
    "environment": os.getenv("ENVIRONMENT", "development"), 
    "host": os.getenv("HOST", "0.0.0.0"),
    "port": int(os.getenv("PORT", "8000")),
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    "cors_origins": ["*"],  # Configure as needed
    "features": {
        "analysis": True,
        "decisions": True, 
        "cases": True,
        "adci_framework": True,
        "flot_protocol": True
    }
}

def create_app() -> FastAPI:
    """Create minimal FastAPI application"""
    
    app = FastAPI(
        title=CONFIG["app_name"],
        version=CONFIG["version"],
        description=CONFIG["description"],
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CONFIG["cors_origins"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files if they exist
    static_path = Path("static")
    if static_path.exists():
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Core endpoints
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": CONFIG["app_name"],
            "version": CONFIG["version"],
            "status": "operational",
            "docs": "/docs"
        }
    
    @app.get("/health")
    async def health():
        """Health check"""
        return {"status": "healthy", "version": CONFIG["version"]}
    
    @app.get("/api/features")
    async def features():
        """Available features"""
        return {
            "message": "Platform features",
            "features": CONFIG["features"],
            "environment": CONFIG["environment"]
        }
    
    # API endpoints
    @app.get("/api/analysis")
    async def analysis():
        """Analysis service endpoint"""
        if not CONFIG["features"]["analysis"]:
            raise HTTPException(status_code=503, detail="Analysis service disabled")
        return {
            "message": "Analysis service operational",
            "features": ["survival_analysis", "statistical_modeling", "risk_assessment"],
            "status": "enabled"
        }
    
    @app.get("/api/decisions")
    async def decisions():
        """Decision support endpoint"""
        if not CONFIG["features"]["decisions"]:
            raise HTTPException(status_code=503, detail="Decision service disabled")
        return {
            "message": "Decision support operational", 
            "adci_framework": CONFIG["features"]["adci_framework"],
            "protocols": ["flot", "neo_adjuvant"] if CONFIG["features"]["flot_protocol"] else [],
            "status": "enabled"
        }
    
    @app.get("/api/cases")
    async def cases():
        """Case management endpoint"""
        if not CONFIG["features"]["cases"]:
            raise HTTPException(status_code=503, detail="Cases service disabled")
        return {
            "message": "Case management operational",
            "supported_types": ["gastric_cancer", "surgical_planning"],
            "status": "enabled"
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
    
    return app

# Create app instance
app = create_app()

def main():
    """Main entry point"""
    logger.info(f"🚀 Starting {CONFIG['app_name']} on {CONFIG['host']}:{CONFIG['port']}")
    
    uvicorn.run(
        "app:app",
        host=CONFIG["host"],
        port=CONFIG["port"],
        reload=CONFIG["debug"],
        log_level="info"
    )

if __name__ == "__main__":
    main()
