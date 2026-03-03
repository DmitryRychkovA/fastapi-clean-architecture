"""Dependency injection wiring for FastAPI.

Maps abstract interfaces (domain layer) to concrete implementations
(infrastructure layer).  Presentation layer imports only from here,
never directly from infrastructure.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.create_study import CreateStudyUseCase
from src.application.use_cases.delete_study import DeleteStudyUseCase
from src.application.use_cases.get_study import GetStudyUseCase
from src.application.use_cases.list_studies import ListStudiesUseCase
from src.application.use_cases.update_study import UpdateStudyUseCase
from src.domain.repositories.study_repository import StudyRepository
from src.infrastructure.cache.redis import get_redis as get_redis
from src.infrastructure.database.connection import get_session as get_session
from src.infrastructure.repositories.sqlalchemy_study_repository import (
    SQLAlchemyStudyRepository,
)


def get_study_repository(
    session: AsyncSession = Depends(get_session),
) -> StudyRepository:
    return SQLAlchemyStudyRepository(session)


def get_create_study_use_case(
    repo: StudyRepository = Depends(get_study_repository),
) -> CreateStudyUseCase:
    return CreateStudyUseCase(repo)


def get_get_study_use_case(
    repo: StudyRepository = Depends(get_study_repository),
) -> GetStudyUseCase:
    return GetStudyUseCase(repo)


def get_list_studies_use_case(
    repo: StudyRepository = Depends(get_study_repository),
) -> ListStudiesUseCase:
    return ListStudiesUseCase(repo)


def get_update_study_use_case(
    repo: StudyRepository = Depends(get_study_repository),
) -> UpdateStudyUseCase:
    return UpdateStudyUseCase(repo)


def get_delete_study_use_case(
    repo: StudyRepository = Depends(get_study_repository),
) -> DeleteStudyUseCase:
    return DeleteStudyUseCase(repo)
