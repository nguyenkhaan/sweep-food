"""Alembic migration environment for asynchronous PostgreSQL."""

import asyncio
from logging.config import fileConfig

from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import context
from src.core.setting import DATABASE_URL
from src.db import build_async_database_url
from src.model import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", build_async_database_url(DATABASE_URL))
target_metadata = Base.metadata


def _get_database_url() -> str:
    """Return the Alembic database URL after verifying it is configured."""
    configured_url = config.get_main_option("sqlalchemy.url")
    if configured_url is None:
        raise RuntimeError("Alembic database URL must be configured")
    return configured_url


database_url = _get_database_url()


def run_migrations_offline() -> None:
    """Run migrations without creating an application database connection."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Configure Alembic with an async connection's synchronous proxy."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine only for this migration command."""
    connectable: AsyncEngine = create_async_engine(
        database_url,
        pool_pre_ping=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations against the configured Neon development/test database."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
