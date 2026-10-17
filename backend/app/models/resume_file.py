from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, LargeBinary, String
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


if TYPE_CHECKING:
    from app.models.resume import Resume


class ResumeFile(BaseModel):
    """The uploaded resume file itself, stored in the database.

    Why the bytes live in Postgres rather than on disk: the API is deployed as a
    Vercel Function, whose filesystem is read-only (only /tmp is writable) and is
    discarded between invocations. A resume written to disk therefore either
    fails outright or disappears before the recruiter downloads it. Keeping the
    bytes in the database makes upload and download behave identically in local
    development and in production, with no object-storage bucket to configure.

    This is a separate table rather than a column on `resumes` so that listing a
    candidate's resumes never drags multi-megabyte blobs into memory.
    """

    __tablename__ = "resume_files"

    resume_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    content_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    data: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
    )

    resume: Mapped["Resume"] = relationship(
        back_populates="file",
    )
