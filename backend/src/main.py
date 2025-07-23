"""
FastAPI backend for Gastric ADCI Platform
Main application factory and configuration
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import time

from .core.config import get_settings
from .core.security import SecurityMiddleware
from .core.logging import setup_logging
from .db.database import init_db, close_db
from .api import api_router
from .services.audit import AuditService
from .services.metrics import MetricsService

# Import frontend integration
from frontend.app import create_frontend_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    settings = get_settings()
    
    # Startup
    setup_logging()
    await init_db()
    
    # Initialize services
    app.state.audit_service = AuditService()
    app.state.metrics_service = MetricsService()
    
    yield
    
    # Shutdown
    await close_db()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title="Gastric ADCI Platform API",
        description="Gastric Oncology-Surgery Decision Support Platform",
        version="1.0.0",
        docs_url="/api/docs" if settings.debug else None,
        redoc_url="/api/redoc" if settings.debug else None,
        openapi_url="/api/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Security middleware
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware for production
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts
        )
    
    # Performance monitoring middleware
    @app.middleware("http")
    async def monitor_performance(request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log performance metrics
        if hasattr(request.app.state, 'metrics_service'):
            await request.app.state.metrics_service.record_request(
                method=request.method,
                endpoint=str(request.url.path),
                status_code=response.status_code,
                duration=process_time
            )
        
        return response
    
    # Audit logging middleware
    @app.middleware("http")
    async def audit_logging(request: Request, call_next):
        # Log request
        if hasattr(request.app.state, 'audit_service'):
            await request.app.state.audit_service.log_request(request)
        
        response = await call_next(request)
        
        # Log response
        if hasattr(request.app.state, 'audit_service'):
            await request.app.state.audit_service.log_response(request, response)
        
        return response
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
    
    # Integrate FastHTML frontend
    frontend_app = create_frontend_app()
    
    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint for load balancers"""
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": time.time()
        }
    
    # Serve frontend through FastHTML
    @app.get("/{path:path}", response_class=HTMLResponse, include_in_schema=False)
    async def serve_frontend(request: Request, path: str = ""):
        """Serve frontend pages through FastHTML"""
        # Delegate to FastHTML app
        return await frontend_app(request.scope, request.receive, request._send)
    
    return app
