#!/usr/bin/env python3
"""
Gastric ADCI Platform - Surgery Decision Support
Clean FastAPI application with Surgify UI and WebAuthn authentication
"""

import logging
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Import web router for Surgify UI
from web.router import web_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    "app_name": "Gastric ADCI Platform",
    "version": "2.0.0",
    "description": "Surgery decision support platform with Surgify UI and WebAuthn",
    "environment": os.getenv("ENVIRONMENT", "development"), 
    "host": os.getenv("HOST", "0.0.0.0"),
    "port": int(os.getenv("PORT", "8000")),
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    "cors_origins": ["*"]
}

def create_app() -> FastAPI:
    """Create clean FastAPI application"""
    
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
    
    # Mount static files
    static_path = Path("web/static")
    if static_path.exists():
        app.mount("/static", StaticFiles(directory="web/static"), name="static")
    
    # Include Surgify UI router
    app.include_router(web_router)
    
    # Include complete API v1 router with all modules
    from api.v1 import router as api_v1_router
    app.include_router(api_v1_router, prefix="/api/v1")
    
    # Core API endpoints  
    @app.get("/api")
    async def api_root():
        """API root endpoint"""
        return {
            "message": "Gastric ADCI Platform API",
            "version": CONFIG["version"],
            "status": "operational",
            "endpoints": {
                "health": "/api/health",
                "docs": "/docs",
                "v1": "/api/v1"
            }
        }
    
    @app.get("/api/health")
    async def health():
        """Health check"""
        return {"status": "healthy", "version": CONFIG["version"]}
    
    return app

# Create app instance
app = create_app()

def main():
    """Main entry point"""
    logger.info(f"🚀 Starting {CONFIG['app_name']} on {CONFIG['host']}:{CONFIG['port']}")
    logger.info(f"🎨 Surgify UI: http://{CONFIG['host']}:{CONFIG['port']}")
    logger.info(f"📚 API docs: http://{CONFIG['host']}:{CONFIG['port']}/docs")
    logger.info(f"🔐 WebAuthn enabled")
    
    uvicorn.run(
        "app:app",
        host=CONFIG["host"],
        port=CONFIG["port"],
        reload=CONFIG["debug"],
        log_level="info"
    )

if __name__ == "__main__":
    main()
