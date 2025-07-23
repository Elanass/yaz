#!/usr/bin/env python3
"""
Gastric ADCI Oncology-Surgery Decision Support Platform
Main application entry point
"""

import os
import uvicorn
from backend.src.main import create_app

def main():
    """Main application entry point"""
    # Create the FastAPI application
    app = create_app()
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    # Configure uvicorn
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        reload=debug,
        reload_dirs=["backend", "frontend"] if debug else None,
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
