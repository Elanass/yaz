"""
Main API Router for the Healthcare Cases PWA
Simplified version for MVP
"""

from fastapi import APIRouter

from .cases import router as cases_router
from .analysis import router as analysis_router
from .auth import router as auth_router
from .decisions import router as decisions_router
from .surgery import router as surgery_router

api_router = APIRouter()

# Include essential routers for MVP
api_router.include_router(cases_router, prefix="/cases", tags=["cases"])
api_router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(decisions_router, prefix="/decisions", tags=["decisions"])
api_router.include_router(surgery_router, prefix="/surgery", tags=["surgery"])
