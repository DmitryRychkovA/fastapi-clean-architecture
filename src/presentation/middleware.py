import time
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import DomainError, StudyNotFoundError

logger = structlog.stdlib.get_logger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


async def request_id_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid4()))
    request.state.request_id = request_id

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    response = await call_next(request)
    response.headers[REQUEST_ID_HEADER] = request_id
    return response


async def request_logging_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 1)

    logger.info(
        "request completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    return response


async def error_handler_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    try:
        return await call_next(request)
    except StudyNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message},
        )
    except DomainError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )
    except Exception:
        logger.exception("unhandled exception")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


def register_middleware(app: FastAPI) -> None:
    # Order matters: outermost middleware runs first.
    # request_id -> logging -> error_handler -> route
    app.middleware("http")(error_handler_middleware)
    app.middleware("http")(request_logging_middleware)
    app.middleware("http")(request_id_middleware)
