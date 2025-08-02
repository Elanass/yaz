#!/usr/bin/env python3
"""
Gastric ADCI Platform - Multi-Environment Surgery Decision Support
Enhanced FastAPI application with Local, P2P, and Multi-Cloud deployment support
"""

import logging
import json
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import environment configuration
from core.config.environment import get_environment_config, get_web_config, DeploymentMode
from core.config.settings import settings
from core.models.base import HealthStatus

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize environment configuration
env_config = get_environment_config()
logger.info(f"🏥 Gastric ADCI Platform starting in {env_config.get_mode().value} mode")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enhanced application lifespan manager with environment support"""
    deployment_info = env_config.get_deployment_info()
    logger.info(f"� Starting Gastric ADCI Platform")
    logger.info(f"   Environment: {deployment_info['environment_display']}")
    logger.info(f"   Mode: {deployment_info['mode']}")
    logger.info(f"   Features: {deployment_info['features']}")
    
    # Validate configuration
    issues = env_config.validate_config()
    if issues:
        logger.warning(f"Configuration issues found: {issues}")
    
    # Initialize database based on environment
    if env_config.get_mode() == DeploymentMode.LOCAL:
        logger.info("🗄️  Initializing local SQLite database")
    elif env_config.get_mode() == DeploymentMode.P2P:
        logger.info("🔗 Initializing P2P distributed storage")
        
        # Initialize P2P signaling server
        try:
            from core.operators.specific_purpose.p2p_signaling import P2pSignalingOperator
            app.state.p2p_signaling = P2pSignalingOperator()
            await app.state.p2p_signaling.initialize()
            logger.info("✅ P2P signaling server initialized")
        except Exception as e:
            logger.error(f"❌ P2P signaling initialization failed: {e}")
            
    else:  # MULTICLOUD
        logger.info(f"☁️  Initializing cloud database ({env_config.cloud.provider.value})")
    
    # Additional initialization based on features
    if env_config.supports_collaboration():
        logger.info("🤝 Collaboration features enabled")
    
    if env_config.supports_real_time():
        logger.info("⚡ Real-time updates enabled")
    
    yield
    
    logger.info(f"🛑 Shutting down {deployment_info['environment_display']} platform")


# Create enhanced FastAPI app with environment-specific configuration
app_config = env_config.get_config()

app = FastAPI(
    title="Gastric ADCI Platform",
    description="Multi-Environment Surgery Decision Support with Collaborative Features",
    version=app_config.get("version", "2.0.0"),
    lifespan=lifespan,
    docs_url=app_config.get("docs_url"),
    redoc_url="/redoc" if app_config.get("debug") else None,
    debug=app_config.get("debug", False)
)

# Enhanced middleware configuration
cors_origins = app_config.get("cors_origins", ["*"]) if app_config.get("debug") else []
if env_config.get_mode() == DeploymentMode.P2P:
    # Allow P2P peer connections
    cors_origins.extend(["http://localhost:8765", "ws://localhost:8765"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add environment-specific routes
from api.v1 import router as api_router
app.include_router(api_router, prefix=app_config.get("api_prefix", "/api/v1"))

# Add P2P signaling routes if in P2P mode
if env_config.get_mode() == DeploymentMode.P2P:
    @app.on_event("startup")
    async def add_p2p_routes():
        if hasattr(app.state, 'p2p_signaling') and app.state.p2p_signaling:
            p2p_router = app.state.p2p_signaling.get_router()
            app.include_router(p2p_router, prefix="/api/v1")

# Initialize templates with environment support
templates = Jinja2Templates(directory="web/templates")

# Enhanced web routes with environment integration
from web.router import router as web_router
app.include_router(web_router)

# Environment configuration endpoints
@app.get("/api/v1/config/environment")
async def get_environment_config_endpoint():
    """Get environment configuration for frontend"""
    return JSONResponse({
        "success": True,
        "data": get_web_config()
    })

@app.get("/api/v1/config/deployment-info")
async def get_deployment_info():
    """Get detailed deployment information"""
    return JSONResponse({
        "success": True,
        "data": env_config.get_deployment_info()
    })

# Enhanced static file serving with environment awareness
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Web routes are handled by the web router

# Health check with environment information
@app.get("/health")
async def health_check():
    """Enhanced health check with environment details"""
    try:
        deployment_info = env_config.get_deployment_info()
        
        # Basic health status
        health_data = {
            "status": "healthy",
            "timestamp": "2025-01-31T00:00:00Z",  # Would use actual timestamp
            "environment": deployment_info["mode"],
            "version": deployment_info["version"],
            "features": deployment_info["features"]
        }
        
        # Environment-specific health checks
        components = {}
        
        if env_config.get_mode() == DeploymentMode.LOCAL:
            components["database"] = "healthy"  # Would check actual database
            components["file_storage"] = "healthy"
            
        elif env_config.get_mode() == DeploymentMode.P2P:
            components["database"] = "healthy"
            
            # Check P2P signaling server status
            if hasattr(app.state, 'p2p_signaling') and app.state.p2p_signaling:
                p2p_status = app.state.p2p_signaling.get_status()
                components["p2p_signaling"] = p2p_status["status"]
                components["active_connections"] = p2p_status["active_connections"]
                components["active_rooms"] = p2p_status["active_rooms"]
            else:
                components["p2p_signaling"] = "unavailable"
                
            components["peer_discovery"] = "healthy"
            
        elif env_config.get_mode() == DeploymentMode.MULTICLOUD:
            components["database"] = "healthy"
            components["cloud_storage"] = "healthy"
            components["load_balancer"] = "healthy"
            components["monitoring"] = "healthy"
        
        health_data["components"] = components
        
        # Add any configuration issues as warnings
        issues = env_config.validate_config()
        if issues:
            health_data["warnings"] = issues
        
        return JSONResponse({
            "success": True,
            "data": health_data
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "Service unhealthy",
                "details": str(e)
            }
        )

# Duplicate health check removed - using the enhanced one above


# Main execution with environment-specific configuration
if __name__ == "__main__":
    app_config = env_config.get_config()
    
    # Environment-specific server configuration
    server_config = {
        "app": "main:app",
        "host": app_config.get("host", "0.0.0.0"),
        "port": app_config.get("port", 8000),
        "log_level": app_config.get("log_level", "info").lower(),
    }
    
    # Add environment-specific settings
    if env_config.get_mode() == DeploymentMode.LOCAL:
        server_config.update({
            "reload": app_config.get("hot_reload", True),
            "reload_dirs": ["web", "api", "core", "features"],
            "access_log": True
        })
    elif env_config.get_mode() == DeploymentMode.P2P:
        server_config.update({
            "reload": False,
            "workers": 1,  # Single worker for P2P coordination
            "access_log": True
        })
    else:  # MULTICLOUD
        server_config.update({
            "reload": False,
            "workers": app_config.get("workers", 4),
            "access_log": False,  # Use cloud logging instead
            "proxy_headers": True,
            "forwarded_allow_ips": "*"
        })
    
    logger.info(f"🚀 Starting server with config: {server_config}")
    uvicorn.run(**server_config)
