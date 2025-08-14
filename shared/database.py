"""
Shared Database Management
Minimal database functionality
"""

import os
from pathlib import Path
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from .config import get_shared_config

# Base model for all apps
Base = declarative_base()

# Global database session
_engine = None
_SessionLocal = None


def get_database_url() -> str:
    """Get database URL from configuration"""
    config = get_shared_config()
    return config.database_url


def init_database() -> None:
    """Initialize database connection"""
    global _engine, _SessionLocal
    
    database_url = get_database_url()
    
    # Ensure data directory exists for SQLite
    if database_url.startswith("sqlite:"):
        db_path = database_url.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    _engine = create_engine(database_url)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_engine():
    """Get database engine"""
    if _engine is None:
        init_database()
    return _engine


def get_session() -> Session:
    """Get database session"""
    if _SessionLocal is None:
        init_database()
    return _SessionLocal()


def get_db():
    """Database dependency for FastAPI"""
    db = get_session()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=get_engine())
