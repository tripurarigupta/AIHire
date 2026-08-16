from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.resume import Resume
    from app.models.application import Application


class CandidateProfile(BaseModel):
    __tablename__ = "candidate_profiles"

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    education: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    experience: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="candidate_profile",
    )

    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
    )

    applications: Mapped[list["Application"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
    )