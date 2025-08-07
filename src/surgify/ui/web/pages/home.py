"""
Home Page Routes - Surgify Integration

Clean, minimal home page with existing Surgify templates
"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

# Get the correct templates directory
current_dir = Path(__file__).parent.parent
templates_dir = current_dir / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main landing page - Surgify template"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "page_title": "Surgify - Advanced Decision Support"},
    )


@router.get("/surgify", response_class=HTMLResponse)
async def surgify_app(request: Request):
    """Surgify clinical research interface - Main UI"""
    # Temporarily use debug template to isolate template issues
    return templates.TemplateResponse("debug.html", {"request": request})


@router.get("/surgify-full", response_class=HTMLResponse)
async def surgify_app_full(request: Request):
    """Surgify clinical research interface - Full UI"""

    # Sample data for the Surgify template
    context = {
        "request": request,
        "featured_series": [
            {
                "id": 1,
                "title": "Advanced Gastric Surgery Techniques",
                "author": "Dr. Smith",
                "image_url": "/static/images/surgery-1.svg",
            },
            {
                "id": 2,
                "title": "Minimally Invasive Procedures",
                "author": "Dr. Johnson",
                "image_url": "/static/images/surgery-2.svg",
            },
        ],
        "upcoming_events": [
            {
                "id": 1,
                "title": "International Gastric Surgery Symposium",
                "date": "Aug 15, 2025",
                "image_url": "/static/images/event-1.svg",
            }
        ],
        "journal_articles": [
            {
                "id": 1,
                "title": "Novel Approaches in Gastric Cancer Treatment",
                "author": "Dr. Wilson",
                "image_url": "/static/images/surgery-1.svg",
            },
            {
                "id": 2,
                "title": "Post-operative Care Protocols",
                "author": "Dr. Brown",
                "image_url": "/static/images/surgery-2.svg",
            },
        ],
    }

    return templates.TemplateResponse("surgify.html", context)


@router.get("/workstation", response_class=HTMLResponse)
async def workstation(request: Request):
    """Clinical workstation entry point"""
    return templates.TemplateResponse(
        "workstation.html", {"request": request, "page_title": "Clinical Workstation"}
    )


@router.get("/get-app", response_class=HTMLResponse)
async def get_app(request: Request):
    """Get App page - Download mobile apps"""
    return templates.TemplateResponse(
        "get-app.html", {"request": request, "page_title": "Get Surgify - Mobile Apps"}
    )
