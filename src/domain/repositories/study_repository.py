from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.study import Modality, Study, StudyStatus


class StudyRepository(ABC):
    """Abstract repository interface for Study persistence operations."""

    @abstractmethod
    async def create(self, study: Study) -> Study:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, study_id: UUID) -> Study | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(
        self,
        offset: int = 0,
        limit: int = 20,
        patient_id: str | None = None,
        modality: Modality | None = None,
        status: StudyStatus | None = None,
    ) -> list[Study]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, study: Study) -> Study:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, study_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def count(
        self,
        patient_id: str | None = None,
        modality: Modality | None = None,
        status: StudyStatus | None = None,
    ) -> int:
        raise NotImplementedError
