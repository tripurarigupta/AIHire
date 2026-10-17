"""store resume files in the database

Revision ID: d8e9f0a1b2c3
Revises: c7d8e9f0a1b2
Create Date: 2026-10-17

Uploaded resumes used to be written to `uploads/resumes` on disk. That cannot
work where the API is deployed: serverless function filesystems are read-only
apart from /tmp, and anything written there disappears with the instance, so a
recruiter's resume download would fail or 404. The bytes now live in
`resume_files` and `resumes.file_path` becomes optional, kept only so rows
uploaded before this change can still be served from disk.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8e9f0a1b2c3'
down_revision: Union[str, Sequence[str], None] = 'c7d8e9f0a1b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'resume_files',
        sa.Column('resume_id', sa.UUID(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('data', sa.LargeBinary(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    # Unique index: one stored file per resume row.
    op.create_index(
        op.f('ix_resume_files_resume_id'),
        'resume_files',
        ['resume_id'],
        unique=True,
    )

    op.alter_column(
        'resumes',
        'file_path',
        existing_type=sa.String(length=500),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema.

    Note: restoring the NOT NULL constraint on `resumes.file_path` fails if any
    resume was uploaded while this revision was applied, because those rows hold
    their bytes here and have no path.
    """
    op.alter_column(
        'resumes',
        'file_path',
        existing_type=sa.String(length=500),
        nullable=False,
    )
    op.drop_index(op.f('ix_resume_files_resume_id'), table_name='resume_files')
    op.drop_table('resume_files')
