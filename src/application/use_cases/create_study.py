import logging

from src.application.dto.study_dto import CreateStudyRequest, StudyResponse
from src.domain.entities.study import Study
from src.domain.repositories.study_repository import StudyRepository

logger = logging.getLogger(__name__)


class CreateStudyUseCase:
    """Create a new medical study and persist it."""

    def __init__(self, repository: StudyRepository) -> None:
        self._repository = repository

    async def execute(self, request: CreateStudyRequest) -> StudyResponse:
        study = Study(
            patient_id=request.patient_id,
            modality=request.modality,
            description=request.description,
        )
        created = await self._repository.create(study)
        logger.info("Study created: %s for patient %s", created.id, created.patient_id)
        return StudyResponse.from_entity(created)
