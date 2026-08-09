from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


if TYPE_CHECKING:
    from app.models.candidate_profile import CandidateProfile


class Resume(BaseModel):
    __tablename__ = "resumes"

    candidate_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    parsed_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    candidate: Mapped["CandidateProfile"] = relationship(
        back_populates="resumes",
    )