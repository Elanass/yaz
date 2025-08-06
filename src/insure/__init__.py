"""
Insure - Insurance Analytics Platform
Risk stratification, cost prediction, and claims optimization
"""

__version__ = "2.0.0"
__author__ = "Surgify Platform Team"

from .api.router import router as insurance_router
from .core.insurance_engine import InsuranceEngine

__all__ = ["InsuranceEngine", "insurance_router"]
