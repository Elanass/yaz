"""
Core module for YAZ Healthcare Platform
Clean, minimal, focused core functionality using shared foundation
"""

from shared.config import get_shared_config
from shared.logging import get_logger
from shared.database import init_database
from shared.base_app import create_base_app

__version__ = "1.0.0"
__author__ = "YAZ Healthcare Platform"

# Re-export shared components for convenience
__all__ = [
    "get_shared_config",
    "get_logger", 
    "init_database",
    "create_base_app"
]
