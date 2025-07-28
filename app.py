"""
Gastric ADCI Platform - Main Application
Clean, DRY, MVP-focused implementation
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from core.config.settings import get_settings
from core.models.base import ApiResponse, HealthStatus
from core.utils.helpers import LoggingUtils

# Import API routers
from api.v1.auth import router as auth_router
from api.v1.decisions import router as decisions_router

# Setup logging
LoggingUtils.setup_structured_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    
    # Startup
    logger.info("🚀 Starting Gastric ADCI Platform")
    
    # Initialize services
    from features.auth.service import auth_service
    from features.decisions.service import DecisionService
    
    # Create decision service instance
    decision_service = DecisionService()
    
    # Health checks
    try:
        auth_health = await auth_service.health_check()
        decision_health = await decision_service.health_check()
        logger.info("✅ All services healthy")
    except Exception as e:
        logger.error(f"❌ Service health check failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Gastric ADCI Platform")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    settings = get_settings()
    
    # Create app
    app = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
        description="Healthcare-grade Progressive Web App for gastric oncology decision support",
        docs_url="/api/docs" if settings.app.enable_swagger else None,
        redoc_url="/api/redoc" if settings.app.enable_swagger else None,
        openapi_url="/api/openapi.json" if settings.app.enable_swagger else None,
        lifespan=lifespan
    )
    
    # Add middleware
    setup_middleware(app, settings)
    
    # Add routes
    setup_routes(app)
    
    # Add exception handlers
    setup_exception_handlers(app)
    
    return app


def setup_middleware(app: FastAPI, settings):
    """Setup application middleware"""
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins,
        allow_credentials=True,
        allow_methods=settings.security.cors_methods,
        allow_headers=settings.security.cors_headers,
    )
    
    # Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        process_time = time.perf_counter() - start_time
        logger.info(
            "HTTP request",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=f"{process_time:.4f}s"
        )
        
        return response


def setup_routes(app: FastAPI):
    """Setup application routes"""
    
    # Health check
    @app.get("/health", response_model=ApiResponse[HealthStatus])
    async def health_check():
        """Application health check"""
        
        health = HealthStatus(
            status="healthy",
            version=get_settings().app.version,
            environment=get_settings().environment
        )
        
        # Check service health
        try:
            from features.auth.service import auth_service
            from features.decisions.service import DecisionService
            
            # Create decision service instance
            decision_service = DecisionService()
            
            auth_health = await auth_service.health_check()
            decision_health = await decision_service.health_check()
            
            health.add_component("auth", auth_health.get("status", "unknown"))
            health.add_component("decisions", decision_health.get("status", "unknown"))
            
        except Exception as e:
            health.add_component("services", "error")
            health.status = "unhealthy"
            logger.error(f"Health check failed: {e}")
        
        return ApiResponse.success_response(
            data=health,
            message="Health check completed"
        )
    
    # Root endpoint
    @app.get("/", response_model=ApiResponse[dict])
    async def root():
        """Root endpoint with API information"""
        
        return ApiResponse.success_response(
            data={
                "name": "Gastric ADCI Platform",
                "version": get_settings().app.version,
                "description": "Healthcare-grade decision support for gastric oncology",
                "docs_url": "/api/docs",
                "endpoints": {
                    "auth": "/api/v1/auth",
                    "decisions": "/api/v1/decisions",
                    "health": "/health"
                }
            },
            message="Welcome to Gastric ADCI Platform"
        )
    
    # API routes
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(decisions_router, prefix="/api/v1")
    
    # Web interface routes
    setup_web_routes(app)
    
    # Static files (for web interface)
    try:
        app.mount("/static", StaticFiles(directory="web/static"), name="static")
    except Exception:
        logger.warning("Static files directory not found")


def setup_web_routes(app: FastAPI):
    """Setup web interface routes"""
    
    from fastapi.responses import HTMLResponse
    from web.components.interface import create_page_layout, create_dashboard, create_decision_form
    
    navigation = [
        {"url": "/", "text": "Dashboard"},
        {"url": "/decision", "text": "New Decision"},
        {"url": "/analysis", "text": "Analysis"},
        {"url": "/api/docs", "text": "API Docs"}
    ]
    
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        """Main dashboard page"""
        content = create_dashboard()
        return create_page_layout("Dashboard", content, navigation)
    
    @app.get("/decision", response_class=HTMLResponse) 
    async def decision_form():
        """Decision analysis form"""
        content = create_decision_form()
        return create_page_layout("Clinical Decision Analysis", content, navigation)
        
    @app.get("/analysis", response_class=HTMLResponse)
    async def analysis_home():
        """Analysis home page"""
        with open("web/pages/analysis.html", "r") as file:
            content = file.read()
        return HTMLResponse(content=content)
        
    @app.get("/analysis/retrospective", response_class=HTMLResponse)
    async def retrospective_analysis():
        """Retrospective analysis page"""
        with open("web/pages/analysis_retrospective.html", "r") as file:
            content = file.read()
        return HTMLResponse(content=content)
        
    @app.get("/analysis/prospective", response_class=HTMLResponse)
    async def prospective_analysis():
        """Prospective analysis page"""
        with open("web/pages/analysis_prospective.html", "r") as file:
            content = file.read()
        return HTMLResponse(content=content)


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers"""
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle validation errors"""
        
        logger.warning(f"Validation error: {exc}")
        return JSONResponse(
            status_code=400,
            content=ApiResponse.error_response(
                message="Validation error",
                errors=[str(exc)]
            ).dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions"""
        
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        # Don't expose internal errors in production
        settings = get_settings()
        if settings.is_production:
            message = "An internal error occurred"
            errors = ["Internal server error"]
        else:
            message = f"Internal error: {type(exc).__name__}"
            errors = [str(exc)]
        
        return JSONResponse(
            status_code=500,
            content=ApiResponse.error_response(
                message=message,
                errors=errors
            ).dict()
        )


# For development and testing
if __name__ == "__main__":
    import time
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "app:create_app",
        factory=True,
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug,
        log_level=settings.app.log_level.lower()
    )
