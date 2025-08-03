"""
Authentication Page Routes

Clean authentication flow using templates
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "page_title": "Sign In"
    })

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "page_title": "Create Account"
    })

@router.post("/login")
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login submission"""
    # TODO: Implement authentication logic
    return RedirectResponse(url="/dashboard", status_code=302)

@router.get("/logout")
async def logout(request: Request):
    """Handle logout"""
    return RedirectResponse(url="/", status_code=302)
