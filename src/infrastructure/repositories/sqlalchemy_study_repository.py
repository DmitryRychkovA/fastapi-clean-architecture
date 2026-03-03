from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.study import Modality, Study, StudyStatus
from src.domain.repositories.study_repository import StudyRepository
from src.infrastructure.database.models import StudyModel
from src.infrastructure.repositories.base import BaseRepository


class SQLAlchemyStudyRepository(BaseRepository[StudyModel, Study], StudyRepository):
    """SQLAlchemy-backed implementation of the StudyRepository interface."""

    _model = StudyModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(self, study: Study) -> Study:
        model = StudyModel(
            id=study.id,
            patient_id=study.patient_id,
            modality=study.modality,
            description=study.description,
            status=study.status,
            image_count=study.image_count,
        )
        created = await self._create(model)
        return self._to_entity(created)

    async def get_by_id(self, study_id: UUID) -> Study | None:
        model = await self._get_by_id(study_id)
        return self._to_entity(model) if model else None

    async def list_all(
        self,
        offset: int = 0,
        limit: int = 20,
        patient_id: str | None = None,
        modality: Modality | None = None,
        status: StudyStatus | None = None,
    ) -> list[Study]:
        query = select(StudyModel).order_by(StudyModel.created_at.desc())
        query = self._apply_filters(query, patient_id, modality, status)
        models = await self._get_multi(query, offset, limit)
        return [self._to_entity(m) for m in models]

    async def update(self, study: Study) -> Study:
        model = await self._get_by_id(study.id)
        if model is None:
            from src.domain.exceptions import StudyNotFoundError

            raise StudyNotFoundError(study.id)

        model.description = study.description
        model.status = study.status
        model.image_count = study.image_count
        updated = await self._update(model)
        return self._to_entity(updated)

    async def delete(self, study_id: UUID) -> bool:
        return await self._delete(study_id)

    async def count(
        self,
        patient_id: str | None = None,
        modality: Modality | None = None,
        status: StudyStatus | None = None,
    ) -> int:
        query = select(func.count(StudyModel.id))
        query = self._apply_filters(query, patient_id, modality, status)
        return await self._count(query)

    @staticmethod
    def _apply_filters(
        query: Select,  # type: ignore[type-arg]
        patient_id: str | None,
        modality: Modality | None,
        status: StudyStatus | None,
    ) -> Select:  # type: ignore[type-arg]
        if patient_id is not None:
            query = query.where(StudyModel.patient_id == patient_id)
        if modality is not None:
            query = query.where(StudyModel.modality == modality)
        if status is not None:
            query = query.where(StudyModel.status == status)
        return query

    @staticmethod
    def _to_entity(model: StudyModel) -> Study:
        return Study(
            id=model.id,
            patient_id=model.patient_id,
            modality=Modality(model.modality),
            description=model.description,
            status=StudyStatus(model.status),
            image_count=model.image_count,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
