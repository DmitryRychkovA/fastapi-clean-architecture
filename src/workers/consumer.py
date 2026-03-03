"""Base consumer pattern for RabbitMQ message processing."""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from typing import Any

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from src.config import settings

logger = logging.getLogger(__name__)


async def base_consumer(
    exchange_name: str,
    queue_name: str,
    routing_key: str,
    callback: Callable[[AbstractIncomingMessage], Coroutine[Any, Any, None]],
) -> None:
    """Connect to RabbitMQ, declare exchange/queue, and consume messages."""
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(
            name=exchange_name,
            durable=True,
        )
        queue = await channel.declare_queue(
            name=queue_name,
            durable=True,
        )
        await queue.bind(exchange=exchange, routing_key=routing_key)
        await queue.consume(callback)

        logger.info("Consuming [%s] from exchange=%s, routing_key=%s",
                     queue_name, exchange_name, routing_key)
        await asyncio.Future()  # run indefinitely
