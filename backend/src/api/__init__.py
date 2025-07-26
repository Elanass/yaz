"""
API Router configuration for Gastric ADCI Platform
"""

from fastapi import APIRouter
from .v1 import auth, users, patients, protocols, decision_engine, evidence, admin, cohorts
from . import assistance_bot, workflow, remote_reports

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(protocols.router, prefix="/protocols", tags=["protocols"])
api_router.include_router(decision_engine.router, prefix="/decision-engine", tags=["decision-engine"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["evidence"])
api_router.include_router(cohorts.router, prefix="/cohorts", tags=["cohorts"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(assistance_bot.router, prefix="/assistance-bot", tags=["assistance-bot"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["workflow"])
api_router.include_router(remote_reports.router, prefix="/remote-reports", tags=["remote-reports"])

# API version info
@api_router.get("/", tags=["info"])
async def api_info():
    """API information endpoint"""
    return {
        "name": "Gastric ADCI Platform API",
        "version": "1.0.0",
        "description": "Gastric Oncology-Surgery Decision Support Platform",
        "documentation": "/api/docs",
        "contact": {
            "clinical_support": "clinical-support@gastric-adci.health",
            "technical_support": "tech-support@gastric-adci.health"
        },
        "compliance": {
            "hipaa": True,
            "gdpr": True,
            "audit_logging": True
        }
    }
