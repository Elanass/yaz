"""
Web Router for YAZ Surgery Analytics Platform

Surgify template integration with backend logic
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Core page routers
from .pages import home, dashboard, auth

# Templates
templates = Jinja2Templates(directory="web/templates")

# Create main web router
web_router = APIRouter(tags=["Web Interface"])

# Static files with efficient caching
web_router.mount("/static", StaticFiles(directory="web/static"), name="static")

# Core routes with Surgify templates
web_router.include_router(home.router, prefix="", tags=["Home"])
web_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
web_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Health check for web interface
@web_router.get("/health", response_class=HTMLResponse)
async def web_health():
    """Web interface health check"""
    return HTMLResponse(
        content="<h1>Web Interface OK - Surgify Ready</h1>",
        status_code=200
    )
