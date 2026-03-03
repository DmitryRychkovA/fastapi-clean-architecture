from uuid import uuid4

from src.domain.entities.study import Modality, Study, StudyStatus
from src.domain.exceptions import DomainError, StudyAlreadyExistsError, StudyNotFoundError


class TestStudyEntity:
    def test_create_study(self):
        study = Study(
            patient_id="PAT-001",
            modality=Modality.CT,
            description="Chest CT scan",
        )
        assert study.patient_id == "PAT-001"
        assert study.modality == Modality.CT
        assert study.status == StudyStatus.PENDING
        assert study.image_count == 0
        assert study.created_at is not None
        assert study.updated_at is not None

    def test_start_processing(self):
        study = Study(
            patient_id="PAT-001",
            modality=Modality.MRI,
            description="Brain MRI",
        )
        study.start_processing()
        assert study.status == StudyStatus.IN_PROGRESS

    def test_complete_study(self):
        study = Study(
            patient_id="PAT-001",
            modality=Modality.CT,
            description="Chest CT scan",
        )
        study.start_processing()
        study.complete(image_count=42)
        assert study.status == StudyStatus.COMPLETED
        assert study.image_count == 42

    def test_fail_study(self):
        study = Study(
            patient_id="PAT-001",
            modality=Modality.XRAY,
            description="Chest X-Ray",
        )
        study.start_processing()
        study.fail()
        assert study.status == StudyStatus.FAILED


class TestDomainExceptions:
    def test_study_not_found_error(self):
        study_id = uuid4()
        error = StudyNotFoundError(study_id)
        assert str(error) == f"Study {study_id} not found"
        assert error.study_id == study_id

    def test_domain_error_is_base(self):
        error = StudyNotFoundError(uuid4())
        assert isinstance(error, DomainError)
        assert isinstance(error, Exception)

    def test_study_already_exists_error(self):
        study_id = uuid4()
        error = StudyAlreadyExistsError(study_id)
        assert str(error) == f"Study {study_id} already exists"
        assert error.study_id == study_id
        assert isinstance(error, DomainError)
