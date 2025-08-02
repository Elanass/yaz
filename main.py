#!/usr/bin/env python3
"""
Gastric ADCI Platform - Decision Precision Engine
Main application entry point with modular app generation
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
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Core imports
from core.config.unified_config import get_settings
from core.services.logger import setup_logging

# API imports
from api.v1 import router as api_v1_router
from web.router import web_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class DecisionPrecisionEngine:
    """Main Decision Precision Engine for generating modular apps"""
    
    def __init__(self):
        self.settings = get_settings()
        self.modules: Dict[str, str] = {}
        
    async def initialize_modules(self):
        """Initialize all application modules"""
        logger.info("🧠 Initializing Decision Precision Engine modules...")
        
        # Register available modules
        self.modules = {
            "surgery": "Surgical procedure planning and execution",
            "insurance": "Insurance coverage and authorization", 
            "logistics": "Resource scheduling and supply chain",
            "analytics": "Data analysis and reporting",
            "education": "Medical education and training",
            "hospitality": "Patient experience and hospitality"
        }
        
        logger.info(f"✅ Initialized {len(self.modules)} application modules")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🏥 Starting Gastric ADCI Decision Precision Engine")
    
    # Initialize decision engine
    engine = DecisionPrecisionEngine()
    await engine.initialize_modules()
    
    # Store engine in app state
    app.state.decision_engine = engine
    
    yield
    
    logger.info("🛑 Shutting down Decision Precision Engine")

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="Gastric ADCI Platform - Decision Precision Engine",
        version="2.0.0",
        description="Advanced Decision Confidence Index Platform with modular architecture",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Add middleware
    setup_middleware(app)
    
    # Mount static files if they exist
    static_path = Path("web/static")
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    # Setup routes
    setup_routes(app)
    
    return app

def setup_middleware(app: FastAPI):
    """Configure application middleware"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = asyncio.get_event_loop().time()
        response = await call_next(request)
        process_time = asyncio.get_event_loop().time() - start_time
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        return response

def setup_routes(app: FastAPI):
    """Setup application routes"""
    
    # Include web UI router (Surgify frontend)
    app.include_router(web_router)
    
    # Include general purpose API routes 
    app.include_router(api_v1_router, prefix="/api/v1", tags=["General API"])
    
    # Include specific business system modules
    from modules.surgery.router import router as surgery_router
    from modules.insurance.router import router as insurance_router
    from modules.logistics.router import router as logistics_router
    from modules.analytics.router import router as analytics_router
    from modules.education.router import router as education_router
    from modules.hospitality.router import router as hospitality_router
    
    app.include_router(surgery_router, prefix="/modules/surgery", tags=["Surgery System"])
    app.include_router(insurance_router, prefix="/modules/insurance", tags=["Insurance System"])
    app.include_router(logistics_router, prefix="/modules/logistics", tags=["Logistics System"])
    app.include_router(analytics_router, prefix="/modules/analytics", tags=["Analytics System"])
    app.include_router(education_router, prefix="/modules/education", tags=["Education System"])
    app.include_router(hospitality_router, prefix="/modules/hospitality", tags=["Hospitality System"])
    
    # Core API endpoints
    @app.get("/api/v1/")
    async def api_root():
        """API root endpoint"""
        return JSONResponse({
            "message": "Gastric ADCI Decision Precision Engine API v1",
            "version": "2.0.0",
            "general_api": {
                "auth": "/api/v1/auth",
                "entities": "/api/v1/entities",
                "concepts": "/api/v1/concepts",
                "knowledge": "/api/v1/knowledge",
                "reporter": "/api/v1/reporter"
            },
            "business_modules": {
                "surgery": "/modules/surgery",
                "insurance": "/modules/insurance", 
                "logistics": "/modules/logistics",
                "analytics": "/modules/analytics",
                "education": "/modules/education",
                "hospitality": "/modules/hospitality"
            },
            "ui": "/",
            "docs": "/docs"
        })
    
    @app.get("/health")
    async def health_check():
        """System health check"""
        return JSONResponse({
            "status": "healthy",
            "version": "2.0.0",
            "timestamp": asyncio.get_event_loop().time(),
            "api_modules": ["auth", "entities", "concepts", "knowledge", "reporter"],
            "business_modules": ["surgery", "insurance", "logistics", "analytics", "education", "hospitality"],
            "decision_engine": "operational"
        })
    
    @app.get("/")
    async def root():
        """Root endpoint - redirect to Surgify UI"""
        return JSONResponse({
            "message": "Gastric ADCI Decision Precision Engine",
            "version": "2.0.0",
            "platform": "Surgify",
            "api_modules": 5,
            "business_modules": 6,
            "ui": "Active",
            "docs": "/docs"
        })

    # Module status endpoints
    @app.get("/api/v1/modules/status")
    async def modules_status():
        """Get status of all modules"""
        engine = app.state.decision_engine
        return JSONResponse({
            "api_modules": {
                "auth": {"status": "active", "endpoint": "/api/v1/auth"},
                "entities": {"status": "active", "endpoint": "/api/v1/entities"},
                "concepts": {"status": "active", "endpoint": "/api/v1/concepts"},
                "knowledge": {"status": "active", "endpoint": "/api/v1/knowledge"},
                "reporter": {"status": "active", "endpoint": "/api/v1/reporter"}
            },
            "business_modules": {
                module: {"status": "active", "endpoint": f"/modules/{module}", "description": desc}
                for module, desc in engine.modules.items()
            },
            "total_api_modules": 5,
            "total_business_modules": len(engine.modules),
            "decision_engine": "operational"
        })

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler"""
        logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Create application instance
app = create_app()

def main():
    """Main entry point"""
    try:
        settings = get_settings()
    except:
        # Fallback settings if config not available
        settings = type('Settings', (), {
            'host': os.getenv("HOST", "0.0.0.0"),
            'port': int(os.getenv("PORT", "8000")),
            'debug': os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
        })()
    
    logger.info(f"🚀 Starting Gastric ADCI Decision Precision Engine")
    logger.info(f"🎨 Surgify UI: http://{settings.host}:{settings.port}")
    logger.info(f"📚 API docs: http://{settings.host}:{settings.port}/docs")
    logger.info(f"🔧 General API: 5 modules (auth, entities, concepts, knowledge, reporter)")
    logger.info(f"🏗️  Business Systems: 6 modules (surgery, insurance, logistics, analytics, education, hospitality)")
    logger.info(f"🔐 Security: WebAuthn + P2P ready")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )

if __name__ == "__main__":
    main()
