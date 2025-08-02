"""
Web router for YAZ Surgery Analytics Platform
Includes all web page routes and handles front-end navigation
"""

from fastapi import APIRouter

# Import page routers
from web.pages.home import router as home_router
from web.pages.auth import router as auth_router
from web.pages.cases import router as cases_router
from web.pages.reports import router as reports_router
from web.pages.education import router as education_router
from web.pages.hospitality import router as hospitality_router

# Create main web router
web_router = APIRouter()

# Include all page routers
web_router.include_router(home_router, tags=["Web Pages"])
web_router.include_router(auth_router, tags=["Web Auth"])
web_router.include_router(cases_router, tags=["Web Cases"])
web_router.include_router(reports_router, tags=["Web Reports"])
web_router.include_router(education_router, tags=["Web Education"])
web_router.include_router(hospitality_router, tags=["Web Hospitality"])
