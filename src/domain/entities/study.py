"""Core domain entity representing a medical imaging study."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class Modality(StrEnum):
    """Supported medical imaging modalities."""

    CT = "CT"
    MRI = "MRI"
    XRAY = "X-RAY"
    ULTRASOUND = "US"
    PET = "PET"


class StudyStatus(StrEnum):
    """Lifecycle status of a medical study."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Study:
    """Medical imaging study with lifecycle management."""

    patient_id: str
    modality: Modality
    description: str
    id: UUID = field(default_factory=uuid4)
    status: StudyStatus = StudyStatus.PENDING
    image_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def start_processing(self) -> None:
        self.status = StudyStatus.IN_PROGRESS
        self.updated_at = datetime.now(UTC)

    def complete(self, image_count: int) -> None:
        self.status = StudyStatus.COMPLETED
        self.image_count = image_count
        self.updated_at = datetime.now(UTC)

    def fail(self) -> None:
        self.status = StudyStatus.FAILED
        self.updated_at = datetime.now(UTC)
