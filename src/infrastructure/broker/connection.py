import logging

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractRobustConnection
from aio_pika.pool import Pool
from fastapi import FastAPI

from src.config import settings

logger = logging.getLogger(__name__)


async def _get_connection() -> AbstractRobustConnection:
    return await aio_pika.connect_robust(settings.rabbitmq_url)


def init_broker(app: FastAPI) -> None:
    """Initialize RabbitMQ connection and channel pools, attach to app state."""
    connection_pool: Pool = Pool(_get_connection, max_size=settings.rabbit_pool_size)  # type: ignore[type-arg]

    async def _get_channel() -> AbstractChannel:
        async with connection_pool.acquire() as connection:
            return await connection.channel()  # type: ignore[no-any-return]

    channel_pool: Pool = Pool(_get_channel, max_size=settings.rabbit_channel_pool_size)  # type: ignore[type-arg]

    app.state.rmq_pool = connection_pool
    app.state.rmq_channel_pool = channel_pool
    logger.info("RabbitMQ broker initialized (pool=%s, channels=%s)",
                settings.rabbit_pool_size, settings.rabbit_channel_pool_size)


async def shutdown_broker(app: FastAPI) -> None:
    """Gracefully close all RabbitMQ connections."""
    if hasattr(app.state, "rmq_channel_pool"):
        await app.state.rmq_channel_pool.close()
    if hasattr(app.state, "rmq_pool"):
        await app.state.rmq_pool.close()
    logger.info("RabbitMQ broker shut down")
