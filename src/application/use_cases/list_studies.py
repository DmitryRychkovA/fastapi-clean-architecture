from src.application.dto.study_dto import PaginatedResponse, StudyResponse
from src.domain.entities.study import Modality, StudyStatus
from src.domain.repositories.study_repository import StudyRepository


class ListStudiesUseCase:
    """List studies with pagination and optional filtering."""

    def __init__(self, repository: StudyRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        offset: int = 0,
        limit: int = 20,
        patient_id: str | None = None,
        modality: Modality | None = None,
        status: StudyStatus | None = None,
    ) -> PaginatedResponse:
        studies = await self._repository.list_all(
            offset=offset,
            limit=limit,
            patient_id=patient_id,
            modality=modality,
            status=status,
        )
        total = await self._repository.count(
            patient_id=patient_id,
            modality=modality,
            status=status,
        )
        items = [StudyResponse.from_entity(s) for s in studies]
        return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)
