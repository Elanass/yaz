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
    """Home page"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except:
        # Fallback HTML response
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Surgify - Gastric ADCI Platform</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-50">
            <div class="min-h-screen flex items-center justify-center">
                <div class="max-w-md w-full text-center">
                    <h1 class="text-4xl font-bold text-gray-900 mb-4">
                        Welcome to Surgify
                    </h1>
                    <p class="text-lg text-gray-600 mb-8">
                        Advanced Decision Support for Surgical Excellence
                    </p>
                    <div class="space-x-4">
                        <a href="/auth/login" class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
                            Login
                        </a>
                        <a href="/auth/register" class="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700">
                            Register
                        </a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

@router.get("/dashboard")
async def dashboard(request: Request):
    """Dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})
