from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.models.application_status import ApplicationStatus


if TYPE_CHECKING:
    from app.models.candidate_profile import CandidateProfile
    from app.models.job import Job


class Application(BaseModel):
    __tablename__ = "applications"

    candidate_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    job_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[ApplicationStatus] = mapped_column(
        String(50),
        nullable=False,
        default=ApplicationStatus.APPLIED,
    )

    cover_letter: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    ats_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        default=0.0,
    )

    @property
    def applied_at(self) -> datetime:
        return self.created_at

    candidate: Mapped["CandidateProfile"] = relationship(
        back_populates="applications",
    )

    job: Mapped["Job"] = relationship(
        back_populates="applications",
    )

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "job_id",
            name="uq_candidate_job_application",
        ),
    )