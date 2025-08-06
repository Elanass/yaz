"""
Integration Components for Universal Research Module
Seamlessly integrates with existing Surgify infrastructure
"""

from .api_enhancer import ResearchAPIEnhancer
from .auth_integrator import AuthIntegrator
from .database_bridge import DatabaseBridge

__all__ = ["ResearchAPIEnhancer", "DatabaseBridge", "AuthIntegrator"]
