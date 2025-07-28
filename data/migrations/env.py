"""
Alembic Environment Configuration
Database migration environment for Gastric ADCI Platform
"""

import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our models and configuration
from data.database import Base
from data.models.orm import *  # Import all ORM models
from core.config.platform_config import config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config_obj = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config_obj.config_file_name is not None:
    fileConfig(config_obj.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Set database URL from environment
config_obj.set_main_option("sqlalchemy.url", config.database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config_obj.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Healthcare-specific migration options
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True,  # For SQLite compatibility
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with database connection"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Healthcare-specific migration options
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True,  # For SQLite compatibility
        # Include table prefix if needed
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter function to determine which database objects to include in migrations.
    
    This can be used to exclude certain tables or columns from autogeneration.
    """
    # Include all objects by default
    # Add any exclusion logic here if needed
    return True


async def run_async_migrations() -> None:
    """Run migrations in async mode"""
    # Convert sync database URL to async for PostgreSQL
    database_url = config.database_url
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    elif database_url.startswith("sqlite:///"):
        database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    
    configuration = config_obj.get_section(config_obj.config_ini_section)
    configuration["sqlalchemy.url"] = database_url
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


# Determine which mode to run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
