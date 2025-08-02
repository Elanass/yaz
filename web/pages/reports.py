"""
Reports pages for the Gastric ADCI Platform
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from core.dependencies import optional_user

router = APIRouter(prefix="/reports")
templates = Jinja2Templates(directory="web/templates")

@router.get("/")
async def reports_home(request: Request, current_user = Depends(optional_user)):
    """Reports home page"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reports - Surgify</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
            <div class="max-w-7xl mx-auto">
                <div class="mb-8">
                    <h1 class="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
                    <p class="mt-2 text-gray-600">Generate surgical reports and view analytics</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900">Surgical Outcomes</h3>
                            <p class="mt-2 text-gray-600">Analysis of surgical outcomes and complications</p>
                            <a href="#" class="mt-4 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200">
                                View Report
                            </a>
                        </div>
                    </div>
                    
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900">Performance Metrics</h3>
                            <p class="mt-2 text-gray-600">Key performance indicators and trends</p>
                            <a href="#" class="mt-4 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200">
                                View Metrics
                            </a>
                        </div>
                    </div>
                    
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900">Quality Assurance</h3>
                            <p class="mt-2 text-gray-600">Quality metrics and improvement recommendations</p>
                            <a href="#" class="mt-4 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200">
                                View QA Report
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
