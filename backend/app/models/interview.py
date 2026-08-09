from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


if TYPE_CHECKING:
    from app.models.application import Application


class Interview(BaseModel):
    __tablename__ = "interviews"

    application_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="scheduled",
    )

    interview_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ai",
    )

    application: Mapped["Application"] = relationship(
        back_populates="interview",
    )