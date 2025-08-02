"""
Hospitality pages for the Gastric ADCI Platform
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from core.dependencies import optional_user

router = APIRouter(prefix="/hospitality")
templates = Jinja2Templates(directory="web/templates")

@router.get("/")
async def hospitality_home(request: Request, current_user = Depends(optional_user)):
    """Hospitality home page"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hospitality - Surgify</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
            <div class="max-w-7xl mx-auto">
                <div class="mb-8">
                    <h1 class="text-3xl font-bold text-gray-900">Hospitality Services</h1>
                    <p class="mt-2 text-gray-600">Patient care and support services</p>
                </div>
                
                <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                    <div class="px-4 py-5 sm:p-6">
                        <h2 class="text-lg font-medium text-gray-900 mb-4">Patient Services</h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <h3 class="text-md font-medium text-gray-900">Pre-operative Care</h3>
                                <p class="text-gray-600">Comprehensive pre-surgical preparation and patient education</p>
                            </div>
                            <div>
                                <h3 class="text-md font-medium text-gray-900">Post-operative Support</h3>
                                <p class="text-gray-600">Recovery monitoring and follow-up care coordination</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
