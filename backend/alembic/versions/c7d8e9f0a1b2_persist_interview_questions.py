"""persist interview question sets

`/interviews/evaluate` previously graded against the `question` text sent by
the browser, so a candidate could submit trivially easy questions together
with a canned answer and store a high score on a session recruiters can read.
This adds server-owned storage for the issued questions and links sessions to
it.

The question row UUID doubles as the question id in the API, so the submitted
id *is* the storage key and an invented question cannot resolve.

Revision ID: c7d8e9f0a1b2
Revises: b2c3d4e5f6a7
Create Date: 2026-10-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON


# revision identifiers, used by Alembic.
revision: str = 'c7d8e9f0a1b2'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'interview_question_sets',
        sa.Column('candidate_id', UUID(as_uuid=True), sa.ForeignKey('candidate_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_interview_question_sets_candidate_id'), 'interview_question_sets', ['candidate_id'], unique=False)

    op.create_table(
        'interview_questions',
        sa.Column('question_set_id', UUID(as_uuid=True), sa.ForeignKey('interview_question_sets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='technical'),
        sa.Column('target_skill', sa.String(length=200), nullable=False, server_default=''),
        sa.Column('keywords', JSON, nullable=False, server_default='[]'),
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_interview_questions_question_set_id'), 'interview_questions', ['question_set_id'], unique=False)

    # Nullable: sessions recorded before this table existed still load, they
    # just have no question set to point at.
    op.add_column(
        'interview_sessions',
        sa.Column('question_set_id', UUID(as_uuid=True), nullable=True),
    )
    # Every /evaluate reads questions by set, and Postgres does not index the
    # referencing side of a foreign key on its own.
    op.create_index(op.f('ix_interview_sessions_question_set_id'), 'interview_sessions', ['question_set_id'], unique=False)
    op.create_foreign_key(
        'fk_interview_sessions_question_set_id',
        'interview_sessions',
        'interview_question_sets',
        ['question_set_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_interview_sessions_question_set_id', 'interview_sessions', type_='foreignkey')
    op.drop_index(op.f('ix_interview_sessions_question_set_id'), table_name='interview_sessions')
    op.drop_column('interview_sessions', 'question_set_id')

    op.drop_index(op.f('ix_interview_questions_question_set_id'), table_name='interview_questions')
    op.drop_table('interview_questions')

    op.drop_index(op.f('ix_interview_question_sets_candidate_id'), table_name='interview_question_sets')
    op.drop_table('interview_question_sets')