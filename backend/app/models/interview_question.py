from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


if TYPE_CHECKING:
    from app.models.candidate_profile import CandidateProfile
    from app.models.interview_session import InterviewSession


class InterviewQuestionSet(BaseModel):
    """One generated question set, as issued to a candidate.

    The questions themselves live in `interview_questions`. Keeping the set as
    its own row means an interview can later be linked back to the exact
    questions that were asked, and it gives `/evaluate` something server-owned
    to verify submitted answers against.

    Why this exists: `/evaluate` used to trust the `question` text that the
    browser sent back, so a candidate could submit trivially easy questions
    alongside a canned answer and bank a high score on a session recruiters
    can read. Grading now reads the question text from here instead.
    """

    __tablename__ = "interview_question_sets"

    candidate_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    candidate: Mapped["CandidateProfile"] = relationship(
        back_populates="interview_question_sets",
    )

    questions: Mapped[list["InterviewQuestion"]] = relationship(
        back_populates="question_set",
        cascade="all, delete-orphan",
        order_by="InterviewQuestion.position",
    )

    sessions: Mapped[list["InterviewSession"]] = relationship(
        back_populates="question_set",
    )


class InterviewQuestion(BaseModel):
    """A single question inside an `InterviewQuestionSet`.

    The row UUID is what the API returns as the question `id` and what
    `/evaluate` expects back, so the submitted id *is* the storage key. A
    client cannot invent a question: anything not in this table is rejected.
    """

    __tablename__ = "interview_questions"

    question_set_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_question_sets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Position within the set, so the order shown to the candidate is preserved.
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="technical",
    )

    target_skill: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        default="",
    )

    keywords: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    question_set: Mapped["InterviewQuestionSet"] = relationship(
        back_populates="questions",
    )