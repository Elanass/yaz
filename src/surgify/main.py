#!/usr/bin/env python3
"""
Surgify - Advanced Surgery Analytics Platform
Decision Precision Engine with Modern Architecture
"""

import asyncio
import logging
import os
import uuid
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
from .core.config.unified_config import get_settings
from .core.services.logger import setup_logging, log_request, log_error
from .core.database import create_tables, engine
from .core.models.database_models import Base
from .core.services.registry import get_service_registry

# API imports
from .api.v1 import router as api_v1_router
from .ui.web.router import web_router

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    settings = get_settings()
    logger.info("🚀 Starting Surgify - Decision Precision Engine")
    logger.info(f"🔧 Environment: {settings.environment}")
    logger.info(f"🔧 Debug Mode: {settings.debug}")
    
    # Ensure required directories exist
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    logger.info("📊 Initializing database...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Initialize services
    await initialize_services()
    
    # Initialize modules
    await initialize_modules()
    
    logger.info("✅ Surgify startup completed successfully")
    
    yield
    
    logger.info("🛑 Shutting down Surgify...")
    await cleanup_services()
    logger.info("✅ Shutdown completed")

async def initialize_services():
    """Initialize core services"""
    logger.info("🔧 Initializing core services...")
    
    # Service registry is already initialized as singleton
    registry = get_service_registry()
    
    # Register core services here
    # registry.register_singleton(DatabaseService, database_service)
    # registry.register_singleton(AuthService, auth_service)
    
    logger.info("✅ Core services initialized")

async def cleanup_services():
    """Cleanup services on shutdown"""
    logger.info("🧹 Cleaning up services...")
    # Add cleanup logic here
    logger.info("✅ Services cleaned up")

async def initialize_modules():
    """Initialize all application modules"""
    logger.info("🧠 Initializing application modules...")
    
    modules = {
        "surgery": "Surgical procedure planning and execution",
        "analytics": "Data analysis and reporting", 
        "clinical": "Clinical workstation and decision support",
        "auth": "Authentication and user management",
        "collaboration": "Real-time collaboration features"
    }
    
    for module, description in modules.items():
        logger.info(f"  ✓ {module}: {description}")
    
    logger.info("✅ All modules initialized")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    # Create FastAPI app with enhanced configuration
    app = FastAPI(
        title=f"{settings.app_name} - Decision Precision Engine",
        description="Advanced Surgery Analytics Platform with AI-Powered Decision Support",
        version=settings.app_version,
        docs_url="/api/docs" if settings.enable_docs else None,
        redoc_url="/api/redoc" if settings.enable_docs else None,
        openapi_url="/api/openapi.json" if settings.enable_docs else None,
        lifespan=lifespan,
        debug=settings.debug
    )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = str(uuid.uuid4())
        
        # Log request
        log_request(
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            user_id=getattr(request.state, 'user_id', None)
        )
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            log_error(e, {"request_id": request_id, "path": str(request.url.path)})
            raise
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Static files
    static_dir = Path("src/surgify/ui/web/static")
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # API routes
    app.include_router(api_v1_router, prefix="/api/v1", tags=["API v1"])
    
    # Web routes
    app.include_router(web_router, tags=["Web Interface"])
    
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
    
    # Global error handler for debugging
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception: {exc}", exc_info=True)
        if settings.debug:
            raise exc
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "service": "Surgify"}
        )

    return app

# Create the app instance
app = create_app()

def main():
    """Run the application"""
    settings = get_settings()
    logger.info(f"🏥 Starting {settings.app_name} - Decision Precision Engine")
    
    uvicorn.run(
        "surgify.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
        access_log=True
    )

if __name__ == "__main__":
    main()
