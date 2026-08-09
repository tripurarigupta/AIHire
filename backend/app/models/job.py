from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


if TYPE_CHECKING:
    from app.models.recruiter_profile import RecruiterProfile
    from app.models.application import Application


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

    location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    employment_type: Mapped[str | None] = mapped_column(
        String(50),
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
    
    applications: Mapped[list["Application"]] = relationship(
    back_populates="job",
    cascade="all, delete-orphan",
    )