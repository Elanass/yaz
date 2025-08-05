"""
Dashboard Page Routes

Clinical workstation and analytics dashboard using templates
"""

from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from flask import render_template

router = APIRouter()

# Get the correct templates directory
current_dir = Path(__file__).parent.parent
templates_dir = current_dir / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard overview"""
    return templates.TemplateResponse(
        "dashboard/overview.html",
        {"request": request, "page_title": "Clinical Dashboard"},
    )


@router.get("/clinical", response_class=HTMLResponse)
async def clinical_workstation(request: Request):
    """Clinical workstation for surgeons"""
    return templates.TemplateResponse(
        "workstation.html", {"request": request, "page_title": "Clinical Workstation"}
    )


@router.get("/cases", response_class=HTMLResponse)
async def cases_dashboard(request: Request):
    """Cases management dashboard"""
    return templates.TemplateResponse(
        "dashboard/cases.html", {"request": request, "page_title": "Cases Management"}
    )


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_dashboard(request: Request):
    """Analytics and reporting dashboard"""
    return templates.TemplateResponse(
        "dashboard/analytics.html",
        {"request": request, "page_title": "Analytics Dashboard"},
    )


def dashboard_page():
    return render_template("dashboard.html")
