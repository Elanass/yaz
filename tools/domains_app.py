#!/usr/bin/env python3
"""
Simple Multi-Domain Application Entry Point
Demonstrates clean domain separation: Surgify, Insurance (Insure), and Logistics (Move)
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import domain routers
from insure.api.router import router as insurance_router
from move.api.router import router as logistics_router

# Create multi-domain application
app = FastAPI(
    title="Multi-Domain Healthcare Platform",
    description="Modular platform with Surgery, Insurance, and Logistics domains",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include domain routers (each domain is independent and reusable)
app.include_router(insurance_router, prefix="/api/v1", tags=["Insurance"])
app.include_router(logistics_router, prefix="/api/v1", tags=["Logistics"])

# Root endpoint demonstrating domain integration
@app.get("/")
async def root():
    """Root endpoint showing available domains"""
    return {
        "platform": "Multi-Domain Healthcare Platform",
        "version": "2.0.0",
        "architecture": "Modular Domain Separation",
        "domains": {
            "insurance": {
                "name": "Insure",
                "description": "Risk stratification, cost prediction, and claims optimization",
                "endpoints": "/insurance/*",
                "status": "active"
            },
            "logistics": {
                "name": "Move", 
                "description": "Resource optimization, workflow analysis, and supply chain management",
                "endpoints": "/logistics/*",
                "status": "active"
            },
            "surgery": {
                "name": "Surgify",
                "description": "Surgical planning, decision support, and outcome prediction",
                "endpoints": "/surgify/* (can be mounted separately)",
                "status": "modular"
            }
        },
        "modularity": "Each domain can be used independently or together",
        "reusability": "Insurance and logistics tools can be used by any domain"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "domains": ["insurance", "logistics"],
        "timestamp": "2025-08-06T10:00:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(
        "domains_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
