"""
Web Router for YAZ Surgery Analytics Platform

Surgify template integration with backend logic
"""

import os
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Core page routers
from .pages import home, dashboard, auth

# Get the current directory
current_dir = Path(__file__).parent

# Templates
templates = Jinja2Templates(directory=str(current_dir / "templates"))

# Create main web router
web_router = APIRouter(tags=["Web Interface"])

# Static files with efficient caching - conditional mounting
static_dir = current_dir / "static"
if static_dir.exists():
    web_router.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Core routes with Surgify templates
web_router.include_router(home.router, prefix="", tags=["Home"])
web_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
web_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])


# Health check for web interface
@web_router.get("/web-health", response_class=HTMLResponse)
async def web_health():
    """Web interface health check"""
    return HTMLResponse(
        content="<h1>Web Interface OK - Surgify Ready</h1>", status_code=200
    )


# Component demo page
@web_router.get("/demo-components", response_class=HTMLResponse)
async def demo_components(request: Request):
    """Component library demonstration page"""
    return templates.TemplateResponse("demo_components.html", {"request": request})
