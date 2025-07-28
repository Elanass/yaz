#!/usr/bin/env python3
"""
Gastric ADCI Platform - Main Entry Point
Clean, DRY, MVP-focused implementation
"""

import os
import uvicorn
from app import create_app
from core.config.settings import ApplicationConfig, DatabaseConfig, SecurityConfig
from features.decisions.service import DecisionService
from api.v1 import api_router
from web.components.layout import create_base_layout
from web.components.pwa import create_pwa_manifest
from web.components.clinical_platform import (
    create_adaptive_decision_component,
    create_simulation_component,
    create_evidence_synthesis_component,
    create_clinical_dashboard
)
from services.event_correlation.service import start_background_processing


def main():
    """Main application entry point"""
    # Load configurations
    app_config = ApplicationConfig()
    db_config = DatabaseConfig()
    security_config = SecurityConfig()

    # Create the FastAPI application
    app = create_app()

    # Register consolidated API router
    app.include_router(api_router, prefix="/api/v1")

    # Register web components
    app.mount("/web/layout", create_base_layout("Gastric ADCI Platform", content=None))
    app.mount("/web/pwa", create_pwa_manifest())

    # Start background services
    @app.on_event("startup")
    async def startup_event():
        """Start background services when app starts"""
        # Start event correlation background processing
        # This would be run as a separate task
        # For now, we'll just log that it would be started
        print("Starting event correlation background processing...")
        # In production, use:
        # import asyncio
        # asyncio.create_task(start_background_processing())

    # Get configuration from environment
    host = os.getenv("HOST", app_config.host)
    port = int(os.getenv("PORT", app_config.port))
    debug = app_config.debug

    # Configure uvicorn
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        reload=debug,
        reload_dirs=["core", "features", "api", "web", "services", "adapters"] if debug else None,
        log_level="info",
        access_log=True,
        server_header=False,  # Security: hide server info
        date_header=False,    # Security: hide date info
    )

    # Start the server
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    main()
