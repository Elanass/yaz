"""
Dashboard API for Decision Precision in Surgery Platform.

Provides endpoints for the Surgify-inspired dashboard interface with
HTMX integration, RBAC security, and real-time data.
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any, Optional
import datetime

from features.auth.service import get_current_user
from features.cohorts import get_featured_series, get_upcoming_events, get_journal_articles
from core.dependencies import get_cohorts_service
from features.cohorts import CohortsService
from core.services.logger import get_logger
from services.event_logger.service import event_logger, EventCategory, EventSeverity

# Initialize router and templates
router = APIRouter(prefix="", tags=["dashboard"])
templates = Jinja2Templates(directory="web")
logger = get_logger(__name__)


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    user=Depends(get_current_user)
):
    """
    Main index page with Surgify UI.
    
    Returns the new Surgify-style PWA interface.
    """
    try:
        # Log access
        await event_logger.log_event(
            category=EventCategory.USER_ACTION,
            severity=EventSeverity.INFO,
            message=f"Home page accessed by user {user.get('id', 'unknown') if user else 'anonymous'}",
            metadata={"endpoint": "/"}
        )
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "current_page": "home",
            "user": user
        })
        
    except Exception as e:
        logger.error(f"Index error: {str(e)}")
        await event_logger.log_event(
            category=EventCategory.SYSTEM_ERROR,
            severity=EventSeverity.ERROR,
            message=f"Index error: {str(e)}",
            metadata={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Home page unavailable")


@router.get("/api/v1/journal", response_class=HTMLResponse)
async def journal_partial(
    request: Request,
    limit: int = 10,
    offset: int = 0,
    user=Depends(get_current_user),
    
):
    """Get journal articles as HTML partial for HTMX."""
    try:
        items = await get_journal_articles(limit=limit, offset=offset)
        
        # Transform for card carousel
        for item in items:
            item.type = "journal"
        
        return templates.TemplateResponse("components/card_carousel.html", {
            "request": request,
            "items": items
        })
        
    except Exception as e:
        logger.error(f"Journal partial error: {str(e)}")
        return HTMLResponse("<div class='text-red-500'>Error loading journal articles</div>")


@router.get("/api/v1/events", response_class=HTMLResponse)
async def events_partial(
    request: Request,
    upcoming: bool = False,
    limit: int = 10,
    offset: int = 0,
    user=Depends(get_current_user),
    
):
    """Get events as HTML partial for HTMX."""
    try:
        items = await get_upcoming_events(limit=limit, offset=offset) if upcoming else await get_events(limit=limit, offset=offset)
        
        # Transform for card carousel
        for item in items:
            item.type = "event"
        
        return templates.TemplateResponse("components/card_carousel.html", {
            "request": request,
            "items": items
        })
        
    except Exception as e:
        logger.error(f"Events partial error: {str(e)}")
        return HTMLResponse("<div class='text-red-500'>Error loading events</div>")


@router.get("/api/v1/series", response_class=HTMLResponse)
async def series_partial(
    request: Request,
    featured: bool = False,
    limit: int = 10,
    offset: int = 0,
    user=Depends(get_current_user),
    
):
    """Get series as HTML partial for HTMX."""
    try:
        items = await get_featured_series(limit=limit, offset=offset) if featured else await get_series(limit=limit, offset=offset)
        
        # Transform for card carousel
        for item in items:
            item.type = "series"
        
        return templates.TemplateResponse("components/card_carousel.html", {
            "request": request,
            "items": items
        })
        
    except Exception as e:
        logger.error(f"Series partial error: {str(e)}")
        return HTMLResponse("<div class='text-red-500'>Error loading series</div>")


@router.get("/api/v1/protocols", response_class=HTMLResponse)
async def protocols_partial(
    request: Request,
    limit: int = 10,
    offset: int = 0,
    user=Depends(get_current_user),
    
):
    """Get protocols as HTML partial for HTMX."""
    try:
        items = await get_protocols(limit=limit, offset=offset)
        
        # Transform for card carousel
        for item in items:
            item.type = "protocol"
        
        return templates.TemplateResponse("components/card_carousel.html", {
            "request": request,
            "items": items
        })
        
    except Exception as e:
        logger.error(f"Protocols partial error: {str(e)}")
        return HTMLResponse("<div class='text-red-500'>Error loading protocols</div>")


@router.get("/api/v1/cases", response_class=HTMLResponse)
async def cases_search(
    request: Request,
    query: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    user=Depends(get_current_user),
    
):
    """Search cases with HTMX support."""
    try:
        # Log search action
        await event_logger.log_event(
            category=EventCategory.USER_ACTION,
            severity=EventSeverity.INFO,
            message=f"Case search by user {user.get('id', 'unknown')}: {query}",
            metadata={"user_id": user.get('id'), "query": query, "category": category}
        )
        
        items = await search_cases(query=query, category=category, limit=limit, offset=offset)
        
        # Transform for card carousel
        for item in items:
            item.type = "case"
        
        return templates.TemplateResponse("components/card_carousel.html", {
            "request": request,
            "items": items
        })
        
    except Exception as e:
        logger.error(f"Cases search error: {str(e)}")
        return HTMLResponse("<div class='text-red-500'>Error searching cases</div>")


# Data fetching functions
async def get_featured_series(limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
    """Get featured clinical series."""
    try:
        # Mock data for now - replace with actual database queries
        series = [
            {
                "id": "series_1",
                "title": "Advanced Gastric Cancer Management",
                "subtitle": "Comprehensive surgical approaches",
                "description": "Latest techniques in gastric oncology surgery",
                "image_url": "/static/images/gastric-series-1.jpg",
                "type": "series",
                "date": datetime.datetime.now() - datetime.timedelta(days=2),
                "author": "Dr. Smith et al."
            },
            {
                "id": "series_2", 
                "title": "FLOT Protocol Implementation",
                "subtitle": "Perioperative chemotherapy guidelines",
                "description": "Evidence-based FLOT protocol for gastric cancer",
                "image_url": "/static/images/flot-series.jpg",
                "type": "series",
                "date": datetime.datetime.now() - datetime.timedelta(days=5),
                "author": "European Oncology Group"
            }
        ]
        
        return series[offset:offset+limit]
        
    except Exception as e:
        logger.error(f"Error fetching featured series: {str(e)}")
        return []


async def get_upcoming_events(limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
    """Get upcoming clinical events."""
    try:
        # Mock data for now - replace with actual database queries
        events = [
            {
                "id": "event_1",
                "title": "Gastric Surgery Symposium 2025",
                "subtitle": "International conference on gastric oncology",
                "description": "Latest advances in gastric cancer surgery",
                "image_url": "/static/images/symposium-2025.jpg",
                "type": "event",
                "date": datetime.datetime.now() + datetime.timedelta(days=30),
                "location": "Medical Center"
            },
            {
                "id": "event_2",
                "title": "ADCI Framework Workshop",
                "subtitle": "Hands-on decision support training",
                "description": "Learn to use the ADCI framework effectively",
                "image_url": "/static/images/adci-workshop.jpg",
                "type": "event",
                "date": datetime.datetime.now() + datetime.timedelta(days=15),
                "location": "Online"
            }
        ]
        
        return events[offset:offset+limit]
        
    except Exception as e:
        logger.error(f"Error fetching upcoming events: {str(e)}")
        return []


async def get_journal_articles(limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
    """Get latest journal articles."""
    try:
        # Mock data for journal articles
        articles = [
            {
                "id": "article_1",
                "title": "ADCI Framework Validation in Gastric Cancer",
                "author": "Dr. Johnson et al.",
                "abstract": "Comprehensive validation of the Adaptive Decision Confidence Index framework",
                "journal": "Journal of Gastric Oncology",
                "published_date": datetime.datetime.now() - datetime.timedelta(days=7),
                "impact_factor": 8.5,
                "type": "journal"
            },
            {
                "id": "article_2",
                "title": "FLOT Protocol Meta-Analysis",
                "author": "Dr. Williams et al.",
                "abstract": "Meta-analysis of FLOT protocol outcomes in gastric cancer",
                "journal": "International Journal of Surgical Oncology",
                "published_date": datetime.datetime.now() - datetime.timedelta(days=14),
                "impact_factor": 7.2,
                "type": "journal"
            }
        ]
        
        return articles
        
    except Exception as e:
        logger.error(f"Error fetching journal articles: {str(e)}")
        return []


async def get_events(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """Get all events."""
    return await get_upcoming_events(limit=limit, offset=offset)


async def get_series(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """Get all series."""
    return await get_featured_series(limit=limit, offset=offset)


async def get_protocols(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """Get clinical protocols."""
    try:
        # Mock protocol data
        protocols = [
            {
                "id": "protocol_1",
                "name": "FLOT Perioperative Protocol",
                "description": "Standard FLOT implementation for gastric cancer",
                "summary": "4 cycles pre-op, 4 cycles post-op of Fluorouracil, Leucovorin, Oxaliplatin, and Docetaxel",
                "created_at": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_by": "Surgical Oncology Team"
            },
            {
                "id": "protocol_2",
                "name": "Gastric ADCI Implementation",
                "description": "Decision support implementation for gastric cancer surgery",
                "summary": "Step-by-step ADCI framework for surgical planning",
                "created_at": datetime.datetime.now() - datetime.timedelta(days=45),
                "created_by": "Decision Precision Team"
            }
        ]
        
        protocols_list = []
        for protocol in protocols:
            protocols_list.append({
                "id": protocol.get("id"),
                "title": protocol.get("name", "Untitled Protocol"),
                "subtitle": protocol.get("description", ""),
                "description": protocol.get("summary", ""),
                "type": "protocol",
                "date": protocol.get("created_at"),
                "author": protocol.get("created_by", "System")
            })
        
        return protocols_list
        
    except Exception as e:
        logger.error(f"Error fetching protocols: {str(e)}")
        return []


async def search_cases(query: Optional[str] = None, category: Optional[str] = None, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """Search clinical cases."""
    try:
        # Mock implementation - replace with actual case search
        cases = [
            {
                "id": "case_1",
                "title": f"Gastric Adenocarcinoma Case - Stage II",
                "subtitle": "T2N1M0 gastric cancer with FLOT protocol",
                "description": "65-year-old patient with gastric adenocarcinoma",
                "type": "case",
                "date": datetime.datetime.now() - datetime.timedelta(days=3),
                "author": "Dr. Clinical Team"
            }
        ]
        
        # Filter by query if provided
        if query:
            cases = [case for case in cases if query.lower() in case["title"].lower()]
        
        return cases[offset:offset+limit]
        
    except Exception as e:
        logger.error(f"Error searching cases: {str(e)}")
        return []
