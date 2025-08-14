"""
Base Application Factory
Standard FastAPI app creation for all YAZ applications
"""

from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import List, Optional

from .config import get_app_config
from .logging import setup_logging, get_logger
from .database import init_database
from .models import HealthCheck, ErrorResponse


def create_base_app(
    app_name: str,
    routers: Optional[List[APIRouter]] = None,
    static_dir: Optional[str] = None
) -> FastAPI:
    """
    Create a standardized FastAPI application
    
    Args:
        app_name: Application name
        routers: List of APIRouter instances to include
        static_dir: Static files directory (optional)
    
    Returns:
        Configured FastAPI application
    """
    
    # Setup logging
    setup_logging(app_name)
    logger = get_logger(app_name)
    
    # Get configuration
    config = get_app_config(app_name)
    
    # Create FastAPI app
    app = FastAPI(
        title=f"YAZ {app_name.title()}",
        version=config["version"],
        debug=config["debug"]
    )
    
    # Initialize database
    init_database()
    
    # Health check endpoint
    @app.get("/health", response_model=HealthCheck)
    async def health_check():
        """Health check endpoint"""
        return HealthCheck()
    
    # Error handler
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Internal server error").dict()
        )
    
    # Include routers
    if routers:
        for router in routers:
            app.include_router(router)
    
    # Static files
    if static_dir and Path(static_dir).exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    logger.info(f"{app_name} application created successfully")
    return app
