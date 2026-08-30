from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.exceptions import register_exception_handlers
from src.core.setting import DATABASE_URL, get_env_var
from src.db import db_session
from src.module.health.health_router import health_router

APP_NAME = "Sweep Food API"
APP_VERSION = "0.1.0"
API_PREFIX = "/api"


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    await db_session.initialize(DATABASE_URL)
    application.state.db_session = db_session
    print('Database connected')
    try:
        yield
    finally:
        print('Database closed')
        await db_session.close()


def create_app() -> FastAPI:
    application = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description="Sweep Food backend API.",
        lifespan=lifespan,
    )
    application.state.environment = get_env_var("ENV", "dev")
    register_exception_handlers(application)
    application.include_router(health_router, prefix=API_PREFIX)
    return application


app = create_app()
