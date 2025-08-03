#!/usr/bin/env python3
"""
Surgify - YAZ Surgery Analytics Platform
Decision Precision Engine with Surgify Template Integration
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# Core imports
from core.config.unified_config import get_settings
from core.services.logger import setup_logging
from core.database import create_tables, engine
from core.models.database_models import Base

# API imports
from api.v1 import router as api_v1_router
from web.router import web_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Surgify - Decision Precision Engine")
    
    # Initialize database
    logger.info("📊 Initializing database...")
    Base.metadata.create_all(bind=engine)
    
    # Initialize modules
    await initialize_modules()
    
    yield
    
    logger.info("🛑 Shutting down Surgify...")

async def initialize_modules():
    """Initialize all application modules"""
    logger.info("🧠 Initializing Surgify modules...")
    
    modules = {
        "surgery": "Surgical procedure planning and execution",
        "analytics": "Data analysis and reporting", 
        "clinical": "Clinical workstation and decision support",
        "auth": "Authentication and user management"
    }
    
    for module, description in modules.items():
        logger.info(f"  ✓ {module}: {description}")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    # Create FastAPI app with Surgify branding
    app = FastAPI(
        title="Surgify - Decision Precision Engine",
        description="Advanced Surgery Analytics Platform with AI-Powered Decision Support",
        version="2.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan
    )
    
    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Static files
    app.mount("/static", StaticFiles(directory="web/static"), name="static")
    
    # Routes
    app.include_router(api_v1_router, prefix="/api/v1")
    app.include_router(web_router)
    
    # Root redirect to Surgify interface
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Redirect to Surgify web interface"""
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Redirecting to Surgify...</title>
            <meta http-equiv="refresh" content="0; url=/surgify">
        </head>
        <body>
            <h1>Redirecting to Surgify...</h1>
            <p>If you are not redirected automatically, <a href="/surgify">click here</a>.</p>
        </body>
        </html>
        """)
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "Surgify Decision Precision Engine",
            "version": "2.0.0",
            "timestamp": str(asyncio.get_event_loop().time())
        }
    
    # Error handlers
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={"message": "Resource not found", "service": "Surgify"}
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        logger.error(f"Internal server error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "service": "Surgify"}
        )
    
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    """Run the application"""
    logger.info("🏥 Starting Surgify - Decision Precision Engine")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
