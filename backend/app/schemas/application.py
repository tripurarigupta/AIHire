from uuid import UUID
from enum import Enum

from pydantic import BaseModel

class ApplicationCreate(BaseModel):
    cover_letter: str | None = None


class ApplicationResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    job_id: UUID
    status: str
    cover_letter: str | None

    model_config = {
        "from_attributes": True,
    }
    
class RecruiterApplicationResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    job_id: UUID
    status: str
    cover_letter: str | None

    model_config = {
        "from_attributes": True,
    }
    
class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    SELECTED = "selected"
    REJECTED = "rejected"

class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    

class JobSummary(BaseModel):
    id: UUID
    title: str

    model_config = {
        "from_attributes": True,
    }

class CandidateApplicationResponse(BaseModel):
    id: UUID
    status: str
    job: JobSummary
    
    model_config = {
        "from_attributes": True,
    }