from uuid import UUID
from pydantic import BaseModel

class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: str | None = None
    location: str | None = None
    employment_type: str | None = None


class JobResponse(BaseModel):
    id: UUID
    recruiter_id: UUID
    title: str
    description: str
    required_skills: str | None
    location: str | None
    employment_type: str | None
    is_active: bool

    model_config = {
        "from_attributes": True,
    }