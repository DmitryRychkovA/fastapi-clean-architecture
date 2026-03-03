from uuid import UUID


class DomainError(Exception):
    """Base exception for domain layer errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class StudyNotFoundError(DomainError):
    """Raised when a study with the given ID does not exist."""

    def __init__(self, study_id: UUID) -> None:
        super().__init__(f"Study {study_id} not found")
        self.study_id = study_id


class StudyAlreadyExistsError(DomainError):
    """Raised when trying to create a study that already exists."""

    def __init__(self, study_id: UUID) -> None:
        super().__init__(f"Study {study_id} already exists")
        self.study_id = study_id
