import logging

import aio_pika
from aio_pika.abc import ExchangeType
from aio_pika.pool import Pool

logger = logging.getLogger(__name__)


async def publish_message(
    channel_pool: Pool,  # type: ignore[type-arg]
    exchange_name: str,
    routing_key: str,
    message: str,
    queue_name: str | None = None,
) -> None:
    """Publish a message to RabbitMQ using a channel from the pool."""
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(
            name=exchange_name,
            durable=True,
            type=ExchangeType.DIRECT,
        )
        if queue_name:
            queue = await channel.declare_queue(name=queue_name, durable=True)
            await queue.bind(exchange=exchange_name, routing_key=routing_key)

        await exchange.publish(
            message=aio_pika.Message(
                body=message.encode("utf-8"),
                content_encoding="utf-8",
                content_type="application/json",
            ),
            routing_key=routing_key,
        )
        logger.info("Published to %s [%s]", exchange_name, routing_key)
