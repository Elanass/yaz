"""
Home page router for Gastric ADCI Platform
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

@router.get("/")
async def home(request: Request):
    """Home page - Surgify template"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "page_title": "Surgify - Advanced Decision Support for Surgical Excellence"
    })

@router.get("/dashboard")
async def dashboard(request: Request):
    """Dashboard page - redirect to workstation"""
    return templates.TemplateResponse("workstation.html", {"request": request})

@router.get("/test")
async def test_page(request: Request):
    """Test page for DRY compliance validation"""
    return HTMLResponse(content=open("web/static/test.html").read())
