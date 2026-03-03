"""API router — all study endpoints and health check."""

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.study_dto import (
    CreateStudyRequest,
    PaginatedResponse,
    StudyResponse,
    UpdateStudyRequest,
)
from src.application.use_cases.create_study import CreateStudyUseCase
from src.application.use_cases.delete_study import DeleteStudyUseCase
from src.application.use_cases.get_study import GetStudyUseCase
from src.application.use_cases.list_studies import ListStudiesUseCase
from src.application.use_cases.update_study import UpdateStudyUseCase
from src.domain.entities.study import Modality, StudyStatus
from src.presentation.api.dependencies import (
    get_create_study_use_case,
    get_delete_study_use_case,
    get_get_study_use_case,
    get_list_studies_use_case,
    get_redis,
    get_session,
    get_update_study_use_case,
)

logger = logging.getLogger(__name__)

api_router = APIRouter()

NOT_FOUND_RESPONSE: dict[int | str, dict[str, Any]] = {404: {"description": "Study not found"}}


@api_router.get(
    "/health",
    tags=["health"],
    responses={
        200: {
            "description": "Service health status",
            "content": {
                "application/json": {
                    "example": {"status": "ok", "db": "connected"},
                }
            },
        },
    },
)
async def health_check(
    session: AsyncSession = Depends(get_session),
    cache: Redis | None = Depends(get_redis),
) -> dict[str, str]:
    result: dict[str, str] = {"status": "ok"}
    try:
        await session.execute(text("SELECT 1"))
        result["db"] = "connected"
    except SQLAlchemyError:
        logger.warning("Health check: database is unavailable")
        result["status"] = "degraded"
        result["db"] = "unavailable"
    try:
        if cache is not None:
            await cache.ping()  # type: ignore[misc]
            result["cache"] = "connected"
        else:
            result["cache"] = "unavailable"
    except Exception:
        result["cache"] = "unavailable"
    return result


@api_router.post(
    "/studies",
    response_model=StudyResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["studies"],
    responses={422: {"description": "Validation error"}},
)
async def create_study(
    request: CreateStudyRequest,
    use_case: CreateStudyUseCase = Depends(get_create_study_use_case),
) -> StudyResponse:
    return await use_case.execute(request)


@api_router.get(
    "/studies",
    response_model=PaginatedResponse,
    tags=["studies"],
)
async def list_studies(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    patient_id: str | None = Query(None, description="Filter by patient ID"),
    modality: Modality | None = Query(None, description="Filter by modality"),
    study_status: StudyStatus | None = Query(None, alias="status", description="Filter by status"),
    use_case: ListStudiesUseCase = Depends(get_list_studies_use_case),
) -> PaginatedResponse:
    return await use_case.execute(
        offset=offset,
        limit=limit,
        patient_id=patient_id,
        modality=modality,
        status=study_status,
    )


@api_router.get(
    "/studies/{study_id}",
    response_model=StudyResponse,
    tags=["studies"],
    responses=NOT_FOUND_RESPONSE,
)
async def get_study(
    study_id: UUID,
    use_case: GetStudyUseCase = Depends(get_get_study_use_case),
) -> StudyResponse:
    return await use_case.execute(study_id)


@api_router.patch(
    "/studies/{study_id}",
    response_model=StudyResponse,
    tags=["studies"],
    responses=NOT_FOUND_RESPONSE,
)
async def update_study(
    study_id: UUID,
    request: UpdateStudyRequest,
    use_case: UpdateStudyUseCase = Depends(get_update_study_use_case),
) -> StudyResponse:
    return await use_case.execute(study_id, request)


@api_router.delete(
    "/studies/{study_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["studies"],
    responses=NOT_FOUND_RESPONSE,
)
async def delete_study(
    study_id: UUID,
    use_case: DeleteStudyUseCase = Depends(get_delete_study_use_case),
) -> None:
    await use_case.execute(study_id)
