import logging
from uuid import UUID

from src.domain.exceptions import StudyNotFoundError
from src.domain.repositories.study_repository import StudyRepository

logger = logging.getLogger(__name__)


class DeleteStudyUseCase:
    """Delete a study by its ID."""

    def __init__(self, repository: StudyRepository) -> None:
        self._repository = repository

    async def execute(self, study_id: UUID) -> None:
        deleted = await self._repository.delete(study_id)
        if not deleted:
            raise StudyNotFoundError(study_id)
        logger.info("Study deleted: %s", study_id)
