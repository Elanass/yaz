#!/usr/bin/env python3
"""
Decision Precision in Surgery - Gastric ADCI Platform
Streamlined FastAPI application for surgical decision support
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from core.config.settings import settings
from core.models.base import HealthStatus

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Decision Precision Platform")
    
    # Initialize database
    try:
        from data.database import init_database
        await init_database()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    yield
    
    logger.info("🛑 Shutting down platform")


# Create FastAPI app
app = FastAPI(
    title="Decision Precision in Surgery",
    description="Surgical decision support platform with ADCI framework",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# API routes
from api.v1 import router as api_router
app.include_router(api_router, prefix="/api/v1")

# Static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API"""
    return RedirectResponse(url="/api/v1/")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return HealthStatus(
        status="healthy",
        version="1.0.0",
        database_connected=True,
        api_available=True,
        environment=settings.environment
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
