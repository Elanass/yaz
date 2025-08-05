"""
Integration Components for Universal Research Module
Seamlessly integrates with existing Surgify infrastructure
"""

from .api_enhancer import ResearchAPIEnhancer
from .database_bridge import DatabaseBridge
from .auth_integrator import AuthIntegrator

__all__ = ["ResearchAPIEnhancer", "DatabaseBridge", "AuthIntegrator"]
