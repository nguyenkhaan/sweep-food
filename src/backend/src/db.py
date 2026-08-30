"""Async PostgreSQL engine and request-session lifecycle."""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


def build_async_database_url(database_url: str) -> str:
    """Return a PostgreSQL URL that uses SQLAlchemy's asyncpg driver."""
    parsed_url: URL = make_url(database_url)
    if parsed_url.drivername in {"postgres", "postgresql"}:
        return parsed_url.set(drivername="postgresql+asyncpg").render_as_string(
            hide_password=False,
        )
    if parsed_url.drivername != "postgresql+asyncpg":
        raise ValueError(
            "DATABASE_URL must use a PostgreSQL scheme, for example "
            "postgresql+asyncpg://user:password@host:5432/database.",
        )
    return database_url


class DatabaseSessionManager:
    """Own the application-wide async engine and create request sessions."""

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def initialize(self, database_url: str) -> None:
        """Create the engine and verify that the configured database is reachable."""
        if self._engine is not None:
            return

        engine = create_async_engine(
            build_async_database_url(database_url),
            pool_pre_ping=True,
        )
        try:
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except SQLAlchemyError:
            await engine.dispose()
            raise

        self._engine = engine
        self._session_factory = async_sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
        )

    async def close(self) -> None:
        """Dispose the connection pool during application shutdown."""
        engine = self._engine
        self._engine = None
        self._session_factory = None
        if engine is not None:
            await engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield one request-scoped async database session."""
        if self._session_factory is None:
            raise RuntimeError("Database session manager has not been initialized.")
        async with self._session_factory() as session:
            yield session


db_session = DatabaseSessionManager()


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields a request-scoped database session."""
    async with db_session.session() as session:
        yield session
