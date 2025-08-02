"""
Home page router for Gastric ADCI Platform
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import logging

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")
logger = logging.getLogger(__name__)

@router.get("/")
async def home(request: Request):
    """Home page - Surgify template"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "page_title": "Surgify - Decision Precision Engine"
    })

@router.get("/workstation")
async def workstation(request: Request):
    """Clinical workstation - main dashboard for surgeons"""
    return templates.TemplateResponse("workstation.html", {
        "request": request,
        "page_title": "Clinical Workstation"
    })

@router.get("/add-case")
async def add_case_form(request: Request):
    """Add new case form - secure form for creating surgical cases"""
    try:
        # Get form configuration from database
        specialties = await get_available_specialties()
        protocols = await get_available_protocols()
        
        return templates.TemplateResponse("add_case.html", {
            "request": request,
            "page_title": "Add New Case",
            "specialties": specialties,
            "protocols": protocols
        })
    except Exception as e:
        logger.error(f"Error loading add case form: {e}")
        return templates.TemplateResponse("add_case.html", {
            "request": request,
            "page_title": "Add New Case",
            "error": "Failed to load form data"
        })

@router.get("/marketplace")
async def marketplace(request: Request):
    """Marketplace page"""
    return templates.TemplateResponse("marketplace.html", {
        "request": request,
        "page_title": "Marketplace"
    })

@router.get("/settings")
async def settings(request: Request):
    """Settings page"""
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "page_title": "Settings"
    })

@router.get("/dashboard")
async def dashboard(request: Request):
    """Dashboard page - redirect to workstation"""
    return templates.TemplateResponse("workstation.html", {"request": request})

@router.get("/test")
async def test_page(request: Request):
    """Test page for DRY compliance validation"""
    return HTMLResponse(content=open("web/static/test.html").read())

# Entity routes
@router.get("/entities/{entity_type}")
async def entity_page(request: Request, entity_type: str):
    """Entity pages for medical entities"""
    try:
        entity_types = {
            "patients": "Patient Management",
            "procedures": "Procedure Catalog", 
            "surgeons": "Surgeon Directory",
            "diagnoses": "Diagnosis Codes"
        }
        
        if entity_type not in entity_types:
            raise HTTPException(status_code=404, detail="Entity type not found")
            
        return templates.TemplateResponse("index.html", {
            "request": request,
            "page_title": entity_types[entity_type],
            "entity_type": entity_type
        })
    except Exception as e:
        logger.error(f"Error loading entity page {entity_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load entity page")

# Concept routes  
@router.get("/concepts/{concept_type}")
async def concept_page(request: Request, concept_type: str):
    """Concept pages for business concepts"""
    try:
        concept_types = {
            "workflows": "Clinical Workflows",
            "protocols": "Clinical Protocols",
            "resources": "Resource Management", 
            "quality": "Quality Metrics"
        }
        
        if concept_type not in concept_types:
            raise HTTPException(status_code=404, detail="Concept type not found")
            
        return templates.TemplateResponse("index.html", {
            "request": request,
            "page_title": concept_types[concept_type],
            "concept_type": concept_type
        })
    except Exception as e:
        logger.error(f"Error loading concept page {concept_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load concept page")

# Knowledge routes
@router.get("/knowledge/{knowledge_type}")
async def knowledge_page(request: Request, knowledge_type: str):
    """Knowledge pages for domain knowledge"""
    try:
        knowledge_types = {
            "guidelines": "Clinical Guidelines",
            "evidence": "Evidence Base",
            "research": "Research Data"
        }
        
        if knowledge_type not in knowledge_types:
            raise HTTPException(status_code=404, detail="Knowledge type not found")
            
        return templates.TemplateResponse("index.html", {
            "request": request,
            "page_title": knowledge_types[knowledge_type],
            "knowledge_type": knowledge_type
        })
    except Exception as e:
        logger.error(f"Error loading knowledge page {knowledge_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load knowledge page")

# Database helper functions with proper error handling
async def get_user_cases_count() -> int:
    """Get total number of cases for current user"""
    try:
        # Mock implementation - replace with actual database query
        return 25
    except Exception:
        return 0

async def get_pending_reviews() -> int:
    """Get number of pending case reviews"""
    try:
        # Mock implementation - replace with actual database query
        return 3
    except Exception:
        return 0

async def get_recent_cases(limit: int = 5) -> list:
    """Get recent cases for current user"""
    try:
        # Mock implementation - replace with actual database query
        return [
            {"id": 1, "title": "Gastric Sleeve Resection", "date": "2025-08-01", "status": "completed"},
            {"id": 2, "title": "Laparoscopic Cholecystectomy", "date": "2025-07-30", "status": "pending"},
            {"id": 3, "title": "ERCP Procedure", "date": "2025-07-28", "status": "reviewed"}
        ]
    except Exception:
        return []

async def get_available_specialties() -> list:
    """Get available surgical specialties"""
    try:
        return ["Gastrointestinal", "Cardiovascular", "Orthopedic", "Neurosurgery", "Urologic"]
    except Exception:
        return []

async def get_available_protocols() -> list:
    """Get available surgical protocols"""
    try:
        return [
            {"id": 1, "name": "ADCI Standard Protocol", "version": "2.0"},
            {"id": 2, "name": "Enhanced Recovery Protocol", "version": "1.5"},
            {"id": 3, "name": "Minimally Invasive Protocol", "version": "3.0"}
        ]
    except Exception:
        return []

async def get_featured_protocols() -> list:
    """Get featured protocols from marketplace"""
    try:
        return [
            {"id": 1, "name": "Advanced Gastric Procedures", "downloads": 1250, "rating": 4.8},
            {"id": 2, "name": "Emergency Surgery Protocols", "downloads": 890, "rating": 4.7},
            {"id": 3, "name": "Pediatric Surgery Guidelines", "downloads": 654, "rating": 4.9}
        ]
    except Exception:
        return []

async def get_protocol_categories() -> list:
    """Get protocol categories"""
    try:
        return ["Emergency", "Elective", "Pediatric", "Geriatric", "Minimally Invasive"]
    except Exception:
        return []

async def get_user_downloads() -> list:
    """Get user's downloaded protocols"""
    try:
        return [
            {"id": 1, "name": "ADCI Standard Protocol", "downloaded_date": "2025-07-15"}
        ]
    except Exception:
        return []

async def get_user_preferences() -> dict:
    """Get user preferences"""
    try:
        return {
            "theme": "light",
            "notifications": True,
            "auto_save": True,
            "language": "en",
            "timezone": "UTC"
        }
    except Exception:
        return {}

async def get_system_settings() -> dict:
    """Get system settings"""
    try:
        return {
            "version": "2.0.0",
            "maintenance_mode": False,
            "backup_enabled": True,
            "security_level": "high"
        }
    except Exception:
        return {}
