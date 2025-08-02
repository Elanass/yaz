"""
Authentication pages for the Gastric ADCI Platform
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any

from core.dependencies import get_current_user, optional_user

router = APIRouter(prefix="/auth")
templates = Jinja2Templates(directory="web/templates")

@router.get("/login")
async def login_page(request: Request, next: Optional[str] = None, current_user = Depends(optional_user)):
    """Login page"""
    
    # Redirect if already logged in
    if current_user:
        return RedirectResponse(url=next or "/", status_code=303)
    
    # Create a simple login page HTML directly for now
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - Surgify</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div class="max-w-md w-full space-y-8">
                <div>
                    <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Sign in to your account
                    </h2>
                </div>
                <form class="mt-8 space-y-6" method="POST" action="/auth/login">
                    <div>
                        <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
                        <input id="email" name="email" type="email" required 
                               class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                    </div>
                    <div>
                        <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
                        <input id="password" name="password" type="password" required 
                               class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                    </div>
                    <div>
                        <button type="submit" 
                                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            Sign in
                        </button>
                    </div>
                    <div class="text-center">
                        <a href="/auth/register" class="font-medium text-blue-600 hover:text-blue-500">
                            Don't have an account? Register
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post("/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: Optional[str] = Form(None)
):
    """Process login form"""
    
    # Simple demo authentication - accept any email/password
    if email and password:
        response = RedirectResponse(url=next or "/dashboard", status_code=303)
        response.set_cookie("access_token", f"demo_token_{email}", httponly=True)
        return response
    else:
        return RedirectResponse(url="/auth/login?error=invalid", status_code=303)

@router.get("/register")
async def register_page(request: Request, current_user = Depends(optional_user)):
    """Registration page"""
    
    # Redirect if already logged in
    if current_user:
        return RedirectResponse(url="/", status_code=303)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - Surgify</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div class="max-w-md w-full space-y-8">
                <div>
                    <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Create your account
                    </h2>
                </div>
                <form class="mt-8 space-y-6" method="POST" action="/auth/register">
                    <div>
                        <label for="name" class="block text-sm font-medium text-gray-700">Full Name</label>
                        <input id="name" name="name" type="text" required 
                               class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                    </div>
                    <div>
                        <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
                        <input id="email" name="email" type="email" required 
                               class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                    </div>
                    <div>
                        <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
                        <input id="password" name="password" type="password" required 
                               class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                    </div>
                    <div>
                        <label for="confirm_password" class="block text-sm font-medium text-gray-700">Confirm Password</label>
                        <input id="confirm_password" name="confirm_password" type="password" required 
                               class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                    </div>
                    <div>
                        <button type="submit" 
                                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            Create Account
                        </button>
                    </div>
                    <div class="text-center">
                        <a href="/auth/login" class="font-medium text-blue-600 hover:text-blue-500">
                            Already have an account? Sign in
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post("/register")
async def register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Process registration form"""
    
    if password != confirm_password:
        return RedirectResponse(url="/auth/register?error=password_mismatch", status_code=303)
    
    # Simple demo registration
    return RedirectResponse(url="/auth/login?registered=1", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    """Logout user"""
    
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response
