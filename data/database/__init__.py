"""
Database initialization module
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config.settings import settings

logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()

# Global database variables
engine = None
SessionLocal = None

async def init_database():
    """Initialize the database connection"""
    global engine, SessionLocal
    
    try:
        # Create async engine
        engine = create_async_engine(
            settings.database_url,
            echo=settings.debug
        )
        
        # Create async session maker
        SessionLocal = async_sessionmaker(
            engine, 
            expire_on_commit=False
        )
        
        # Create tables if they don't exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
        
async def get_database():
    """Get database session"""
    if SessionLocal is None:
        await init_database()
    
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
