from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


if TYPE_CHECKING:
    from app.models.candidate_profile import CandidateProfile
    from app.models.interview_question import InterviewQuestionSet
    from app.models.job import Job


class InterviewSession(BaseModel):
    __tablename__ = "interview_sessions"

    candidate_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Nullable: general practice interviews can be taken without picking a job.
    job_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=True,
    )

    # The exact questions this session was graded against. Nullable so sessions
    # recorded before this table existed still load.
    question_set_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_question_sets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    overall_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    feedback: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    strengths: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    improvements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    candidate: Mapped["CandidateProfile"] = relationship(
        back_populates="interview_sessions",
    )

    job: Mapped["Job"] = relationship(
        back_populates="interview_sessions",
    )

    question_set: Mapped["InterviewQuestionSet | None"] = relationship(
        back_populates="sessions",
    )
