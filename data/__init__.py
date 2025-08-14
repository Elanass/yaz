"""
Minimal Data Management
Clean interface to database operations using shared foundation
"""

from shared.database import get_session, create_tables, Base
from shared.models import BaseEntity

# Re-export shared components
__all__ = [
    "get_session",
    "create_tables", 
    "Base",
    "BaseEntity"
]


def initialize_data():
    """Initialize data layer"""
    create_tables()


def get_db_session():
    """Get database session - convenience function"""
    return get_session()
