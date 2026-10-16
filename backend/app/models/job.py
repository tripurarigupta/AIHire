from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


if TYPE_CHECKING:
    from app.models.recruiter_profile import RecruiterProfile
    from app.models.application import Application
    from app.models.interview_session import InterviewSession
    from app.models.recommendation import Recommendation


class Job(BaseModel):
    __tablename__ = "jobs"

    recruiter_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recruiter_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    required_skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    experience_required: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    salary: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    job_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    recruiter: Mapped["RecruiterProfile"] = relationship(
        back_populates="jobs",
    )

    @property
    def company_name(self) -> str | None:
        return self.recruiter.company_name if self.recruiter is not None else None

    applications: Mapped[list["Application"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )

    interview_sessions: Mapped[list["InterviewSession"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )