"""
Movit - Logistics and Movement Analytics Platform
Resource optimization, workflow analysis, and supply chain management
"""

__version__ = "2.0.0"
__author__ = "Surgify Platform Team"

from .api.router import router as logistics_router
from .core.logistics_engine import LogisticsEngine

__all__ = ["LogisticsEngine", "logistics_router"]
