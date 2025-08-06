#!/usr/bin/env python3
"""
Surgify - Advanced Surgery Analytics Platform
Decision Precision Engine with Modern Architecture
Multi-Domain Support: Surgery, Logistics, Insurance
"""

import argparse
import asyncio
import logging
import os
# Universal Research Module imports
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Add the parent src directory to the path
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from universal_research.integration.api_enhancer import ResearchAPIEnhancer
from universal_research.integration.auth_integrator import AuthIntegrator
from universal_research.integration.database_bridge import DatabaseBridge

# API imports
from .api.v1 import router as api_v1_router
# Core imports
from .core.config.unified_config import get_settings
from .core.database import create_tables, engine
# Domain adapter imports
from .core.domain_adapter import Domain, domain_registry
from .core.models.database_models import Base
from .core.services.logger import log_error, log_request, setup_logging
from .core.services.registry import get_service_registry
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

    # Initialize domain adapters
    logger.info("🎯 Initializing domain adapters...")
    validation_results = domain_registry.validate_all_domains()
    for domain, result in validation_results.items():
        status = "✅" if result.get("status") == "operational" else "⚠️"
        logger.info(f"  {status} {domain}: {result.get('message', 'Unknown status')}")

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
        "collaboration": "Real-time collaboration features",
        "universal_research": "Universal research and deliverable generation",
    }

    for module, description in modules.items():
        logger.info(f"  ✓ {module}: {description}")

    # Initialize research database components
    try:
        logger.info("🔬 Initializing Universal Research Module...")
        db_bridge = DatabaseBridge()
        db_bridge.create_research_views()
        db_bridge.create_research_indexes()
        logger.info("✅ Universal Research Module initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ Research module initialization had issues: {e}")
        logger.info("🔄 Application will continue with core functionality")

    logger.info("✅ All modules initialized")


def create_app(domain: str = None) -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()

    # Set current domain if provided
    if domain:
        try:
            domain_enum = Domain(domain)
            domain_registry.set_current_domain(domain_enum)
            logger.info(f"🎯 Set application domain to: {domain}")
        except ValueError:
            logger.warning(f"⚠️ Invalid domain '{domain}', using default behavior")

    # Create FastAPI app with enhanced configuration
    app = FastAPI(
        title=f"{settings.app_name} - Decision Precision Engine",
        description="Advanced Surgery Analytics Platform with AI-Powered Decision Support",
        version=settings.app_version,
        docs_url="/api/docs" if settings.enable_docs else None,
        redoc_url="/api/redoc" if settings.enable_docs else None,
        openapi_url="/api/openapi.json" if settings.enable_docs else None,
        lifespan=lifespan,
        debug=settings.debug,
    )

    # Store domain info in app state
    app.state.current_domain = domain
    app.state.domain_registry = domain_registry

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = str(uuid.uuid4())

        # Log request
        log_request(
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            user_id=getattr(request.state, "user_id", None),
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

    # Universal Research API routes (NEW - PRESERVES EXISTING)
    try:
        research_enhancer = ResearchAPIEnhancer()
        research_router = research_enhancer.get_router()
        app.include_router(research_router, tags=["Research Analytics"])
        logger.info("✅ Research API endpoints added successfully")

        # Initialize research authentication enhancements
        from .modules.universal_research.integration.auth_integrator import \
            AuthIntegrator

        auth_integrator = AuthIntegrator()
        auth_integrator.enhance_existing_auth_middleware(app)

    except Exception as e:
        logger.warning(f"⚠️ Research API integration had issues: {e}")
        logger.info("🔄 Application continues with core functionality")

    # Web routes
    app.include_router(web_router, tags=["Web Interface"])

    # Root redirect to Surgify interface
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Redirect to Surgify web interface"""
        return HTMLResponse(
            """
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
        """
        )

    # Health check with domain info
    @app.get("/health")
    async def health_check():
        """Health check endpoint with domain information"""
        current_adapter = domain_registry.get_current_adapter()
        return {
            "status": "healthy",
            "service": "Surgify Decision Precision Engine",
            "version": "2.0.0",
            "current_domain": current_adapter.domain.value if current_adapter else None,
            "available_domains": domain_registry.list_domains(),
            "timestamp": str(asyncio.get_event_loop().time()),
        }

    # Error handlers
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={"message": "Resource not found", "service": "Surgify"},
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        logger.error(f"Internal server error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "service": "Surgify"},
        )

    # Global error handler for debugging
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception: {exc}", exc_info=True)
        if settings.debug:
            raise exc
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "service": "Surgify"},
        )

    return app


# Create the app instance (will be recreated in main() with CLI args)
app = create_app()


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Surgify - Advanced Surgery Analytics Platform"
    )
    parser.add_argument(
        "--domain",
        choices=["surgery", "logistics", "insurance"],
        help="Set the primary domain for the application (surgery, logistics, or insurance)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=6379,
        help="Port to bind the server to (default: 6379)",
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )
    return parser.parse_args()


def main():
    """Run the application"""
    # Parse command line arguments
    args = parse_args()

    # Recreate app with domain configuration
    global app
    app = create_app(domain=args.domain)

    settings = get_settings()
    logger.info(f"🏥 Starting {settings.app_name} - Decision Precision Engine")

    if args.domain:
        logger.info(f"🎯 Running in {args.domain} domain mode")

    uvicorn.run(
        "surgify.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload or settings.is_development,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()
