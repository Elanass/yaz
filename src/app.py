#!/usr/bin/env python3
"""
Multi-Domain Application Entry Point
Demonstrates how to use Surgify, Insurance, and Logistics domains together
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
os.environ["PYTHONPATH"] = str(src_path)

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from insure.api.router import router as insurance_router
from move.api.router import router as logistics_router

# Import domain routers
from surgify.main import app as surgify_app

# Create multi-domain application
app = FastAPI(
    title="Multi-Domain Healthcare Platform",
    description="Integrated platform with Surgery, Insurance, and Logistics domains",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount domain applications
app.mount("/surgify", surgify_app)

# Include domain routers
app.include_router(insurance_router, prefix="/insurance", tags=["Insurance"])
app.include_router(logistics_router, prefix="/logistics", tags=["Logistics"])


@app.get("/")
async def root():
    """Root endpoint showing all available domains"""
    return {
        "application": "Multi-Domain Healthcare Platform",
        "version": "1.0.0",
        "description": "Integrated platform with modular domains",
        "domains": {
            "surgify": {
                "description": "Surgery analytics and decision support",
                "endpoint": "/surgify",
                "docs": "/surgify/docs",
            },
            "insurance": {
                "description": "Insurance claims and policy management",
                "endpoint": "/insurance",
                "status": "available",
            },
            "logistics": {
                "description": "Resource optimization and workflow analysis",
                "endpoint": "/logistics",
                "status": "available",
            },
        },
        "features": [
            "Modular domain architecture",
            "Cross-domain data sharing",
            "Reusable domain tools",
            "Independent scaling",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "domains": {
            "surgify": "operational",
            "insurance": "operational",
            "logistics": "operational",
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if app.debug else "An error occurred",
        },
    )


def main():
    """Run the multi-domain application"""
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level="info")


if __name__ == "__main__":
    main()
