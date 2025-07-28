"""
Database Services
Application-level database management and initialization
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from data.database import db_manager, get_db_session, init_database, close_database
from data.repositories import RepositoryFactory
from core.config.platform_config import config

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    High-level database service for application management
    """
    
    def __init__(self):
        self._initialized = False
        self.repository_factory = None
    
    async def initialize(self):
        """Initialize database service for application startup"""
        if self._initialized:
            return
        
        try:
            logger.info("Initializing database service...")
            
            # Initialize database manager
            await init_database()
            
            # Create repository factory
            self.repository_factory = RepositoryFactory
            
            self._initialized = True
            logger.info("Database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup database connections for application shutdown"""
        try:
            logger.info("Cleaning up database service...")
            await close_database()
            self._initialized = False
            logger.info("Database service cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error cleaning up database service: {e}")
            raise
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session for manual transaction management"""
        async with db_manager.get_async_session() as session:
            yield session
    
    def get_repository_factory(self, session: AsyncSession) -> RepositoryFactory:
        """Get repository factory for a session"""
        return RepositoryFactory(session)
    
    async def health_check(self) -> dict:
        """Check database health status"""
        try:
            async with self.get_session() as session:
                # Simple query to test connectivity
                result = await session.execute("SELECT 1")
                row = result.fetchone()
                
                if row and row[0] == 1:
                    return {
                        "status": "healthy",
                        "database": "connected",
                        "url": config.database_url.split("@")[-1] if "@" in config.database_url else "local"
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "database": "query_failed"
                    }
                    
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "database": "connection_failed",
                "error": str(e)
            }


# Global database service instance
db_service = DatabaseService()


# Dependency functions for FastAPI

async def get_database_service() -> DatabaseService:
    """Dependency to get database service"""
    if not db_service._initialized:
        await db_service.initialize()
    return db_service


async def get_repository_factory(
    session: AsyncSession = get_db_session()
) -> RepositoryFactory:
    """Dependency to get repository factory with session"""
    return RepositoryFactory(session)


# Application lifecycle management

@asynccontextmanager
async def database_lifespan():
    """Context manager for database lifecycle in FastAPI app"""
    try:
        # Startup
        await db_service.initialize()
        logger.info("Database service started")
        yield
    finally:
        # Shutdown
        await db_service.cleanup()
        logger.info("Database service stopped")


# Utility functions

async def create_test_data():
    """Create test data for development (use with caution)"""
    if config.environment == "production":
        raise ValueError("Cannot create test data in production environment")
    
    try:
        async with db_service.get_session() as session:
            repo_factory = db_service.get_repository_factory(session)
            
            # Import test data creation here to avoid circular imports
            from data.test_data import create_sample_patients
            await create_sample_patients(repo_factory)
            
            await session.commit()
            logger.info("Test data created successfully")
            
    except Exception as e:
        logger.error(f"Error creating test data: {e}")
        raise


async def reset_database():
    """Reset database (use with extreme caution)"""
    if config.environment == "production":
        raise ValueError("Cannot reset database in production environment")
    
    try:
        await db_manager.drop_tables()
        await db_manager.create_tables()
        logger.info("Database reset successfully")
        
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise
