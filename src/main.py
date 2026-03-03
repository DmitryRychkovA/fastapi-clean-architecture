import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import settings
from src.infrastructure.broker.connection import init_broker, shutdown_broker
from src.infrastructure.cache.redis import close_redis
from src.logging_config import configure_logging
from src.presentation.api.router import api_router
from src.presentation.middleware import register_middleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting %s (env=%s)", settings.project_name, settings.app_env)
    if not settings.testing:
        init_broker(app)
    yield
    if not settings.testing:
        await shutdown_broker(app)
    await close_redis()
    logger.info("Shutting down %s", settings.project_name)


def create_app() -> FastAPI:
    if not settings.testing:
        configure_logging()

    app = FastAPI(
        title=settings.project_name,
        description="API for managing medical study metadata",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    register_middleware(app)
    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_app()
