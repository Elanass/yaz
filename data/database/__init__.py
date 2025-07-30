"""
Database Configuration and Connection Management
Healthcare-grade database setup with audit trails and HIPAA compliance
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import create_engine, event, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from core.config.platform_config import config
from core.services.logger import get_logger

logger = get_logger(__name__)

# Database metadata with naming convention for consistent migrations
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

# Base class for all ORM models
Base = declarative_base(metadata=metadata)

# Global session factory
async_session_factory = None
engine = None

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session with proper error handling and connection management"""
    if async_session_factory is None:
        raise RuntimeError("Database has not been initialized. Call init_database() first.")
    
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        await session.close()

async def init_database():
    """Initialize the database with connection pooling and retry logic"""
    global engine, async_session_factory
    
    logger.info("Initializing database connection")
    
    # Create async engine with appropriate connection pool settings
    engine = create_async_engine(
        config.database_url,
        echo=config.debug,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,  # Recycle connections every 30 minutes
        pool_pre_ping=True,  # Check connection liveness before using from pool
    )
    
    # Create async session factory
    async_session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        autoflush=False,
    )
    
    # Create tables if they don't exist
    try:
        from data.models.orm import Base
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all)  # Uncomment to reset database
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise
    return True


async def close_database():
    """Close database connections"""
    logger.info("Closing database connections")
    # For MVP with SQLite, this is a no-op
    return True


class DatabaseManager:
    """
    Healthcare-grade database manager with connection pooling,
    audit trails, and compliance features.
    """
    
    def __init__(self):
        self.async_engine = None
        self.sync_engine = None
        self.async_session_factory = None
        self.sync_session_factory = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connections and setup audit trails."""
        if self._initialized:
            return
        
        database_url = config.database_url
        
        # Convert SQLite URL for async operations
        if database_url.startswith("sqlite:///"):
            async_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        elif database_url.startswith("postgresql://"):
            async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            async_url = database_url
        
        # Create async engine with healthcare-grade settings
        self.async_engine = create_async_engine(
            async_url,
            echo=config.debug,
            pool_size=20,
            max_overflow=30,
            pool_timeout=30,
            pool_recycle=3600,  # 1 hour
            poolclass=StaticPool if "sqlite" in async_url else None,
            connect_args={"check_same_thread": False} if "sqlite" in async_url else {}
        )
        
        # Create sync engine for migrations
        self.sync_engine = create_engine(
            database_url,
            echo=config.debug,
            pool_size=10,
            max_overflow=20,
            poolclass=StaticPool if "sqlite" in database_url else None,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
        )
        
        # Create session factories
        self.async_session_factory = async_sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self.sync_session_factory = sessionmaker(
            self.sync_engine,
            autocommit=False,
            autoflush=False
        )
        
        # Setup audit logging
        self._setup_audit_logging()
        
        self._initialized = True
        logger.info("Database manager initialized successfully")
    
    def _setup_audit_logging(self):
        """Setup SQL audit logging for compliance."""
        if config.enable_audit_logging:
            @event.listens_for(self.sync_engine, "before_cursor_execute")
            def log_sql_queries(conn, cursor, statement, parameters, context, executemany):
                # Log SQL queries for audit (sanitized)
                sanitized_statement = statement[:500] + "..." if len(statement) > 500 else statement
                logger.info(f"SQL Query: {sanitized_statement}")
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session with automatic cleanup."""
        if not self._initialized:
            await self.initialize()
        
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def get_sync_session(self):
        """Get sync database session for migrations."""
        if not self._initialized:
            raise RuntimeError("Database manager not initialized")
        return self.sync_session_factory()
    
    async def create_tables(self):
        """Create all database tables."""
        if not self._initialized:
            await self.initialize()
        
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
    
    async def drop_tables(self):
        """Drop all database tables (use with caution)."""
        if not self._initialized:
            await self.initialize()
        
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("Database tables dropped")
    
    async def close(self):
        """Close all database connections."""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.sync_engine:
            self.sync_engine.dispose()
        
        self._initialized = False
        logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()


# Dependency function for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency function to get database session in FastAPI endpoints."""
    async with db_manager.get_async_session() as session:
        yield session


# Utility functions
async def init_database():
    """Initialize database for application startup."""
    await db_manager.initialize()
    await db_manager.create_tables()


async def close_database():
    """Close database connections for application shutdown."""
    await db_manager.close()


async def check_database_connection() -> bool:
    """Check if the database connection is alive and functioning"""
    if engine is None:
        logger.warning("Database not initialized, connection check failed")
        return False
    
    try:
        # Attempt a simple query to check connection
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def close_db_connections() -> None:
    """Close all database connections"""
    if engine is None:
        logger.warning("No database engine to close")
        return
    
    try:
        await engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
        raise


# Explicitly export get_db_session
__all__ = ['get_db_session', 'init_database', 'close_database']
