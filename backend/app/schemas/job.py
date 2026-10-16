from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: str | None = None
    experience_required: str | None = None
    location: str | None = None
    salary: str | None = None
    job_type: str | None = None
    deadline: datetime | None = None


class JobUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    required_skills: str | None = None
    experience_required: str | None = None
    location: str | None = None
    salary: str | None = None
    job_type: str | None = None
    deadline: datetime | None = None


class JobResponse(BaseModel):
    id: UUID
    title: str
    description: str
    required_skills: str | None = None
    experience_required: str | None = None
    location: str | None = None
    salary: str | None = None
    job_type: str | None = None
    deadline: datetime | None = None
    is_active: bool
    created_at: datetime | None = None
    company_name: str | None = None

    model_config = {
        "from_attributes": True,
    }