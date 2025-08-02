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

# Create main web router
router = APIRouter()

# Include all page routers
router.include_router(home_router, tags=["Web Pages"])
router.include_router(auth_router, tags=["Web Auth"])
router.include_router(cases_router, tags=["Web Cases"])
router.include_router(reports_router, tags=["Web Reports"])
router.include_router(education_router, tags=["Web Education"])
router.include_router(hospitality_router, tags=["Web Hospitality"])
