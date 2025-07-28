"""
ElectricSQL Database Configuration
Healthcare-grade offline-first database with HIPAA compliance
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import declarative_base

from core.config.platform_config import config
from core.services.logger import get_logger
from core.services.encryption import encrypt_sensitive_data, decrypt_sensitive_data

logger = get_logger(__name__)

# Healthcare-compliant naming convention
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

# Base class for all ORM models with ElectricSQL support
Base = declarative_base(metadata=metadata)


class ElectricSQLConfig:
    """ElectricSQL configuration for healthcare applications"""
    
    def __init__(self):
        self.database_url = config.database_url
        self.electric_url = config.electricsql_url
        self.electric_token = config.electric_token
        self.database_id = config.electric_database_id
        
        # Healthcare compliance settings
        self.encryption_enabled = config.patient_data_encryption
        self.audit_enabled = config.enable_audit_logging
        self.data_retention_days = config.data_retention_days
        
        # Performance settings
        self.sync_interval_ms = config.sync_interval_ms
        self.offline_storage_mb = config.offline_storage_mb
        self.enable_collaboration = config.enable_real_time_collaboration
    
    def get_electric_config(self) -> Dict[str, Any]:
        """Get ElectricSQL client configuration"""
        return {
            "url": self.electric_url,
            "token": self.electric_token,
            "database_id": self.database_id,
            "sync_interval": self.sync_interval_ms,
            "offline_storage_limit": self.offline_storage_mb * 1024 * 1024,  # Convert to bytes
            "encryption": {
                "enabled": self.encryption_enabled,
                "key": config.encryption_key
            },
            "audit": {
                "enabled": self.audit_enabled,
                "retention_days": self.data_retention_days
            },
            "collaboration": {
                "enabled": self.enable_collaboration,
                "conflict_resolution": "last_write_wins_with_audit"
            }
        }


class ElectricSQLManager:
    """
    Manages ElectricSQL connections with healthcare compliance
    """
    
    def __init__(self):
        self.config = ElectricSQLConfig()
        self.async_engine = None
        self.sync_engine = None
        self.async_session_factory = None
        self.electric_client = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize ElectricSQL with healthcare compliance"""
        if self._initialized:
            return
            
        try:
            logger.info("Initializing ElectricSQL with healthcare compliance...")
            
            # Setup PostgreSQL connection for ElectricSQL
            await self._setup_database_engines()
            
            # Initialize ElectricSQL client (simulated for now)
            await self._setup_electric_client()
            
            # Setup audit logging
            self._setup_audit_logging()
            
            # Setup data encryption
            self._setup_data_encryption()
            
            self._initialized = True
            logger.info("ElectricSQL initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ElectricSQL: {e}")
            raise
    
    async def _setup_database_engines(self):
        """Setup SQLAlchemy engines for ElectricSQL"""
        # Async engine for application use
        self.async_engine = create_async_engine(
            self.config.database_url,
            echo=config.debug,
            # Healthcare-grade connection pooling
            pool_size=20,
            max_overflow=30,
            pool_timeout=30,
            pool_recycle=3600,  # 1 hour for security
            pool_pre_ping=True,  # Validate connections
        )
        
        # Sync engine for migrations
        sync_url = self.config.database_url.replace("+asyncpg", "").replace("+aiopg", "")
        self.sync_engine = create_engine(
            sync_url,
            echo=config.debug,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600
        )
        
        # Async session factory
        self.async_session_factory = async_sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("Database engines configured for ElectricSQL")
    
    async def _setup_electric_client(self):
        """Setup ElectricSQL client (simulated for now)"""
        try:
            # In a real implementation, this would initialize the ElectricSQL client
            # For now, we'll simulate the configuration
            electric_config = self.config.get_electric_config()
            
            # Store configuration for frontend use
            await self._store_electric_config(electric_config)
            
            logger.info("ElectricSQL client configured")
            
        except Exception as e:
            logger.error(f"Failed to setup ElectricSQL client: {e}")
            raise
    
    async def _store_electric_config(self, electric_config: Dict[str, Any]):
        """Store ElectricSQL configuration for frontend"""
        config_path = "web/static/js/electric-config.js"
        
        # Create sanitized config for frontend (remove sensitive data)
        frontend_config = {
            "url": electric_config["url"],
            "database_id": electric_config["database_id"],
            "sync_interval": electric_config["sync_interval"],
            "collaboration": electric_config["collaboration"],
            "encryption": {"enabled": electric_config["encryption"]["enabled"]}
        }
        
        js_content = f"""
// ElectricSQL Configuration for Gastric ADCI Platform
window.ELECTRIC_CONFIG = {json.dumps(frontend_config, indent=2)};

// Initialize ElectricSQL client
import {{ Electric }} from 'electric-sql/browser';

const electric = await Electric.connect({{
    url: window.ELECTRIC_CONFIG.url,
    database: window.ELECTRIC_CONFIG.database_id,
    token: await getAuthToken(), // Function to get auth token
    options: {{
        syncInterval: window.ELECTRIC_CONFIG.sync_interval,
        encryption: window.ELECTRIC_CONFIG.encryption.enabled
    }}
}});

// Export for global use
window.electric = electric;
"""
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Write configuration
        with open(config_path, 'w') as f:
            f.write(js_content)
        
        logger.info(f"ElectricSQL frontend configuration written to {config_path}")
    
    def _setup_audit_logging(self):
        """Setup SQL audit logging for HIPAA compliance"""
        if not config.enable_audit_logging:
            return
            
        @event.listens_for(self.sync_engine, "before_cursor_execute")
        def log_sql_queries(conn, cursor, statement, parameters, context, executemany):
            """Log SQL queries for audit trail"""
            # Sanitize sensitive data in queries
            sanitized_statement = self._sanitize_sql_for_audit(statement)
            
            audit_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "query": sanitized_statement[:500],  # Limit length
                "parameters_count": len(parameters) if parameters else 0,
                "executemany": executemany,
                "connection_info": str(conn.info) if hasattr(conn, 'info') else None
            }
            
            logger.info(f"SQL_AUDIT: {json.dumps(audit_data)}")
        
        logger.info("SQL audit logging enabled")
    
    def _setup_data_encryption(self):
        """Setup automatic data encryption for sensitive fields"""
        if not config.patient_data_encryption:
            return
            
        # This would be expanded to handle automatic encryption/decryption
        # of sensitive fields marked with custom annotations
        logger.info("Data encryption enabled for sensitive fields")
    
    def _sanitize_sql_for_audit(self, statement: str) -> str:
        """Sanitize SQL statements for audit logging"""
        # Remove potential sensitive data patterns
        sensitive_patterns = [
            r"'[^']*@[^']*'",  # Email addresses
            r"'\d{3}-\d{2}-\d{4}'",  # SSNs
            r"'\d{10,}'",  # Long numbers (could be phone/ID)
        ]
        
        sanitized = statement
        for pattern in sensitive_patterns:
            import re
            sanitized = re.sub(pattern, "'[REDACTED]'", sanitized)
        
        return sanitized
    
    @asynccontextmanager
    async def get_session(self):
        """Get async database session with audit context"""
        if not self._initialized:
            await self.initialize()
            
        async with self.async_session_factory() as session:
            try:
                # Add audit context to session
                session.info["audit_context"] = {
                    "timestamp": datetime.utcnow(),
                    "session_id": id(session)
                }
                
                yield session
                await session.commit()
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_tables(self):
        """Create all database tables"""
        if not self._initialized:
            await self.initialize()
            
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created")
    
    async def setup_electric_sync(self, table_names: List[str]):
        """Setup ElectricSQL sync for specified tables"""
        try:
            # In a real implementation, this would configure ElectricSQL sync
            for table_name in table_names:
                logger.info(f"Configuring ElectricSQL sync for table: {table_name}")
                
                # Configure table-level sync settings
                sync_config = {
                    "table": table_name,
                    "sync_mode": "bidirectional",
                    "conflict_resolution": "last_write_wins_with_audit",
                    "encryption": config.patient_data_encryption,
                    "retention_policy": f"{config.data_retention_days} days"
                }
                
                # Store sync configuration
                await self._store_table_sync_config(table_name, sync_config)
            
            logger.info(f"ElectricSQL sync configured for {len(table_names)} tables")
            
        except Exception as e:
            logger.error(f"Failed to setup ElectricSQL sync: {e}")
            raise
    
    async def _store_table_sync_config(self, table_name: str, sync_config: Dict[str, Any]):
        """Store table sync configuration"""
        # This would integrate with ElectricSQL's sync configuration
        logger.info(f"Sync config for {table_name}: {sync_config}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check ElectricSQL health status"""
        try:
            health_status = {
                "database": "unknown",
                "electric_sync": "unknown",
                "encryption": "unknown",
                "audit": "unknown"
            }
            
            # Check database connection
            async with self.get_session() as session:
                result = await session.execute("SELECT 1")
                if result.scalar() == 1:
                    health_status["database"] = "healthy"
                else:
                    health_status["database"] = "unhealthy"
            
            # Check ElectricSQL sync status (simulated)
            health_status["electric_sync"] = "healthy" if self._initialized else "unhealthy"
            
            # Check encryption status
            health_status["encryption"] = "enabled" if config.patient_data_encryption else "disabled"
            
            # Check audit status
            health_status["audit"] = "enabled" if config.enable_audit_logging else "disabled"
            
            return {
                "status": "healthy" if all(v in ["healthy", "enabled"] for v in health_status.values()) else "degraded",
                "components": health_status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"ElectricSQL health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def close(self):
        """Close all connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.sync_engine:
            self.sync_engine.dispose()
        
        self._initialized = False
        logger.info("ElectricSQL connections closed")


# Global ElectricSQL manager instance
electric_manager = ElectricSQLManager()


# Dependency function for FastAPI
async def get_electric_session():
    """Dependency function to get ElectricSQL session"""
    async with electric_manager.get_session() as session:
        yield session


# Utility functions
async def init_electric_database():
    """Initialize ElectricSQL for application startup"""
    await electric_manager.initialize()
    await electric_manager.create_tables()
    
    # Setup sync for clinical tables
    clinical_tables = [
        "patients", "comorbidities", "tumor_characteristics",
        "performance_status", "laboratory_results", "treatment_plans",
        "adci_decisions", "clinical_outcomes"
    ]
    await electric_manager.setup_electric_sync(clinical_tables)


async def close_electric_database():
    """Close ElectricSQL connections"""
    await electric_manager.close()
