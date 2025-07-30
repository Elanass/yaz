#!/usr/bin/env python3
"""
Decision Precision in Surgery - Gastric ADCI Surgery FLOT Impact Platform
Production-ready FastAPI application with optimized imports and error handling
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from core.config.platform_config import config
from core.models.base import ApiResponse, HealthStatus
from core.services.logger import get_logger
from core.utils.helpers import LoggingUtils
from core.licensing_manager import licensing_manager
from orches.main import run as run_orchestrator

# Setup logging
LoggingUtils.setup_structured_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with improved error handling and initialization"""
    
    # Startup
    logger.info("🚀 Starting Decision Precision in Surgery Platform - Gastric ADCI FLOT Impact")
    
    # Initialize database
    try:
        from data.database import init_database
        await init_database()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # We don't raise the exception here to allow the app to start even with DB issues
        # This is a production-focused approach that allows for graceful degradation
    
    # Initialize core services with better error isolation
    service_initialization_tasks = []
    
    try:
        # Start orchestrator for service coordination
        logger.info("Starting orchestrator...")
        run_orchestrator()
        
        # Pre-initialize key engines - use lazy loading to improve startup time
        logger.info("Pre-initializing key engines...")
        
        # Register initialization tasks to run concurrently
        service_initialization_tasks.extend([
            asyncio.create_task(initialize_adci_engine()),
            asyncio.create_task(initialize_flot_analyzer()),
            asyncio.create_task(initialize_impact_calculator())
        ])
        
        # Import and initialize auth and decision services
        from features.auth.service import auth_service
        from features.decisions.service import DecisionService
        
        # Create decision service instance
        decision_service = DecisionService()
        
        # Health checks
        async def perform_health_checks():
            try:
                auth_health = await auth_service.health_check()
                decision_health = await decision_service.health_check()
                logger.info("✅ All services healthy")
            except Exception as e:
                logger.error(f"❌ Service health check failed: {e}")
        
        # Schedule health checks to run in the background
        if not config.is_testing:  # Skip in testing mode
            service_initialization_tasks.append(
                asyncio.create_task(perform_health_checks())
            )
        
    except Exception as e:
        logger.error(f"❌ Core services initialization failed: {e}")
    
    # Register any cache warmup or data preloading tasks here
    try:
        # Run all initialization tasks concurrently
        if service_initialization_tasks:
            await asyncio.gather(*service_initialization_tasks, return_exceptions=True)
    except Exception as e:
        logger.error(f"❌ Service initialization tasks failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Decision Precision in Surgery Platform")
    
    # Close any open connections or resources
    try:
        # Close database connections
        from data.database.services import close_db_connections
        await close_db_connections()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database connections: {e}")


# Create FastAPI app with optimized settings
app = FastAPI(
    title="Decision Precision in Surgery",
    description="""
    A healthcare-grade Progressive Web App for surgical decision support
    with a focus on gastric oncology using the ADCI (Adaptive Decision Confidence Index) 
    framework and FLOT protocol impact assessment.
    """,
    version=config.api_version,
    lifespan=lifespan,
    # Only enable docs in development or when explicitly enabled
    docs_url="/docs" if config.enable_swagger else None,
    redoc_url="/redoc" if config.enable_swagger else None,
)


# Add middleware with proper security settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-CSRF-Token", "X-Requested-With"],
)

# Add session middleware with secure configuration
app.add_middleware(
    SessionMiddleware,
    secret_key=config.secret_key,
    session_cookie="gastric_adci_session",
    max_age=86400,  # 1 day in seconds
    same_site="lax",
    https_only=config.is_production,  # Only use HTTPS in production
)

# Add Gzip compression for performance optimization
if config.enable_response_compression:
    app.add_middleware(GZipMiddleware, minimum_size=1000)

# Import API router
from api.v1.main import api_router

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Serve static files with optimized caching
app.mount(
    "/static", 
    StaticFiles(directory="web/static"), 
    name="static"
)

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Return a JSON response for API requests, HTML for web requests
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred"},
        )
    else:
        # For web requests, return a simple error page
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred. Please try again later."}
        )


@app.get("/", tags=["Root"], include_in_schema=False)
async def root():
    """Redirect to the PWA app"""
    return RedirectResponse(url="/api/v1/")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    # Improved health check with more comprehensive status information
    status = "healthy"
    database_connected = True
    api_available = True
    
    # Check database connectivity
    try:
        from data.database import check_database_connection
        database_connected = await check_database_connection()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        database_connected = False
        status = "degraded"
    
    return HealthStatus(
        status=status,
        version=config.api_version,
        database_connected=database_connected,
        api_available=api_available,
        environment=config.environment
    )


# Engine initialization functions
async def initialize_adci_engine():
    """Initialize ADCI Engine with error handling"""
    try:
        from features.decisions.adci_engine import ADCIEngine
        adci_engine = ADCIEngine()
        logger.info("✅ ADCI Engine initialized successfully")
        return adci_engine
    except Exception as e:
        logger.error(f"❌ Failed to initialize ADCI Engine: {e}")
        return None

async def initialize_flot_analyzer():
    """Initialize FLOT Analyzer with error handling"""
    try:
        from features.protocols.flot_analyzer import FLOTAnalyzer
        flot_analyzer = FLOTAnalyzer()
        logger.info("✅ FLOT Analyzer initialized successfully")
        return flot_analyzer
    except Exception as e:
        logger.error(f"❌ Failed to initialize FLOT Analyzer: {e}")
        return None

async def initialize_impact_calculator():
    """Initialize Impact Metrics Calculator with error handling"""
    try:
        from features.analysis.impact_metrics import ImpactMetricsCalculator
        impact_calculator = ImpactMetricsCalculator()
        logger.info("✅ Impact Metrics Calculator initialized successfully")
        return impact_calculator
    except Exception as e:
        logger.error(f"❌ Failed to initialize Impact Metrics Calculator: {e}")
        return None


if __name__ == "__main__":
    # Run using Uvicorn with optimized settings when called directly
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=config.debug_mode,
        log_level=config.log_level.lower(),
        workers=config.workers if config.is_production else 1,
        proxy_headers=config.is_production,  # Enable in production for proper IP forwarding
        forwarded_allow_ips="*" if config.is_production else None,
    )
