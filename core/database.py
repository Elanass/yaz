"""
Database Configuration and Connection Management
"""

import os
from pathlib import Path
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Database configuration
DATABASE_DIR = Path(__file__).parent.parent / "data" / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/surgify.db"

# Create engine with proper configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
        "timeout": 20
    },
    echo=False  # Set to True for SQL logging
)

# Session configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)

def reset_database():
    """Reset database by dropping and recreating tables"""
    drop_tables()
    create_tables()
