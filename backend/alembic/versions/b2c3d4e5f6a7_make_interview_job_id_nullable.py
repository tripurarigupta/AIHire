"""make interview_sessions.job_id nullable

General mock interviews (no job selected) are a supported flow — the API
schema allows job_id=null — but the column was NOT NULL, so saving those
sessions crashed with a 500. Align the schema with the contract.

Revision ID: b2c3d4e5f6a7
Revises: f6ac375b0143
Create Date: 2026-09-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'f6ac375b0143'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'interview_sessions',
        'job_id',
        existing_type=sa.UUID(),
        nullable=True,
    )


def downgrade() -> None:
    # Refuse implicitly if NULL rows exist; delete them first to downgrade.
    op.execute("DELETE FROM interview_sessions WHERE job_id IS NULL")
    op.alter_column(
        'interview_sessions',
        'job_id',
        existing_type=sa.UUID(),
        nullable=False,
    )
