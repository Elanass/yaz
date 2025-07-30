"""
Education page for the YAZ Surgery Analytics Platform
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fasthtml.common import *

from features.auth.service import get_current_user, optional_user
from web.components.layout import create_base_layout
from web.components.education_dashboard import render_education_dashboard

router = APIRouter(prefix="/education")
templates = Jinja2Templates(directory="web/templates")

@router.get("/", response_class=HTMLResponse)
async def education_home(request: Request, current_user = Depends(optional_user)):
    """Education and training dashboard"""
    
    # Mock user data - in production this would come from the database
    user_data = {
        'name': current_user.get('name', 'User') if current_user else 'Guest',
        'role': current_user.get('role', 'Healthcare Professional') if current_user else 'Guest',
        'id': current_user.get('id') if current_user else None
    }
    
    content = Div(
        # Page header
        Div(
            H1(
                "Medical Education & Training",
                class_="text-3xl font-bold text-gray-900"
            ),
            P(
                "Comprehensive training programs, skill assessment, and continuing education for surgical excellence.",
                class_="mt-2 text-lg text-gray-600"
            ),
            class_="mb-8"
        ),
        
        # Navigation tabs
        Div(
            Nav(
                Div(
                    A("Dashboard", href="/education", class_="tab-active"),
                    A("Training Programs", href="/education/programs", class_="tab-link"),
                    A("Skill Assessment", href="/education/assessment", class_="tab-link"),
                    A("Continuing Education", href="/education/continuing", class_="tab-link"),
                    A("Simulation Lab", href="/education/simulation", class_="tab-link"),
                    class_="flex space-x-8 border-b border-gray-200"
                ),
                class_="mb-6"
            ),
            class_="border-b border-gray-200"
        ),
        
        # Dashboard content
        Div(
            NotStr(render_education_dashboard(user_data)),
            class_="education-content"
        ),
        
        # Action buttons
        Div(
            Div(
                A(
                    "New Training Program",
                    href="/education/programs/new",
                    class_="btn btn-primary"
                ),
                A(
                    "View Reports",
                    href="/education/reports",
                    class_="btn btn-secondary ml-4"
                ),
                A(
                    "Settings",
                    href="/education/settings",
                    class_="btn btn-outline ml-4"
                ),
                class_="flex justify-center space-x-4"
            ),
            class_="mt-8"
        ),
        
        class_="container mx-auto px-4 py-6"
    )
    
    # Add custom styles for education dashboard
    styles = """
    <style>
        .education-dashboard {
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
        
        .progress-circle, .score-circle {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: conic-gradient(#3b82f6 75%, #e5e7eb 0);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #1f2937;
        }
        
        .tab-active {
            color: #3b82f6;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 8px;
            font-weight: 600;
        }
        
        .tab-link {
            color: #6b7280;
            padding-bottom: 8px;
            transition: color 0.2s;
        }
        
        .tab-link:hover {
            color: #3b82f6;
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
            background: #3b82f6;
            color: white;
        }
        
        .btn-primary:hover {
            background: #2563eb;
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
            background: #dbeafe;
            color: #1e40af;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 14px;
            font-weight: 500;
        }
    </style>
    """
    
    return create_base_layout(
        content=content,
        title="Education & Training - YAZ Surgery Analytics",
        extra_head=styles
    )

@router.get("/programs", response_class=HTMLResponse)
async def education_programs(request: Request, current_user = Depends(optional_user)):
    """Training programs management"""
    
    
    content = Div(
        H1("Training Programs", class_="text-3xl font-bold text-gray-900 mb-6"),
        P("Manage and track surgical training programs", class_="text-lg text-gray-600 mb-8"),
        
        # Programs grid
        Div(
            # Program cards would be dynamically generated here
            Div(
                H3("Laparoscopic Surgery Fundamentals", class_="text-xl font-semibold mb-2"),
                P("8-week comprehensive program covering basic laparoscopic techniques", class_="text-gray-600 mb-4"),
                Div(
                    Span("Duration: 8 weeks", class_="text-sm text-gray-500 mr-4"),
                    Span("Level: Beginner", class_="text-sm text-gray-500 mr-4"),
                    Span("Enrolled: 24", class_="text-sm text-gray-500"),
                    class_="mb-4"
                ),
                A("View Details", href="/education/programs/1", class_="btn btn-primary"),
                class_="bg-white p-6 rounded-lg shadow border"
            ),
            
            Div(
                H3("Advanced Robotic Surgery", class_="text-xl font-semibold mb-2"),
                P("Specialized training in robotic surgical systems and techniques", class_="text-gray-600 mb-4"),
                Div(
                    Span("Duration: 12 weeks", class_="text-sm text-gray-500 mr-4"),
                    Span("Level: Advanced", class_="text-sm text-gray-500 mr-4"),
                    Span("Enrolled: 8", class_="text-sm text-gray-500"),
                    class_="mb-4"
                ),
                A("View Details", href="/education/programs/2", class_="btn btn-primary"),
                class_="bg-white p-6 rounded-lg shadow border"
            ),
            
            class_="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        ),
        
        class_="container mx-auto px-4 py-6"
    )
    
    return create_base_layout(
        content=content,
        title="Training Programs - YAZ Surgery Analytics"
    )

@router.get("/assessment", response_class=HTMLResponse)
async def education_assessment(request: Request, current_user = Depends(optional_user)):
    """Skill assessment and evaluation"""
    
    
    content = Div(
        H1("Skill Assessment", class_="text-3xl font-bold text-gray-900 mb-6"),
        P("Evaluate and track surgical skills and competencies", class_="text-lg text-gray-600 mb-8"),
        
        # Assessment dashboard
        Div(
            Div(
                H3("Recent Assessments", class_="text-xl font-semibold mb-4"),
                # Assessment items would be listed here
                P("Assessment interface would be implemented here", class_="text-gray-600"),
                class_="bg-white p-6 rounded-lg shadow border"
            ),
            class_="grid grid-cols-1 gap-6"
        ),
        
        class_="container mx-auto px-4 py-6"
    )
    
    return create_base_layout(
        content=content,
        title="Skill Assessment - YAZ Surgery Analytics"
    )

@router.get("/continuing", response_class=HTMLResponse)
async def continuing_education(request: Request, current_user = Depends(optional_user)):
    """Continuing education and professional development"""
    
    
    content = Div(
        H1("Continuing Education", class_="text-3xl font-bold text-gray-900 mb-6"),
        P("Stay current with latest surgical techniques and medical advances", class_="text-lg text-gray-600 mb-8"),
        
        # CE content
        Div(
            Div(
                H3("Available Courses", class_="text-xl font-semibold mb-4"),
                P("Continuing education courses would be listed here", class_="text-gray-600"),
                class_="bg-white p-6 rounded-lg shadow border"
            ),
            class_="grid grid-cols-1 gap-6"
        ),
        
        class_="container mx-auto px-4 py-6"
    )
    
    return create_base_layout(
        content=content,
        title="Continuing Education - YAZ Surgery Analytics"
    )

@router.get("/simulation", response_class=HTMLResponse) 
async def simulation_lab(request: Request, current_user = Depends(optional_user)):
    """Virtual simulation laboratory"""
    
    
    content = Div(
        H1("Simulation Lab", class_="text-3xl font-bold text-gray-900 mb-6"),
        P("Practice surgical procedures in a risk-free virtual environment", class_="text-lg text-gray-600 mb-8"),
        
        # Simulation interface
        Div(
            Div(
                H3("Available Simulations", class_="text-xl font-semibold mb-4"),
                P("Virtual surgery simulation interface would be implemented here", class_="text-gray-600"),
                class_="bg-white p-6 rounded-lg shadow border"
            ),
            class_="grid grid-cols-1 gap-6"
        ),
        
        class_="container mx-auto px-4 py-6"
    )
    
    return create_base_layout(
        content=content,
        title="Simulation Lab - YAZ Surgery Analytics"
    )
