"""Generic async CRUD repository for SQLAlchemy models.

Provides reusable database operations so concrete repositories only need
to define model-specific queries and entity mapping.
"""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelT = TypeVar("ModelT", bound=DeclarativeBase)
EntityT = TypeVar("EntityT")


class BaseRepository(Generic[ModelT, EntityT]):
    """Generic async repository with common CRUD operations.

    Subclasses must set ``_model`` and implement ``_to_entity``.
    """

    _model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Read ──────────────────────────────────────────────────

    async def _get_by_id(self, entry_id: UUID) -> ModelT | None:
        result = await self._session.execute(
            select(self._model).where(self._model.id == entry_id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def _get_multi(
        self,
        query: Select,  # type: ignore[type-arg]
        offset: int = 0,
        limit: int = 20,
    ) -> list[ModelT]:
        result = await self._session.execute(query.offset(offset).limit(limit))
        return list(result.scalars().all())

    async def _count(self, query: Select | None = None) -> int:  # type: ignore[type-arg]
        if query is None:
            query = select(func.count(self._model.id))  # type: ignore[attr-defined]
        result = await self._session.execute(query)
        count: int = result.scalar_one()
        return count

    # ── Write ─────────────────────────────────────────────────

    async def _create(self, model: ModelT) -> ModelT:
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model

    async def _update(self, model: ModelT) -> ModelT:
        await self._session.commit()
        await self._session.refresh(model)
        return model

    async def _delete(self, entry_id: UUID) -> bool:
        result = await self._session.execute(
            sa_delete(self._model).where(self._model.id == entry_id)  # type: ignore[attr-defined]
        )
        await self._session.commit()
        row_count: int = result.rowcount  # type: ignore[attr-defined]
        return row_count > 0

    # ── Abstract ──────────────────────────────────────────────

    @staticmethod
    def _to_entity(model: ModelT) -> EntityT:
        raise NotImplementedError
