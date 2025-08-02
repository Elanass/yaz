"""
Hospitality page for the YAZ Surgery Analytics Platform
"""

from fastapi import APIRouter as FastAPIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fasthtml.common import Div, H1, H2, H3, H4, P, Form as FHTMLForm, Input, Button, A, Br, Script, Table, Tr, Td, Th, Span, Strong

from core.dependencies import require_auth, optional_user
from web.components.layout import create_base_layout
from web.components.hospitality_dashboard import render_hospitality_dashboard

router = FastAPIRouter(prefix="/hospitality")
templates = Jinja2Templates(directory="web/templates")

@router.get("/")
async def hospitality_home(request: Request, current_user = Depends(optional_user)):
    """Hospitality and patient experience dashboard"""
    
    
    # Mock user data - in production this would come from the database
    user_data = {
        'name': current_user.get('name', 'User') if current_user else 'Guest',
        'role': current_user.get('role', 'Hospitality Coordinator') if current_user else 'Guest',
        'id': current_user.get('id') if current_user else None
    }
    
    content = Div(
        # Page header
        Div(
            H1(
                "Patient Hospitality & Experience",
                class_="text-3xl font-bold text-gray-900"
            ),
            P(
                "Comprehensive patient care coordination, accommodation management, and family support services.",
                class_="mt-2 text-lg text-gray-600"
            ),
            class_="mb-8"
        ),
        
        # Navigation tabs
        Div(
            Nav(
                Div(
                    A("Dashboard", href="/hospitality", class_="tab-active"),
                    A("Patient Plans", href="/hospitality/plans", class_="tab-link"),
                    A("Accommodation", href="/hospitality/accommodation", class_="tab-link"),
                    A("Family Services", href="/hospitality/family", class_="tab-link"),
                    A("Dietary Management", href="/hospitality/dietary", class_="tab-link"),
                    A("Transportation", href="/hospitality/transport", class_="tab-link"),
                    class_="flex space-x-8 border-b border-gray-200"
                ),
                class_="mb-6"
            ),
            class_="border-b border-gray-200"
        ),
        
        # Dashboard content
        Div(
            NotStr(render_hospitality_dashboard(user_data)),
            class_="hospitality-content"
        ),
        
        # Action buttons
        Div(
            Div(
                A(
                    "New Hospitality Plan",
                    href="/hospitality/plans/new",
                    class_="btn btn-primary"
                ),
                A(
                    "View Metrics",
                    href="/hospitality/metrics",
                    class_="btn btn-secondary ml-4"
                ),
                A(
                    "Settings",
                    href="/hospitality/settings",
                    class_="btn btn-outline ml-4"
                ),
                class_="flex justify-center space-x-4"
            ),
            class_="mt-8"
        ),
        
        class_="container mx-auto px-4 py-6"
    )
    
    # Add custom styles for hospitality dashboard
    styles = """
    <style>
        .hospitality-dashboard {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 24px;
        }
        
        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }
        
        .dashboard-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.2s ease-in-out;
        }
        
        .dashboard-card:hover {
            box-shadow: 0 8px 25px -4px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        
        .card-header h3 {
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
            margin: 0;
        }
        
        .score-circle, .satisfaction-indicator {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: conic-gradient(#10b981 94%, #e5e7eb 0);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #1f2937;
        }
        
        .tab-active {
            color: #059669;
            border-bottom: 2px solid #059669;
            padding-bottom: 8px;
            font-weight: 600;
        }
        
        .tab-link {
            color: #6b7280;
            padding-bottom: 8px;
            transition: color 0.2s;
        }
        
        .tab-link:hover {
            color: #059669;
        }
        
        .btn {
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: #059669;
            color: white;
        }
        
        .btn-primary:hover {
            background: #047857;
        }
        
        .btn-secondary {
            background: #6b7280;
            color: white;
        }
        
        .btn-outline {
            border: 1px solid #d1d5db;
            color: #374151;
            background: white;
        }
        
        .role-badge {
            background: #d1fae5;
            color: #065f46;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 14px;
            font-weight: 500;
        }
        
        .service-status {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .status-active {
            background: #d1fae5;
            color: #065f46;
        }
        
        .status-pending {
            background: #fef3c7;
            color: #92400e;
        }
        
        .status-completed {
            background: #dbeafe;
            color: #1e40af;
        }
    </style>
    """
    
    return create_base_layout(
        content=content,
        title="Hospitality & Patient Experience - YAZ Surgery Analytics",
        extra_head=styles
    )

@router.get("/plans")
async def hospitality_plans(request: Request, current_user = Depends(optional_user)):
    """Hospitality plans management"""
    
    
    content = Div(
        H1("Hospitality Plans", class_="text-3xl font-bold text-gray-900 mb-6"),
        P("Manage comprehensive patient hospitality and care coordination plans", class_="text-lg text-gray-600 mb-8"),
        
        # Plans grid
        Div(
            # Plan cards would be dynamically generated here
            Div(
                H3("Comprehensive Care Package", class_="text-xl font-semibold mb-2"),
                P("Full-service hospitality including accommodation, meals, and family support", class_="text-gray-600 mb-4"),
                Div(
                    Span("Duration: 7 days", class_="text-sm text-gray-500 mr-4"),
                    Span("Type: Surgery", class_="text-sm text-gray-500 mr-4"),
                    Span("Active Plans: 12", class_="text-sm text-gray-500"),
                    class_="mb-4"
                ),
                A("View Details", href="/hospitality/plans/1", class_="btn btn-primary"),
                class_="bg-white p-6 rounded-lg shadow border"
            ),
            
            Div(
                H3("Outpatient Support Package", class_="text-xl font-semibold mb-2"),
                P("Day-visit support with meal service and transportation coordination", class_="text-gray-600 mb-4"),
                Div(
                    Span("Duration: 1 day", class_="text-sm text-gray-500 mr-4"),
                    Span("Type: Consultation", class_="text-sm text-gray-500 mr-4"),
                    Span("Active Plans: 8", class_="text-sm text-gray-500"),
                    class_="mb-4"
                ),
                A("View Details", href="/hospitality/plans/2", class_="btn btn-primary"),
                class_="bg-white p-6 rounded-lg shadow border"
            ),
            
            class_="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        ),
        
        class_="container mx-auto px-4 py-6"
    )
    
    return create_base_layout(
        content=content,
        title="Hospitality Plans - YAZ Surgery Analytics"
    )

@router.get("/accommodation")
async def hospitality_accommodation(request: Request, current_user = Depends(optional_user)):
    """Accommodation management"""
    
    
    content = Div(
        H1("Accommodation Management", class_="text-3xl font-bold text-gray-900 mb-6"),
        P("Manage patient and family accommodation arrangements", class_="text-lg text-gray-600 mb-8"),
        
        # Accommodation dashboard
        Div(
            Div(
                H3("Room Availability", class_="text-xl font-semibold mb-4"),
                # Room status would be displayed here
                P("Room management interface would be implemented here", class_="text-gray-600"),
                class_="bg-white p-6 rounded-lg shadow border"
            ),
            class_="grid grid-cols-1 gap-6"
        ),
        
        class_="container mx-auto px-4 py-6"
    )
    
    return create_base_layout(
        content=content,
        title="Accommodation Management - YAZ Surgery Analytics"
    )

@router.get("/family")
async def family_services(request: Request, current_user = Depends(optional_user)):
    """Family support services"""
    
    
    content = Div(
        H1("Family Support Services", class_="text-3xl font-bold text-gray-900 mb-6"),
        P("Coordinate support services for patient families", class_="text-lg text-gray-600 mb-8"),
        
        # Family services content
        Div(
            Div(
                H3("Active Family Plans", class_="text-xl font-semibold mb-4"),
                P("Family support coordination would be managed here", class_="text-gray-600"),
                class_="bg-white p-6 rounded-lg shadow border"
            ),
            class_="grid grid-cols-1 gap-6"
        ),
        
        class_="container mx-auto px-4 py-6"
    )
    
    return create_base_layout(
        content=content,
        title="Family Support Services - YAZ Surgery Analytics"
    )

@router.get("/dietary")
async def dietary_management(request: Request, current_user = Depends(optional_user)):
    """Dietary management and meal planning"""
    
    
    content = Div(
        H1("Dietary Management", class_="text-3xl font-bold text-gray-900 mb-6"),
        P("Manage patient dietary requirements and meal planning", class_="text-lg text-gray-600 mb-8"),
        
        # Dietary management interface
        Div(
            Div(
                H3("Meal Plans", class_="text-xl font-semibold mb-4"),
                P("Dietary management interface would be implemented here", class_="text-gray-600"),
                class_="bg-white p-6 rounded-lg shadow border"
            ),
            class_="grid grid-cols-1 gap-6"
        ),
        
        class_="container mx-auto px-4 py-6"
    )
    
    return create_base_layout(
        content=content,
        title="Dietary Management - YAZ Surgery Analytics"
    )

@router.get("/transport")
async def transportation_coordination(request: Request, current_user = Depends(optional_user)):
    """Transportation coordination"""
    
    
    content = Div(
        H1("Transportation Coordination", class_="text-3xl font-bold text-gray-900 mb-6"),
        P("Coordinate patient and family transportation services", class_="text-lg text-gray-600 mb-8"),
        
        # Transportation interface
        Div(
            Div(
                H3("Transportation Requests", class_="text-xl font-semibold mb-4"),
                P("Transportation coordination interface would be implemented here", class_="text-gray-600"),
                class_="bg-white p-6 rounded-lg shadow border"
            ),
            class_="grid grid-cols-1 gap-6"
        ),
        
        class_="container mx-auto px-4 py-6"
    )
    
    return create_base_layout(
        content=content,
        title="Transportation Coordination - YAZ Surgery Analytics"
    )
