"""Reconcile schema to canonical spec

Revision ID: a1b2c3d4e5f6
Revises: 59bdf19fec7c
Create Date: 2026-09-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '59bdf19fec7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Reconcile schema to canonical specification."""

    # 1. CandidateProfile: add phone, address, headline, bio
    op.add_column('candidate_profiles', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('candidate_profiles', sa.Column('address', sa.String(255), nullable=True))
    op.add_column('candidate_profiles', sa.Column('headline', sa.String(200), nullable=True))
    op.add_column('candidate_profiles', sa.Column('bio', sa.Text(), nullable=True))

    # 2. Jobs: add new columns, then rename employment_type → job_type
    op.add_column('jobs', sa.Column('experience_required', sa.String(50), nullable=True))
    op.add_column('jobs', sa.Column('salary', sa.String(50), nullable=True))
    op.add_column('jobs', sa.Column('job_type', sa.String(50), nullable=True))
    op.add_column('jobs', sa.Column('deadline', sa.DateTime(timezone=True), nullable=True))

    # Copy data from employment_type to job_type
    op.execute("UPDATE jobs SET job_type = employment_type WHERE employment_type IS NOT NULL")

    # Drop the old employment_type column
    op.drop_column('jobs', 'employment_type')

    # 3. Resumes: add parsed_skills (JSON), ats_score; rename parsed_text → extracted_text
    op.add_column('resumes', sa.Column('parsed_skills', JSON, nullable=True))
    op.add_column('resumes', sa.Column('ats_score', sa.Float(), nullable=True))
    op.add_column('resumes', sa.Column('extracted_text', sa.Text(), nullable=True))

    # Copy data from parsed_text to extracted_text
    op.execute("UPDATE resumes SET extracted_text = parsed_text WHERE parsed_text IS NOT NULL")

    # Drop the old parsed_text column
    op.drop_column('resumes', 'parsed_text')

    # 4. Drop old interviews table and create interview_sessions
    op.drop_table('interviews')

    op.create_table(
        'interview_sessions',
        sa.Column('candidate_id', UUID(as_uuid=True), sa.ForeignKey('candidate_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_id', UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=False),
        sa.Column('strengths', sa.Text(), nullable=True),
        sa.Column('improvements', sa.Text(), nullable=True),
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 5. Create recommendations table
    op.create_table(
        'recommendations',
        sa.Column('candidate_id', UUID(as_uuid=True), sa.ForeignKey('candidate_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_id', UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('match_percentage', sa.Float(), nullable=True),
        sa.Column('missing_skills', JSON, nullable=True),
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Revert schema reconciliation."""

    # Drop new tables
    op.drop_table('recommendations')
    op.drop_table('interview_sessions')

    # Restore old interviews table
    op.create_table(
        'interviews',
        sa.Column('application_id', UUID(as_uuid=True), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='scheduled'),
        sa.Column('interview_type', sa.String(50), nullable=False, server_default='ai'),
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('application_id'),
    )

    # Restore resumes: add parsed_text back, drop new columns
    op.add_column('resumes', sa.Column('parsed_text', sa.Text(), nullable=True))
    op.execute("UPDATE resumes SET parsed_text = extracted_text WHERE extracted_text IS NOT NULL")
    op.drop_column('resumes', 'extracted_text')
    op.drop_column('resumes', 'ats_score')
    op.drop_column('resumes', 'parsed_skills')

    # Restore jobs: add employment_type back, drop new columns
    op.add_column('jobs', sa.Column('employment_type', sa.String(50), nullable=True))
    op.execute("UPDATE jobs SET employment_type = job_type WHERE job_type IS NOT NULL")
    op.drop_column('jobs', 'deadline')
    op.drop_column('jobs', 'salary')
    op.drop_column('jobs', 'job_type')
    op.drop_column('jobs', 'experience_required')

    # Remove CandidateProfile new columns
    op.drop_column('candidate_profiles', 'bio')
    op.drop_column('candidate_profiles', 'headline')
    op.drop_column('candidate_profiles', 'address')
    op.drop_column('candidate_profiles', 'phone')
