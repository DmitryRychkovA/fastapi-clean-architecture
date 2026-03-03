"""Worker handlers for study-related RabbitMQ events.

Example: when an external service creates a task linked to a study,
this worker picks up the message and processes it.
"""

import json
import logging

from aio_pika.abc import AbstractIncomingMessage

from src.infrastructure.cache.redis import cache_invalidate, close_redis, get_redis

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "study.events"
QUEUE_STUDY_CREATED = "study.created.worker"
ROUTING_KEY_CREATED = "study.created"
QUEUE_STUDY_UPDATED = "study.updated.worker"
ROUTING_KEY_UPDATED = "study.updated"


async def on_study_created(message: AbstractIncomingMessage) -> None:
    """Handle study creation events from external services."""
    async with message.process():
        try:
            data = json.loads(message.body)
            logger.info("Received study.created event: study_id=%s", data.get("study_id"))
        except json.JSONDecodeError:
            logger.error("Invalid JSON in study.created message")
            return

        # Invalidate list cache when a new study is created
        async for redis in get_redis():
            if redis is not None:
                await cache_invalidate(redis, "studies:list:*")
        await close_redis()


async def on_study_updated(message: AbstractIncomingMessage) -> None:
    """Handle study update events — invalidate caches, trigger downstream actions."""
    async with message.process():
        try:
            data = json.loads(message.body)
            study_id = data.get("study_id")
            logger.info("Received study.updated event: study_id=%s", study_id)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in study.updated message")
            return

        # Invalidate specific study cache and list caches
        async for redis in get_redis():
            if redis is not None:
                await cache_invalidate(redis, f"studies:detail:{study_id}")
                await cache_invalidate(redis, "studies:list:*")
        await close_redis()
