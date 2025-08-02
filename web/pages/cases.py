"""
Case management pages for the Gastric ADCI Platform
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from core.dependencies import optional_user

router = APIRouter(prefix="/cases")
templates = Jinja2Templates(directory="web/templates")

@router.get("/")
async def list_cases(request: Request, current_user = Depends(optional_user)):
    """Cases list page"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cases - Surgify</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
            <div class="max-w-7xl mx-auto">
                <div class="mb-8">
                    <h1 class="text-3xl font-bold text-gray-900">Cases</h1>
                    <p class="mt-2 text-gray-600">Manage surgical cases and patient data</p>
                </div>
                
                <div class="bg-white shadow overflow-hidden sm:rounded-md">
                    <div class="px-4 py-5 sm:p-6">
                        <h2 class="text-lg font-medium text-gray-900 mb-4">Recent Cases</h2>
                        <div class="text-center py-12">
                            <p class="text-gray-500">No cases found. Add your first case to get started.</p>
                            <a href="/cases/add" class="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
                                Add New Case
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

@router.get("/add")
async def add_case_page(request: Request, current_user = Depends(optional_user)):
    """Add new case page"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Case - Surgify</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
            <div class="max-w-2xl mx-auto">
                <div class="mb-8">
                    <h1 class="text-3xl font-bold text-gray-900">Add New Case</h1>
                    <p class="mt-2 text-gray-600">Enter patient and surgical information</p>
                </div>
                
                <div class="bg-white shadow sm:rounded-lg">
                    <div class="px-4 py-5 sm:p-6">
                        <form method="POST" action="/cases/add" class="space-y-6">
                            <div>
                                <label for="patient_id" class="block text-sm font-medium text-gray-700">Patient ID</label>
                                <input type="text" name="patient_id" id="patient_id" required
                                       class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                            </div>
                            
                            <div>
                                <label for="surgery_type" class="block text-sm font-medium text-gray-700">Surgery Type</label>
                                <select name="surgery_type" id="surgery_type" required
                                        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                                    <option value="">Select surgery type</option>
                                    <option value="gastrectomy">Gastrectomy</option>
                                    <option value="distal_gastrectomy">Distal Gastrectomy</option>
                                    <option value="total_gastrectomy">Total Gastrectomy</option>
                                </select>
                            </div>
                            
                            <div>
                                <label for="notes" class="block text-sm font-medium text-gray-700">Notes</label>
                                <textarea name="notes" id="notes" rows="4"
                                          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"></textarea>
                            </div>
                            
                            <div class="flex justify-end space-x-3">
                                <a href="/cases" class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                                    Cancel
                                </a>
                                <button type="submit" class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
                                    Save Case
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
