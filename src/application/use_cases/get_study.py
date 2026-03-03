from uuid import UUID

from src.application.dto.study_dto import StudyResponse
from src.domain.exceptions import StudyNotFoundError
from src.domain.repositories.study_repository import StudyRepository


class GetStudyUseCase:
    """Retrieve a single study by its ID."""

    def __init__(self, repository: StudyRepository) -> None:
        self._repository = repository

    async def execute(self, study_id: UUID) -> StudyResponse:
        study = await self._repository.get_by_id(study_id)
        if study is None:
            raise StudyNotFoundError(study_id)
        return StudyResponse.from_entity(study)
