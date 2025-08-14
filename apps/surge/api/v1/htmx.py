"""
HTMX Endpoints for Surgery Platform
FastHTML + HTMX integration for the surgery healthcare PWA
"""

from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger("surge.htmx")

# Setup templates
templates_path = Path(__file__).parent.parent.parent / "ui" / "web" / "templates"
templates = Jinja2Templates(directory=str(templates_path)) if templates_path.exists() else None

router = APIRouter(prefix="/htmx", tags=["HTMX"])

# Mock data for development - replace with your actual services
MOCK_CASES = [
    {
        "id": "1",
        "patient_name": "John Doe",
        "procedure": "Laparoscopic Cholecystectomy",
        "surgeon": "Dr. Smith",
        "status": "scheduled",
        "scheduled_start_time": "2025-08-11 09:00",
        "room": "OR-1"
    },
    {
        "id": "2", 
        "patient_name": "Jane Smith",
        "procedure": "Appendectomy",
        "surgeon": "Dr. Johnson",
        "status": "intra_op",
        "scheduled_start_time": "2025-08-11 10:30",
        "room": "OR-2"
    }
]

MOCK_ROOMS = [
    {"id": "or-1", "name": "OR-1", "status": "available"},
    {"id": "or-2", "name": "OR-2", "status": "occupied"},
    {"id": "or-3", "name": "OR-3", "status": "cleaning"},
    {"id": "or-4", "name": "OR-4", "status": "maintenance"},
]

@router.get("/cases/list", response_class=HTMLResponse)
async def get_cases_list_partial(
    request: Request,
    search: str = Query("", description="Search term"),
    status: str = Query("", description="Case status filter"),
    procedure: str = Query("", description="Procedure filter")
):
    """HTMX partial for cases list with filters"""
    try:
        # Filter mock data based on parameters
        filtered_cases = MOCK_CASES
        
        if search:
            filtered_cases = [c for c in filtered_cases if 
                            search.lower() in c["patient_name"].lower() or 
                            search.lower() in c["procedure"].lower()]
        
        if status:
            filtered_cases = [c for c in filtered_cases if c["status"] == status]
            
        if procedure:
            filtered_cases = [c for c in filtered_cases if c["procedure"] == procedure]

        cases_html = ""
        for case in filtered_cases:
            status_color = {
                "scheduled": "blue",
                "pre_op": "yellow", 
                "intra_op": "green",
                "post_op": "purple",
                "completed": "gray"
            }.get(case["status"], "blue")
            
            cases_html += f"""
                <div class="card p-4 hover:shadow-md transition-shadow cursor-pointer"
                     hx-get="/api/v1/htmx/cases/{case['id']}/details"
                     hx-target="#case-details-modal"
                     hx-trigger="click">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="font-semibold text-lg">{case['procedure']}</h3>
                            <p class="text-sm text-gray-600">Patient: {case['patient_name']}</p>
                            <p class="text-sm text-gray-600">Surgeon: {case['surgeon']}</p>
                            <p class="text-sm text-gray-600">Room: {case['room']}</p>
                            <p class="text-sm text-gray-600">Scheduled: {case['scheduled_start_time']}</p>
                        </div>
                        <span class="px-3 py-1 text-sm rounded-full bg-{status_color}-100 text-{status_color}-800">
                            {case['status'].replace('_', ' ').title()}
                        </span>
                    </div>
                </div>
            """
        
        if not cases_html:
            cases_html = '<div class="text-center text-gray-500 py-8">No cases found</div>'
            
        return HTMLResponse(f'<div id="cases-list" class="space-y-4">{cases_html}</div>')
        
    except Exception as e:
        logger.error(f"Error in get_cases_list_partial: {e}")
        return HTMLResponse(f'<div class="error text-red-600">Error loading cases: {str(e)}</div>')

@router.get("/cases/new-form", response_class=HTMLResponse)
async def get_new_case_form(request: Request):
    """HTMX partial for new case form"""
    return HTMLResponse("""
        <div id="case-form-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg p-6 w-full max-w-2xl mx-4">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-semibold">New Surgical Case</h3>
                    <button onclick="document.getElementById('case-form-modal').remove()" 
                            class="text-gray-400 hover:text-gray-600 text-xl">×</button>
                </div>
                
                <form hx-post="/api/v1/htmx/cases/create" 
                      hx-target="#cases-list" 
                      hx-swap="outerHTML"
                      hx-on="htmx:afterRequest: document.getElementById('case-form-modal').remove()">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium mb-1">Patient Name</label>
                            <input type="text" name="patient_name" class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500" required>
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-1">Procedure</label>
                            <select name="procedure" class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500" required>
                                <option value="">Select Procedure</option>
                                <option value="Laparoscopic Cholecystectomy">Laparoscopic Cholecystectomy</option>
                                <option value="Appendectomy">Appendectomy</option>
                                <option value="Hernia Repair">Hernia Repair</option>
                                <option value="Gallbladder Surgery">Gallbladder Surgery</option>
                                <option value="Knee Arthroscopy">Knee Arthroscopy</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-1">Surgeon</label>
                            <select name="surgeon" class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500" required>
                                <option value="">Select Surgeon</option>
                                <option value="Dr. Smith">Dr. Smith</option>
                                <option value="Dr. Johnson">Dr. Johnson</option>
                                <option value="Dr. Williams">Dr. Williams</option>
                                <option value="Dr. Brown">Dr. Brown</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-1">Scheduled Date & Time</label>
                            <input type="datetime-local" name="scheduled_datetime" class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500" required>
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-1">Room</label>
                            <select name="room" class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500" required>
                                <option value="">Select Room</option>
                                <option value="OR-1">OR-1</option>
                                <option value="OR-2">OR-2</option>
                                <option value="OR-3">OR-3</option>
                                <option value="OR-4">OR-4</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-1">Priority</label>
                            <select name="priority" class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500">
                                <option value="routine">Routine</option>
                                <option value="urgent">Urgent</option>
                                <option value="emergency">Emergency</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <label class="block text-sm font-medium mb-1">Notes</label>
                        <textarea name="notes" rows="3" class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500" 
                                  placeholder="Additional notes or special instructions..."></textarea>
                    </div>
                    
                    <div class="flex justify-end space-x-3 mt-6">
                        <button type="button" onclick="document.getElementById('case-form-modal').remove()" 
                                class="px-4 py-2 text-gray-600 border rounded hover:bg-gray-50 transition-colors">
                            Cancel
                        </button>
                        <button type="submit" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
                            Create Case
                        </button>
                    </div>
                </form>
            </div>
        </div>
    """)

@router.post("/cases/create", response_class=HTMLResponse)
async def create_case_htmx(request: Request):
    """Create new case and return updated cases list"""
    try:
        form_data = await request.form()
        
        # In real implementation, save to database
        new_case = {
            "id": str(len(MOCK_CASES) + 1),
            "patient_name": form_data.get("patient_name"),
            "procedure": form_data.get("procedure"),
            "surgeon": form_data.get("surgeon"),
            "status": "scheduled",
            "scheduled_start_time": form_data.get("scheduled_datetime"),
            "room": form_data.get("room"),
            "priority": form_data.get("priority", "routine"),
            "notes": form_data.get("notes", "")
        }
        
        MOCK_CASES.append(new_case)
        
        # Return updated cases list
        return await get_cases_list_partial(request)
        
    except Exception as e:
        logger.error(f"Error creating case: {e}")
        return HTMLResponse(f'<div class="error text-red-600">Error creating case: {str(e)}</div>')

@router.get("/cases/today", response_class=HTMLResponse)
async def get_todays_cases(request: Request):
    """HTMX partial for today's cases"""
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    
    todays_cases = [c for c in MOCK_CASES if c["scheduled_start_time"].startswith(today)]
    
    if not todays_cases:
        return HTMLResponse('<div class="text-sm text-gray-500 text-center py-4">No cases scheduled for today</div>')
    
    cases_html = ""
    for case in todays_cases:
        status_color = {
            "scheduled": "blue", "intra_op": "green", "completed": "gray"
        }.get(case["status"], "blue")
        
        cases_html += f"""
            <div class="flex items-center justify-between p-3 border rounded hover:bg-gray-50 transition-colors">
                <div class="flex-1">
                    <div class="font-medium text-sm">{case['procedure']}</div>
                    <div class="text-xs text-gray-600">{case['patient_name']} • {case['surgeon']}</div>
                    <div class="text-xs text-gray-600">{case['room']}</div>
                </div>
                <div class="text-right">
                    <div class="text-xs font-medium">{case['scheduled_start_time'].split(' ')[1]}</div>
                    <span class="text-xs px-2 py-1 rounded bg-{status_color}-100 text-{status_color}-800">
                        {case['status'].replace('_', ' ').title()}
                    </span>
                </div>
            </div>
        """
    
    return HTMLResponse(f'<div class="space-y-2">{cases_html}</div>')

@router.get("/cases/{case_id}/details", response_class=HTMLResponse)
async def get_case_details_modal(case_id: str, request: Request):
    """HTMX partial for case details modal"""
    try:
        case = next((c for c in MOCK_CASES if c["id"] == case_id), None)
        if not case:
            return HTMLResponse('<div class="error">Case not found</div>')
        
        return HTMLResponse(f"""
            <div id="case-details-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
                    <div class="flex justify-between items-start mb-6">
                        <h3 class="text-xl font-semibold">Case Details: {case['procedure']}</h3>
                        <button onclick="document.getElementById('case-details-modal').remove()" 
                                class="text-gray-400 hover:text-gray-600 text-xl">×</button>
                    </div>
                    
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div class="space-y-6">
                            <div>
                                <h4 class="font-semibold mb-3 text-gray-900">Patient Information</h4>
                                <div class="bg-gray-50 p-4 rounded-lg space-y-2">
                                    <div><span class="text-gray-600 font-medium">Name:</span> {case['patient_name']}</div>
                                    <div><span class="text-gray-600 font-medium">MRN:</span> MRN-{case['id'].zfill(6)}</div>
                                    <div><span class="text-gray-600 font-medium">DOB:</span> 1985-03-15</div>
                                    <div><span class="text-gray-600 font-medium">Age:</span> 40 years</div>
                                </div>
                            </div>
                            
                            <div>
                                <h4 class="font-semibold mb-3 text-gray-900">Case Information</h4>
                                <div class="bg-gray-50 p-4 rounded-lg space-y-2">
                                    <div><span class="text-gray-600 font-medium">Procedure:</span> {case['procedure']}</div>
                                    <div><span class="text-gray-600 font-medium">Surgeon:</span> {case['surgeon']}</div>
                                    <div><span class="text-gray-600 font-medium">Room:</span> {case['room']}</div>
                                    <div><span class="text-gray-600 font-medium">Scheduled:</span> {case['scheduled_start_time']}</div>
                                    <div><span class="text-gray-600 font-medium">Priority:</span> 
                                        <span class="capitalize">{case.get('priority', 'routine')}</span>
                                    </div>
                                    <div><span class="text-gray-600 font-medium">Status:</span> 
                                        <span class="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">
                                            {case['status'].replace('_', ' ').title()}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="space-y-6">
                            <div>
                                <h4 class="font-semibold mb-3 text-gray-900">Pre-Op Checklist</h4>
                                <div class="bg-gray-50 p-4 rounded-lg">
                                    <div class="space-y-2">
                                        <label class="flex items-center">
                                            <input type="checkbox" class="mr-2" checked> Consent signed
                                        </label>
                                        <label class="flex items-center">
                                            <input type="checkbox" class="mr-2" checked> NPO confirmed
                                        </label>
                                        <label class="flex items-center">
                                            <input type="checkbox" class="mr-2"> Allergies reviewed
                                        </label>
                                        <label class="flex items-center">
                                            <input type="checkbox" class="mr-2"> Site marked
                                        </label>
                                        <label class="flex items-center">
                                            <input type="checkbox" class="mr-2"> Pre-op assessment complete
                                        </label>
                                    </div>
                                </div>
                            </div>
                            
                            <div>
                                <h4 class="font-semibold mb-3 text-gray-900">Quick Actions</h4>
                                <div class="space-y-2">
                                    <button class="w-full btn-secondary text-left px-4 py-2 bg-blue-50 border border-blue-200 rounded hover:bg-blue-100 transition-colors"
                                            hx-post="/api/v1/htmx/cases/{case['id']}/status"
                                            hx-vals='{{"status": "pre_op"}}'
                                            hx-target="#case-details-modal"
                                            hx-swap="outerHTML">
                                        Mark as Pre-Op
                                    </button>
                                    <button class="w-full btn-secondary text-left px-4 py-2 bg-green-50 border border-green-200 rounded hover:bg-green-100 transition-colors"
                                            hx-post="/api/v1/htmx/cases/{case['id']}/status"
                                            hx-vals='{{"status": "intra_op"}}'
                                            hx-target="#case-details-modal"
                                            hx-swap="outerHTML">
                                        Start Surgery
                                    </button>
                                    <button class="w-full btn-secondary text-left px-4 py-2 bg-purple-50 border border-purple-200 rounded hover:bg-purple-100 transition-colors"
                                            hx-post="/api/v1/htmx/cases/{case['id']}/status"
                                            hx-vals='{{"status": "post_op"}}'
                                            hx-target="#case-details-modal"
                                            hx-swap="outerHTML">
                                        Complete Surgery
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-6 pt-6 border-t flex justify-end">
                        <button onclick="document.getElementById('case-details-modal').remove()" 
                                class="px-6 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors">
                            Close
                        </button>
                    </div>
                </div>
            </div>
        """)
    except Exception as e:
        logger.error(f"Error getting case details: {e}")
        return HTMLResponse(f'<div class="error text-red-600">Error loading case details: {str(e)}</div>')

@router.get("/rooms/status", response_class=HTMLResponse)
async def get_room_status(request: Request):
    """HTMX partial for OR room status"""
    rooms_html = ""
    for room in MOCK_ROOMS:
        status_color = {
            "available": "green",
            "occupied": "blue", 
            "cleaning": "yellow",
            "maintenance": "red"
        }.get(room["status"], "gray")
        
        rooms_html += f"""
            <div class="flex items-center justify-between p-3 border rounded">
                <div class="font-medium">{room['name']}</div>
                <span class="px-2 py-1 text-xs rounded bg-{status_color}-100 text-{status_color}-800 capitalize">
                    {room['status']}
                </span>
            </div>
        """
    
    return HTMLResponse(f'<div class="space-y-2">{rooms_html}</div>')

@router.get("/or-board/status", response_class=HTMLResponse)
async def get_or_board_status(request: Request):
    """HTMX partial for OR board status update"""
    # This would typically fetch real-time data
    # For now, return success to indicate the island should refresh
    return HTMLResponse('<div hx-trigger="load" hx-get="/api/v1/htmx/or-board/refresh"></div>')

# Export the router
__all__ = ["router"]
