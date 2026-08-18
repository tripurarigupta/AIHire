from uuid import UUID

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