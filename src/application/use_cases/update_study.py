import logging
from uuid import UUID

from src.application.dto.study_dto import StudyResponse, UpdateStudyRequest
from src.domain.exceptions import StudyNotFoundError
from src.domain.repositories.study_repository import StudyRepository

logger = logging.getLogger(__name__)


class UpdateStudyUseCase:
    """Apply partial updates to an existing study."""

    def __init__(self, repository: StudyRepository) -> None:
        self._repository = repository

    async def execute(self, study_id: UUID, request: UpdateStudyRequest) -> StudyResponse:
        study = await self._repository.get_by_id(study_id)
        if study is None:
            raise StudyNotFoundError(study_id)

        if request.description is not None:
            study.description = request.description
        if request.status is not None:
            study.status = request.status
        if request.image_count is not None:
            study.image_count = request.image_count

        updated = await self._repository.update(study)
        logger.info("Study updated: %s", updated.id)
        return StudyResponse.from_entity(updated)
