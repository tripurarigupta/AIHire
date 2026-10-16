from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


if TYPE_CHECKING:
    from app.models.candidate_profile import CandidateProfile
    from app.models.job import Job


class Recommendation(BaseModel):
    __tablename__ = "recommendations"

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

    match_percentage: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    missing_skills: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    candidate: Mapped["CandidateProfile"] = relationship(
        back_populates="recommendations",
    )

    job: Mapped["Job"] = relationship(
        back_populates="recommendations",
    )
