"""Database Configuration and Connection Management."""

from collections.abc import Generator

from sqlalchemy import MetaData, create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import get_shared_config


# Get configuration
settings = get_shared_config()

# Ensure database directory exists
DATABASE_DIR = settings.data_dir / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Database URL with proper configuration
if settings.database_url.startswith("sqlite"):
    DATABASE_URL = f"sqlite:///{DATABASE_DIR}/surgify.db"
else:
    DATABASE_URL = settings.database_url

# Create engine with environment-specific configuration
engine_kwargs = {
    "echo": settings.debug_mode,
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update(
        {
            "poolclass": StaticPool,
            "connect_args": {"check_same_thread": False, "timeout": 20},
        }
    )

engine = create_engine(DATABASE_URL, **engine_kwargs)

# Enable WAL mode for SQLite for better concurrency
if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=1000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()


# Session configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """Database dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)


def reset_database() -> None:
    """Reset database by dropping and recreating tables."""
    drop_tables()
    create_tables()
