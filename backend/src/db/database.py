"""
Database configuration and ElectricsQL integration
"""

import asyncio
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger
import asyncpg

from ..core.config import get_settings

# Database metadata and base
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# Global database variables
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None


async def init_db():
    """Initialize database connections"""
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    settings = get_settings()
    
    try:
        # Create async engine for main application
        async_engine = create_async_engine(
            settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,
            echo=settings.debug,
        )
        
        # Create sync engine for migrations
        engine = create_engine(
            settings.database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,
            echo=settings.debug,
        )
        
        # Create session factories
        AsyncSessionLocal = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        # Test connection
        async with async_engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db():
    """Close database connections"""
    global engine, async_engine
    
    if async_engine:
        await async_engine.dispose()
        logger.info("Async database engine disposed")
    
    if engine:
        engine.dispose()
        logger.info("Sync database engine disposed")


async def get_async_session() -> AsyncSession:
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session():
    """Get sync database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class ElectricsQLIntegration:
    """ElectricsQL integration for offline-first sync"""
    
    def __init__(self):
        self.settings = get_settings()
        self.sync_tables = [
            "users",
            "patients", 
            "clinical_protocols",
            "treatment_plans",
            "decision_results",
            "evidence_records"
        ]
    
    async def setup_electricsql_sync(self):
        """Setup ElectricsQL sync configuration"""
        try:
            # Connect to ElectricsQL sync service
            conn = await asyncpg.connect(self.settings.database_url)
            
            # Enable electric extensions
            await conn.execute("CREATE EXTENSION IF NOT EXISTS electric;")
            
            # Configure sync tables
            for table in self.sync_tables:
                await self._enable_sync_for_table(conn, table)
            
            await conn.close()
            logger.info("ElectricsSQL sync configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup ElectricsSQL sync: {e}")
            raise
    
    async def _enable_sync_for_table(self, conn, table_name: str):
        """Enable sync for a specific table"""
        try:
            # Enable electric sync for table
            await conn.execute(f"SELECT electric.electrify('{table_name}');")
            
            # Add sync metadata columns if not exists
            await conn.execute(f"""
                ALTER TABLE {table_name} 
                ADD COLUMN IF NOT EXISTS _electric_sync_id UUID DEFAULT gen_random_uuid(),
                ADD COLUMN IF NOT EXISTS _electric_sync_timestamp TIMESTAMPTZ DEFAULT NOW(),
                ADD COLUMN IF NOT EXISTS _electric_sync_version INTEGER DEFAULT 1;
            """)
            
            # Create sync trigger
            await conn.execute(f"""
                CREATE OR REPLACE TRIGGER {table_name}_electric_sync_trigger
                BEFORE UPDATE ON {table_name}
                FOR EACH ROW
                EXECUTE FUNCTION electric.update_sync_metadata();
            """)
            
            logger.info(f"Enabled ElectricsSQL sync for table: {table_name}")
            
        except Exception as e:
            logger.warning(f"Failed to enable sync for {table_name}: {e}")
    
    async def trigger_sync(self, table_name: str, record_id: str):
        """Trigger manual sync for specific record"""
        try:
            conn = await asyncpg.connect(self.settings.database_url)
            
            await conn.execute(f"""
                SELECT electric.trigger_sync('{table_name}', '{record_id}');
            """)
            
            await conn.close()
            logger.info(f"Triggered sync for {table_name}:{record_id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger sync: {e}")
    
    async def get_sync_status(self, table_name: str) -> dict:
        """Get sync status for a table"""
        try:
            conn = await asyncpg.connect(self.settings.database_url)
            
            result = await conn.fetchrow(f"""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(*) FILTER (WHERE _electric_sync_timestamp > NOW() - INTERVAL '1 hour') as recent_syncs,
                    MAX(_electric_sync_timestamp) as last_sync
                FROM {table_name};
            """)
            
            await conn.close()
            
            return {
                "table": table_name,
                "total_records": result["total_records"],
                "recent_syncs": result["recent_syncs"],
                "last_sync": result["last_sync"].isoformat() if result["last_sync"] else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get sync status for {table_name}: {e}")
            return {"error": str(e)}


# Global ElectricsQL integration instance
electricsql = ElectricsQLIntegration()


class DatabaseHealth:
    """Database health monitoring"""
    
    @staticmethod
    async def check_connection() -> bool:
        """Check database connection health"""
        try:
            async with async_engine.begin() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    @staticmethod
    async def check_electricsql_sync() -> bool:
        """Check ElectricsQL sync health"""
        try:
            # Check if electric extension is available
            conn = await asyncpg.connect(get_settings().database_url)
            result = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM pg_extension WHERE extname = 'electric'
                );
            """)
            await conn.close()
            return result
        except Exception as e:
            logger.error(f"ElectricsQL health check failed: {e}")
            return False
    
    @staticmethod
    async def get_performance_metrics() -> dict:
        """Get database performance metrics"""
        try:
            conn = await asyncpg.connect(get_settings().database_url)
            
            # Get connection stats
            stats = await conn.fetchrow("""
                SELECT 
                    numbackends as active_connections,
                    xact_commit as committed_transactions,
                    xact_rollback as rolled_back_transactions,
                    blks_read as blocks_read,
                    blks_hit as blocks_hit,
                    tup_returned as tuples_returned,
                    tup_fetched as tuples_fetched,
                    tup_inserted as tuples_inserted,
                    tup_updated as tuples_updated,
                    tup_deleted as tuples_deleted
                FROM pg_stat_database 
                WHERE datname = current_database();
            """)
            
            await conn.close()
            
            return dict(stats) if stats else {}
            
        except Exception as e:
            logger.error(f"Failed to get database metrics: {e}")
            return {}


# Database health instance
db_health = DatabaseHealth()
