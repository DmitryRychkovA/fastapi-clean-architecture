"""create studies table

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "studies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.String(length=64), nullable=False),
        sa.Column(
            "modality",
            sa.Enum("CT", "MRI", "X-RAY", "US", "PET", name="modality_enum"),
            nullable=False,
        ),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "in_progress", "completed", "failed", name="study_status_enum"),
            nullable=False,
        ),
        sa.Column("image_count", sa.Integer(), nullable=True, default=0),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_studies_patient_id"), "studies", ["patient_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_studies_patient_id"), table_name="studies")
    op.drop_table("studies")
    op.execute("DROP TYPE IF EXISTS modality_enum")
    op.execute("DROP TYPE IF EXISTS study_status_enum")
