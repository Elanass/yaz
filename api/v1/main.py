"""
Main API Router for Decision Precision in Surgery - Gastric ADCI FLOT Impact
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_404_NOT_FOUND

from core.config.platform_config import config
from core.dependencies import get_current_user

from .cases import router as cases_router
from .analysis import router as analysis_router
from .auth import router as auth_router
from .decisions import router as decisions_router
from .decisions_adci import router as adci_router
from .surgery import router as surgery_router
from .dashboard import router as dashboard_router

# API Router with better documentation
api_router = APIRouter(
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal server error"},
    },
)

# Initialize templates
templates = Jinja2Templates(directory="web/templates")

# Add request context processor to inject global template variables
@templates.context_processor
async def template_context(request: Request):
    """Inject global template variables into all templates"""
    return {
        "app_name": config.pwa_name,
        "app_version": config.api_version,
        "environment": config.environment,
        "is_production": config.is_production,
        "is_development": config.is_development,
    }

# Web routes for the Progressive Web App
# Root route for the web app
@api_router.get("/", response_class=HTMLResponse)
async def web_app_root(request: Request):
    """Serve the main web app interface"""
    return templates.TemplateResponse("index.html", {"request": request})

# Settings page route
@api_router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Serve the user settings page"""
    return templates.TemplateResponse("settings.html", {"request": request})

# Workstation page route
@api_router.get("/workstation", response_class=HTMLResponse)
async def workstation_page(request: Request):
    """Serve the workstation page"""
    return templates.TemplateResponse("workstation.html", {"request": request})

# Add case page route
@api_router.get("/add-case", response_class=HTMLResponse)
async def add_case_page(request: Request):
    """Serve the add case page"""
    return templates.TemplateResponse("add_case.html", {"request": request})

# Marketplace page route
@api_router.get("/marketplace", response_class=HTMLResponse)
async def marketplace_page(request: Request):
    """Serve the marketplace page"""
    return templates.TemplateResponse("marketplace.html", {"request": request})

# Include essential routers with better organization and proper tagging
api_router.include_router(
    cases_router, 
    prefix="/cases", 
    tags=["cases"],
    responses={404: {"description": "Case not found"}},
)

api_router.include_router(
    analysis_router, 
    prefix="/analysis", 
    tags=["analysis"],
)

api_router.include_router(
    auth_router, 
    prefix="/auth", 
    tags=["auth"],
)

api_router.include_router(
    decisions_router, 
    prefix="/decisions", 
    tags=["decisions"],
)

api_router.include_router(
    adci_router, 
    prefix="/decisions/adci", 
    tags=["adci"],
)

api_router.include_router(
    surgery_router, 
    prefix="/surgery", 
    tags=["surgery"],
)

api_router.include_router(
    dashboard_router, 
    prefix="/dashboard",
    tags=["dashboard"],
)

# Handle 404 for pages that don't exist
@api_router.get("/{path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, path: str):
    """Catch-all route to handle 404 errors with a proper template"""
    try:
        # First try to serve the requested path as a template
        return templates.TemplateResponse(f"{path}.html", {"request": request})
    except Exception:
        # If template doesn't exist, return 404 page
        return templates.TemplateResponse(
            "404.html", 
            {"request": request, "path": path}, 
            status_code=HTTP_404_NOT_FOUND
        )
