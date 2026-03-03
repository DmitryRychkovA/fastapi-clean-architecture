from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.entities.study import Modality, StudyStatus

if TYPE_CHECKING:
    from src.domain.entities.study import Study


class CreateStudyRequest(BaseModel):
    patient_id: str = Field(..., min_length=1, max_length=64, examples=["PAT-001"])
    modality: Modality = Field(..., examples=[Modality.CT])
    description: str = Field(..., min_length=1, max_length=500, examples=["Chest CT scan"])


class UpdateStudyRequest(BaseModel):
    description: str | None = Field(None, min_length=1, max_length=500)
    status: StudyStatus | None = None
    image_count: int | None = Field(None, ge=0)


class StudyResponse(BaseModel):
    id: UUID
    patient_id: str
    modality: Modality
    description: str
    status: StudyStatus
    image_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_entity(cls, study: Study) -> StudyResponse:
        return cls(
            id=study.id,
            patient_id=study.patient_id,
            modality=study.modality,
            description=study.description,
            status=study.status,
            image_count=study.image_count,
            created_at=study.created_at,
            updated_at=study.updated_at,
        )


class PaginatedResponse(BaseModel):
    items: list[StudyResponse]
    total: int
    offset: int
    limit: int
