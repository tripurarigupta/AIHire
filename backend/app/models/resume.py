from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


if TYPE_CHECKING:
    from app.models.candidate_profile import CandidateProfile
    from app.models.resume_file import ResumeFile


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

    # Path on disk. Only populated for resumes uploaded before the bytes moved
    # into the database; new rows store the file in `resume_files` and leave
    # this NULL, so the filesystem is never a hard dependency.
    file_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    extracted_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    parsed_skills: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    ats_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # Alias for backward compatibility — maps to created_at from BaseModel
    @property
    def uploaded_at(self):
        return self.created_at

    candidate: Mapped["CandidateProfile"] = relationship(
        back_populates="resumes",
    )

    file: Mapped["ResumeFile | None"] = relationship(
        back_populates="resume",
        uselist=False,
        cascade="all, delete-orphan",
    )