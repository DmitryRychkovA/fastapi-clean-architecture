"""Worker entry point — runs async consumers in an exception-aware event loop.

Usage:
    python -m src.workers.main
"""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from typing import Any

from src.logging_config import configure_logging
from src.workers.consumer import base_consumer
from src.workers.study_events import (
    EXCHANGE_NAME,
    QUEUE_STUDY_CREATED,
    QUEUE_STUDY_UPDATED,
    ROUTING_KEY_CREATED,
    ROUTING_KEY_UPDATED,
    on_study_created,
    on_study_updated,
)

logger = logging.getLogger(__name__)

AsyncFn = Callable[..., Coroutine[Any, Any, None]]
WorkerEntry = tuple[AsyncFn, str, tuple[Any, ...], dict[str, Any]]
WorkerPayload = list[WorkerEntry]


async def exception_aware_scheduler(payload: WorkerPayload) -> None:
    """Run multiple async consumers, restart them on failure."""
    tasks: dict[asyncio.Task[None], WorkerEntry] = {
        asyncio.create_task(fn(*args, **kwargs), name=name): (fn, name, args, kwargs)
        for fn, name, args, kwargs in payload
    }

    while tasks:
        done, _pending = await asyncio.wait(
            tasks.keys(),
            return_when=asyncio.FIRST_EXCEPTION,
        )
        for task in done:
            fn, name, args, kwargs = tasks.pop(task)
            if task.exception() is not None:
                logger.error("Worker %s crashed: %s — restarting", name, task.exception())
            else:
                logger.warning("Worker %s exited cleanly — restarting", name)
            tasks[asyncio.create_task(fn(*args, **kwargs), name=name)] = (fn, name, args, kwargs)
        await asyncio.sleep(1)


def main() -> None:
    configure_logging()
    logger.info("Starting workers...")

    workers: WorkerPayload = [
        (
            base_consumer,
            "study_created_consumer",
            (EXCHANGE_NAME, QUEUE_STUDY_CREATED, ROUTING_KEY_CREATED, on_study_created),
            {},
        ),
        (
            base_consumer,
            "study_updated_consumer",
            (EXCHANGE_NAME, QUEUE_STUDY_UPDATED, ROUTING_KEY_UPDATED, on_study_updated),
            {},
        ),
    ]

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(exception_aware_scheduler(workers))
    except KeyboardInterrupt:
        logger.info("Workers stopped by user")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
