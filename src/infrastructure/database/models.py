import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.domain.entities.study import Modality, StudyStatus


class Base(DeclarativeBase):
    pass


class StudyModel(Base):
    """SQLAlchemy ORM model for the ``studies`` table."""

    __tablename__ = "studies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    modality: Mapped[Modality] = mapped_column(
        Enum(Modality, name="modality_enum"), nullable=False
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[StudyStatus] = mapped_column(
        Enum(StudyStatus, name="study_status_enum"),
        nullable=False,
        default=StudyStatus.PENDING,
    )
    image_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
