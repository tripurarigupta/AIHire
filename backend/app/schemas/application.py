from uuid import UUID
from datetime import datetime

from pydantic import BaseModel
from typing import Optional

from app.models.application_status import ApplicationStatus


class ApplicationCreate(BaseModel):
    cover_letter: str | None = None


class ApplicationResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    job_id: UUID
    status: ApplicationStatus
    cover_letter: str | None = None
    applied_at: datetime | None = None

    model_config = {
        "from_attributes": True,
    }


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationBulkStatusUpdate(BaseModel):
    application_ids: list[UUID]
    status: ApplicationStatus


class JobSummary(BaseModel):
    id: UUID
    title: str
    location: str | None = None
    salary: str | None = None
    company_name: str | None = None

    model_config = {
        "from_attributes": True,
    }


class RecruiterApplicationResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    job_id: UUID
    status: ApplicationStatus
    cover_letter: str | None = None
    ats_score: Optional[float] = None
    applied_at: Optional[datetime] = None
    job: Optional[JobSummary] = None
    candidate_name: Optional[str] = "N/A"
    candidate_email: Optional[str] = None

    model_config = {
        "from_attributes": True,
    }


class CandidateApplicationResponse(BaseModel):
    id: UUID
    job_id: UUID
    status: ApplicationStatus
    ats_score: float | None = 0.0
    job: JobSummary

    model_config = {
        "from_attributes": True,
    }


class ApplicationDetailsResponse(BaseModel):
    """The only candidate data that may cross the application boundary.

    A recruiter receives these fields exclusively for candidates who applied
    to one of their own jobs. The candidate's own profile endpoints stay
    private to the candidate, and no recruiter can read another recruiter's
    data through this schema.
    """

    application_id: str
    status: ApplicationStatus
    ats_score: Optional[float] = None
    cover_letter: str | None = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    education: str | None = None
    skills: str | None = None
    experience: str | None = None
    resume_id: Optional[str] = None
    resume_file_name: Optional[str] = None
    interview_score: Optional[float] = None