"""
Education pages for the Gastric ADCI Platform
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from core.dependencies import optional_user

router = APIRouter(prefix="/education")
templates = Jinja2Templates(directory="web/templates")

@router.get("/")
async def education_home(request: Request, current_user = Depends(optional_user)):
    """Education home page"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Education - Surgify</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
            <div class="max-w-7xl mx-auto">
                <div class="mb-8">
                    <h1 class="text-3xl font-bold text-gray-900">Education Center</h1>
                    <p class="mt-2 text-gray-600">Learn about surgical procedures and best practices</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900">Surgical Techniques</h3>
                            <p class="mt-2 text-gray-600">Learn advanced surgical techniques and procedures</p>
                            <a href="#" class="mt-4 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200">
                                Learn More
                            </a>
                        </div>
                    </div>
                    
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900">Case Studies</h3>
                            <p class="mt-2 text-gray-600">Review real-world surgical case studies</p>
                            <a href="#" class="mt-4 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200">
                                View Cases
                            </a>
                        </div>
                    </div>
                    
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900">Guidelines</h3>
                            <p class="mt-2 text-gray-600">Access clinical guidelines and protocols</p>
                            <a href="#" class="mt-4 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200">
                                View Guidelines
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
