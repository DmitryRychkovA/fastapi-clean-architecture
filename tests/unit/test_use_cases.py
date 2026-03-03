from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dto.study_dto import CreateStudyRequest, StudyResponse, UpdateStudyRequest
from src.application.use_cases.create_study import CreateStudyUseCase
from src.application.use_cases.delete_study import DeleteStudyUseCase
from src.application.use_cases.get_study import GetStudyUseCase
from src.application.use_cases.list_studies import ListStudiesUseCase
from src.application.use_cases.update_study import UpdateStudyUseCase
from src.domain.entities.study import Modality, Study, StudyStatus
from src.domain.exceptions import StudyNotFoundError


class TestCreateStudyUseCase:
    @pytest.mark.asyncio
    async def test_creates_study(self):
        mock_repo = AsyncMock()
        mock_repo.create.return_value = Study(
            patient_id="PAT-001",
            modality=Modality.CT,
            description="Chest CT scan",
        )

        use_case = CreateStudyUseCase(mock_repo)
        request = CreateStudyRequest(
            patient_id="PAT-001",
            modality=Modality.CT,
            description="Chest CT scan",
        )
        result = await use_case.execute(request)

        assert result.patient_id == "PAT-001"
        assert result.modality == Modality.CT
        mock_repo.create.assert_called_once()


class TestGetStudyUseCase:
    @pytest.mark.asyncio
    async def test_returns_study(self):
        study_id = uuid4()
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = Study(
            id=study_id,
            patient_id="PAT-002",
            modality=Modality.MRI,
            description="Brain MRI",
        )

        use_case = GetStudyUseCase(mock_repo)
        result = await use_case.execute(study_id)

        assert result.patient_id == "PAT-002"

    @pytest.mark.asyncio
    async def test_raises_not_found(self):
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None

        use_case = GetStudyUseCase(mock_repo)
        with pytest.raises(StudyNotFoundError):
            await use_case.execute(uuid4())


class TestUpdateStudyUseCase:
    @pytest.mark.asyncio
    async def test_updates_study(self):
        study_id = uuid4()
        existing = Study(
            id=study_id,
            patient_id="PAT-001",
            modality=Modality.CT,
            description="Original",
        )
        updated = Study(
            id=study_id,
            patient_id="PAT-001",
            modality=Modality.CT,
            description="Updated",
        )
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = existing
        mock_repo.update.return_value = updated

        use_case = UpdateStudyUseCase(mock_repo)
        request = UpdateStudyRequest(description="Updated")
        result = await use_case.execute(study_id, request)

        assert result.description == "Updated"
        mock_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_updates_status_and_image_count(self):
        study_id = uuid4()
        existing = Study(
            id=study_id,
            patient_id="PAT-001",
            modality=Modality.CT,
            description="CT scan",
        )
        updated = Study(
            id=study_id,
            patient_id="PAT-001",
            modality=Modality.CT,
            description="CT scan",
            status=StudyStatus.COMPLETED,
            image_count=42,
        )
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = existing
        mock_repo.update.return_value = updated

        use_case = UpdateStudyUseCase(mock_repo)
        request = UpdateStudyRequest(status=StudyStatus.COMPLETED, image_count=42)
        result = await use_case.execute(study_id, request)

        assert result.status == StudyStatus.COMPLETED
        assert result.image_count == 42

    @pytest.mark.asyncio
    async def test_raises_not_found(self):
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None

        use_case = UpdateStudyUseCase(mock_repo)
        request = UpdateStudyRequest(description="Updated")
        with pytest.raises(StudyNotFoundError):
            await use_case.execute(uuid4(), request)


class TestStudyResponseDTO:
    def test_from_entity(self):
        study = Study(
            patient_id="PAT-001",
            modality=Modality.CT,
            description="CT scan",
            image_count=10,
        )
        response = StudyResponse.from_entity(study)
        assert response.id == study.id
        assert response.patient_id == study.patient_id
        assert response.modality == study.modality
        assert response.image_count == 10


class TestListStudiesUseCase:
    @pytest.mark.asyncio
    async def test_returns_paginated_list(self):
        studies = [
            Study(patient_id="PAT-001", modality=Modality.CT, description="Study 1"),
            Study(patient_id="PAT-002", modality=Modality.MRI, description="Study 2"),
        ]
        mock_repo = AsyncMock()
        mock_repo.list_all.return_value = studies
        mock_repo.count.return_value = 2

        use_case = ListStudiesUseCase(mock_repo)
        result = await use_case.execute(offset=0, limit=20)

        assert len(result.items) == 2
        assert result.total == 2
        assert result.offset == 0
        assert result.limit == 20


class TestDeleteStudyUseCase:
    @pytest.mark.asyncio
    async def test_deletes_study(self):
        mock_repo = AsyncMock()
        mock_repo.delete.return_value = True

        use_case = DeleteStudyUseCase(mock_repo)
        await use_case.execute(uuid4())
        mock_repo.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_not_found(self):
        mock_repo = AsyncMock()
        mock_repo.delete.return_value = False

        use_case = DeleteStudyUseCase(mock_repo)
        with pytest.raises(StudyNotFoundError):
            await use_case.execute(uuid4())
