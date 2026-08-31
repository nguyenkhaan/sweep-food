"""FastAPI application factory and runtime lifespan."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.exceptions import RedisError

from src.core.exceptions import register_exception_handlers
from src.core.openapi import BearerOpenAPIFastAPI
from src.core.setting import DATABASE_URL, REDIS_URL, get_env_var
from src.db import db_session
from src.module.auth.auth_router import auth_router
from src.module.catalog.catalog_router import catalog_router
from src.module.cooking.cooking_route import cooking_router
from src.module.health.health_router import health_router
from src.module.recipes.recipe_router import recipe_router
from src.module.user.user_router import user_router
from src.service.redis_service import redis_service

APP_NAME = "Sweep Food API"
APP_VERSION = "0.1.0"
API_PREFIX = "/api"


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Open the database before serving requests and close it at shutdown."""
    await db_session.initialize(DATABASE_URL)
    try:
        await redis_service.initialize(REDIS_URL)
    except (RedisError, ValueError):
        await db_session.close()
        raise

    application.state.db_session = db_session
    print("Database connected")
    application.state.redis_service = redis_service
    print("Redis connected")
    try:
        yield
    finally:
        await redis_service.close()
        print("Redis closed")
        await db_session.close()
        print("Database closed")


def create_app() -> FastAPI:
    """Create the configured Sweep Food API application."""
    application = BearerOpenAPIFastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description="Sweep Food backend API.",
        lifespan=lifespan,
    )
    application.state.environment = get_env_var("ENV", "dev")
    register_exception_handlers(application)
    application.include_router(health_router, prefix=API_PREFIX)
    application.include_router(auth_router, prefix=API_PREFIX)
    application.include_router(catalog_router, prefix=API_PREFIX)
    application.include_router(recipe_router, prefix=API_PREFIX)
    application.include_router(cooking_router, prefix=API_PREFIX)
    application.include_router(user_router, prefix=API_PREFIX)
    return application


app = create_app()
